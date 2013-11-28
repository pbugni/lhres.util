from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import getpass
import psycopg2
import os
import shlex
import subprocess

from pheme.util.config import Config


def db_params(section):
    """Return dict of database connection values from named config section

    Returned dict includes:
    - user
    - password
    - database  (name of database)

    """
    config = Config()
    database = config.get(section, 'database')
    user = config.get(section, 'database_user')
    password = config.get(section, 'database_password')
    return {'user': user, 'password': password, 'database': database}


def db_connection(section):
    """Return active database connection (a la SQLAlchemy) for use

    Uses values found in named section of the config file
    for database, username, etc.

    :param section: block of config file to use for connection details

    NB caller responsible for calling disconnect() on the returned handle.

    """
    return AlchemyAccess(**db_params(section))


def _getPgUser():
    """ Returns best guess for postgres (user,password)

    If the postgres ENV vars PGUSER, PGPASSWORD are defined, return
    them.  Otherwise, raise an exception

    """
    if 'PGUSER' in os.environ:
        return (os.environ['PGUSER'], os.environ['PGPASSWORD'])

    raise RuntimeError("Set enviornment variable 'PGUSER' to preferred "
                       "PostgreSQL user, and 'PGPASSWORD' accordingly")


class AlchemyAccess(object):
    """ Access to the named database using the SQLAlchemy interface.

    """

    def __init__(self, database='', host='localhost', port=5432,
                 user=None, password=None, verbosity=0):
        self.dbName = database
        self.dbHost = host
        self.dbPort = port
        self.dbUser = user
        self.dbPass = password
        self.verbosity = verbosity
        if not self.dbUser:
            (self.dbUser, self.dbPass) = _getPgUser()
        self._connect()

    def _getUrl(self):
        """ Return the URL used to connect to the database """
        return "postgresql://%(user)s:%(password)s@%(host)s:"\
            "%(port)d/%(database)s" % \
            {'user': self.dbUser,
             'password': self.dbPass,
             'host': self.dbHost,
             'port': self.dbPort,
             'database': self.dbName}

    def _connect(self):
        """ Connect to the database.
        """
        # Set up logging, eliminates the deprecation warning
        import logging
        logging.getLogger('sqlalchemy.orm.unitofwork').setLevel(logging.DEBUG)

        # To view all queries on stdout with their variable data, add
        # "echo=True" to this create_engine call
        self.engine = create_engine(self._getUrl(),
                                    use_native_unicode=False, echo=False)
        Session = sessionmaker(bind=self.engine,
                               autoflush=False)
        self.session = Session()

    def disconnect(self):
        """ Disconnect from the database.
        """
        if hasattr(self, 'session'):
            self.session.close()
            del self.session  # enable the check in __del__
            self.engine.dispose()

    def __del__(self):
        """ __del__ isn't guaranteed to be called, but we'll use it to
        notify users when they didn't clean up after themselves."""
        if hasattr(self, 'session'):
            print 'ERROR: DestDB still has '\
                'an open session; be sure to call '\
                '_disconnect()'


class DirectAccess(object):
    """ For the occasion (outside the norm of using SQLAlchemy or
    feeding SQL files directly to the database) where direct SQL
    access is needed, this class provides rudimentary access to run
    queries, etc.
    """

    def __init__(self, database, host='localhost', port=5432,
                 user=None, password=None):
        """ If the database user and password aren't supplied, we'll
        use the current user and attempt to get a password as
        implemented in pg_access._getPgUser()
        """
        self.dbHost = host
        self.dbName = database
        self.dbPort = port
        self.dbUser = user
        self.dbPass = password
        if not self.dbUser:
            (self.dbUser, self.dbPass) = _getPgUser()

    def raw_query(self, query):
        """ Typically we use sqlalchemy - this is for the exceptional
        case where a low level query is needed in a test (say when
        sqlalchemy doesn't support the feature, like a view).
        """
        cursor = self._cursor()
        cursor.execute(query)
        return cursor

    def commit(self):
        """ After inserts/updates, user needs to commit the
        transaction"""
        self.psyco_conn.commit()

    def close(self):
        """ Close any open connections or cursors from this instance.
        """
        self._disconn()

    def _cursor(self):
        """ Get a lowlevel (psycopg2) cursor for the database.
        Typically we use sqlalchemy, but some tests require direct
        access.
        """
        if hasattr(self, 'psyco_cursor'):
            return self.psyco_cursor

        # First time - retain connection and cursor for cleanup later
        self.psyco_conn = psycopg2.connect(database=self.dbName,
                                           host=self.dbHost,
                                           port=self.dbPort,
                                           user=self.dbUser,
                                           password=self.dbPass)
        self.psyco_cursor = self.psyco_conn.cursor()
        return self.psyco_cursor

    def _disconn(self):
        """ Disconnect from the psycopg2 connection.
        """
        if hasattr(self, 'psyco_cursor'):
            self.psyco_cursor.close()
            del(self.psyco_cursor)
        if hasattr(self, 'psyco_conn'):
            self.psyco_conn.close()
            del(self.psyco_conn)

    def __del__(self):
        """ __del__ isn't guaranteed to be called, but we'll use it to
        raise cane when it doesn't look like the user cleaned up the
        connection """
        if hasattr(self, 'psyco_conn'):
            print 'ERROR: DbLayer still has '\
                'an open psyco connection; be sure to '\
                'call tearDown()'


class FilesystemPersistence(object):
    """Backup and restore database images using filesystem files"""

    def __init__(self, database, user, password, host='localhost'):
        self.database_name = database
        self.database_user = user
        self.database_password = password
        self.database_host = host

    def _need_sudo(self):
        """Return sudo prefix when necessary depending on user"""
        if getpass.getuser() == self.database_user:
            return ''
        return 'sudo -u %s ' % self.database_user

    sudo_prefix = property(_need_sudo)

    def persist(self):
        write_to_file = shlex.split("pg_dump %s" % self.database_name)
        with open(self._persistent_filename(), 'w') as target_file:
            subprocess.Popen(write_to_file, env=self.db_enviornment,
                             stdout=target_file).wait()

    def restore(self):
        delete_old = shlex.split(self.sudo_prefix + "dropdb %s" %
                                 self.database_name)
        subprocess.Popen(delete_old, env=self.db_enviornment).wait()
        recreate = shlex.split(self.sudo_prefix + "createdb %s" %
                               self.database_name)
        subprocess.Popen(recreate, env=self.db_enviornment).wait()

        copy_data = shlex.split(self.sudo_prefix + "psql %s -f %s" %
                                (self.database_name,
                                 self._persistent_filename()))
        with open(os.devnull, 'w') as dev_null:
            subprocess.Popen(copy_data, env=self.db_enviornment,
                             stdout=dev_null).wait()

    def _get_db_enviornment(self):
        """Return dictionary of environment setting for db auth"""
        return {'PGUSER': self.database_user,
                'PGPASSWORD': self.database_password,
                'PGHOST': self.database_host}

    db_enviornment = property(_get_db_enviornment)

    def _persistent_filename(self):
        """Returns the full path and name of filesystem file"""
        base = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         "../../var"))
        return os.path.join(base, '%s.sql' % self.database_name)
