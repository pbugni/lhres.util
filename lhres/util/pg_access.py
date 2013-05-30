from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import getpass
import psycopg2
import os, sys

def _getPgUser():
    """ Returns best guess for postgres (user,password)

    If the postgres ENV vars PGUSER, PGPASSWORD are defined, return
    them.  Otherwise, raise an exception

    """
    if 'PGUSER' in os.environ:
        return (os.environ['PGUSER'], os.environ['PGPASSWORD'])

    raise RuntimeError("Set enviornment variable 'PGUSER' to preferred "\
                           "PostgreSQL user, and 'PGPASSWORD' accordingly")


class AlchemyAccess(object):
    """ Access to the named database using the SQLAlchemy interface.

    """

    def __init__(self, database, host='localhost', port=5432,
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
            {'user':self.dbUser,
             'password':self.dbPass,
             'host':self.dbHost,
             'port':self.dbPort,
             'database':self.dbName}

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
