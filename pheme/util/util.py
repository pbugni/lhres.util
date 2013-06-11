from datetime import datetime
from datetime import date
import glob
import logging
from socket import gethostname
import os
import subprocess

from pheme.util.config import Config
import ConfigParser

def inProduction():
    """Simple state check to avoid uploading files to thrid party
    servers and what not when not 'in production'.
    """
    config = Config()
    try:
        return config.get('general', 'in_production')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):  # pragma: no cover
        raise ValueError("Config file doesn't specify "
                         "`[general]in_production` "
                         "unsafe to guess, can't continue")


def systemUnderLoad():  # pragma: no cover
    """Method to determine if the system appears to be under a heavy load
    at the moment.  This is used typically by cron jobs before firing
    to prevent starvation.

    """
    # getloadavg returns the number of processes in the system run
    # queue averaged over the last 1, 5, and 15 minutes or raises
    # OSError if the load average was unobtainable
    try:
        lastMinLoadAvg = os.getloadavg()[0]
        if lastMinLoadAvg < 2.0:
            return False
        else:
            logging.info("System under load: %f" % lastMinLoadAvg)
            return True
    except:
        logging.error("System load unattainable - assuming loaded")
        return True


def getYearDiff(start_datetime, end_datetime=date.today()):
    """Get the number of years from start_datetime to
    end_datetime, defaulting to today for the end_datetime.

    Returns an int.
    """
    year_delta = end_datetime - start_datetime
    raw_years = year_delta.days / 365

    return raw_years


def getDobDatetime(raw_dob):
    """Dates of birth only include month and year.
    Create a datetime assuming the fifteenth of the month
    for these dates.

    :param raw_dob: date of birth to convert, as YYYYMM or YYYY,MM

    Returns a datetime

    """
    if not raw_dob:
        return

    if type(raw_dob) == type(6):
        year = raw_dob / 100
        month = raw_dob % 100
    elif ',' in raw_dob:
        #Handle the format YYYY,MM
        year, month = raw_dob.split(',')
    else:
        #Handle the format YYYYMM
        year = raw_dob[:4]
        month = raw_dob[-2:]
    return datetime(int(year), int(month), 15)


def _intCast(s):
    """Make int cast a callable for use in map. """
    return int(s)


def parseDate(d):
    """Parse and return a datatime.date object from the string passed in.
    Only date formats supported are YYYYMMDD or YYYY-MM-DD.  If a date
    can not be created, a ValueError exception is raised w/ the details.
    """
    msg = "Couldn't create a date from '%s'" % (d)
    try:
        if d.find('-') > 0:
            (y, m, d) = d.split('-')
        else:
            (y, m, d) = (d[:4], d[4:6], d[6:])
        return date(*map(_intCast, (y, m, d)))
    except ValueError, e:
        raise ValueError(msg + "\n->  " + e.__str__())


def stringFields(fields):
    """ Null and int safe function to convert a list of fields into a
    stringified verson, joined w/ ':'.  This is typically used by
    methods to generate a comparable string for a complex object using
    a restricted list of fields.

    :param fields: a list or tuple of fields to join on.  str() will be
                   used on valid (non null) values to handle integer
                   and other non string types

    returns a single string representing the fields

    """

    return ":".join([str(f) for f in fields if f])


def strict_execute(cmd, ignore_stderr_alone=False):
    """This wraps a cmd, executes it.  If any problems are found, log as
    error before raising the exception.

    :param cmd: string version of cmd to execute, just as it'd be used
                at the shell.
    :param ignore_stderr_alone: typically any noise on stderr is
                treated as an exception.  With this value set, use the
                retval to define success.  Useful for programs like
                curl that write stats to stderr. 

    returns stdout if there was any
    """
    logging.debug('Launch cmd: %s', cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    out, err = process.communicate()
    retval = process.returncode
    if not ignore_stderr_alone and err or retval:
        logging.error("cmd '%s' generated unexpected retval '%s' or "\
                      "output '%s'", cmd, retval, err)
        raise ValueError("Failed execution of '%s'" % cmd)
    logging.debug('Successful execution of cmd: %s', cmd)
    return out


def none_safe_min(x, y):
    """returns the min value, even if x or y is None

    The stdlib version of min (at least for some datatypes) raises a
    TypeError when asked to compare with a NoneType.  If only one of
    the values is defined, return that as the min.  If both are
    defined, return the stdlib min result.  If both are None, return
    None.

    """
    if x is None and y is None:
        return None
    if x is None:
        return y
    if y is None:
        return x
    return min(x, y)


def none_safe_max(x, y):
    """returns the max value, even if x or y is None

    The stdlib version of max (at least for some datatypes) raises a
    TypeError when asked to compare with a NoneType.  If only one of
    the values is defined, return that as the max.  If both are
    defined, return the stdlib max result.  If both are None, return
    None.

    """
    if x is None and y is None:
        return None
    if x is None:
        return y
    if y is None:
        return x
    return max(x, y)

def next_sequential_file(filename):
    """Returns next available filename ending in a sequential counter

    As an example, if `filename` = '/tmp/foo' and '/tmp/foo.1' and
    '/tmp/foo.2' already exist, '/tmp/foo.3' will be returned.

    :param filename: Path and filename to consider.  If there is no
                     file found with this name, it is simply returned.
                     If there is an existing file by this name, a
                     directory search is used to find the next
                     available sequential extension

    """
    if not os.path.exists(filename):
        return filename
    
    basename = os.path.basename(filename)
    dirname = os.path.dirname(filename)

    existing = glob.glob(filename + '.*')
    values = []
    for x in existing:
        xbase = os.path.basename(x)
        suffix = xbase[len(basename) + 1:]  # +1 for the '.'
        try:
            values.append(int(suffix))
        except ValueError:
            pass  # don't care, a non sequential index, won't get in
                  # the way
    if not len(values):
        suffix = 1
    else:
        values.sort()
        suffix = values[-1] + 1
    return os.path.join(dirname, basename + '.' + str(suffix))
