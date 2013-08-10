import ConfigParser
import logging
import os
import re

# Configuration files are processed in order.  Last value found
# takes precidence
CONFIG_FILES = ('pheme.conf',
                '/etc/pheme/pheme.conf',
                os.path.expanduser('~/.pheme.conf'))


class Config(object):
    """Exposes values from project configuration files

    Values found are converted to native types, when obvious, such as
    floating point (float), integers (int), and boolean.  NB, 0 and 1
    are seen as integers, not boolean values.

    """

    def __init__(self, config_files=CONFIG_FILES):
        """Create config parser instance and parse config_files

        :param config_files: optional list of configuration files

        Parses, in order, the config_files.  Last value found for
        any option in a seciont takes precedence.

        """
        self.config_files = config_files
        self.parser = ConfigParser.ConfigParser()
        self.bool_pattern = re.compile("(t)|(f)|(true)|(false)$",
                                       re.IGNORECASE)
        for f in config_files:
            if os.path.exists(f):
                with open(f) as cf:
                    self.parser.readfp(cf)

    def get(self, section, option, default=None):
        """Return the value of 'option' in 'section' if found

        :param section: the name of the [section] in the configuration
          file
        :param option: the specific option to look for, or key, if you
          will
        :param default: value to return if the option and/or section
          aren't found.  Must have a value to avoid exception for an
          undefined section/option pair.  No coercion performed on
          default values.

        For example, called with (section='DB', option='user') with
        a config file containing::

          [DB]
          user=sample

        The string 'sample' would be returned.

        Attempts to coerce the return type to integer, float or
        boolean if the value matches the obvious patterns, i.e. '373'
        returns an int, '12.6' returns a fload and 'true' returns True

        If the value begins with a tilde `~` an attempt to expand as a
        user's home directory is performed on the value before
        returning to simplify file access.

        """
        try:
            found = self.parser.get(section, option)
            if re.match(r'[-]?\d+$', found):
                found = int(found)
            elif re.match(r'[-]?\d+\.\d+$', found):
                found = float(found)
            elif found.lower().strip() in ('t', 'true'):
                found = True
            elif found.lower().strip() in ('f', 'false'):
                found = False
            elif found.startswith('~'):
                found = os.path.expanduser(found)
        except:
            if default:
                found = default
            else:
                stmt = "'[%s]%s' not in config file(s): "\
                    "{'%s'}" % (section, option,
                                ','.join(self.config_files))
                logging.error(stmt)
                raise RuntimeError(stmt)
        return found


def configure_logging(verbosity=0, logfile='generic.log', append=True):
    """Utility to configure logging for the calling package.

    :param verbosity: used to set the desired level of logging
                      {0:WARNING, 1:INFO, 2:DEBUG}
    :param logfile: should be set to the desired filename in the
                    configured log directory.  value of 'stderr'
                    overrides use of a file - logging will hit stderr.
    :param append: if true (default) the log file will be appended to; if
                   set false the logfile will be reset on execution

    returns the path to the log file

    """
    kwargs = {'format': '%(asctime)s %(message)s',
              'datefmt': '%Y-%m-%d %H:%M:%S', 'filemode': append and
              'a' or 'w'}
    loglevel = logging.WARNING
    if verbosity > 0:
        loglevel = logging.INFO
    if verbosity > 1:
        loglevel = logging.DEBUG
    kwargs['level'] = loglevel

    if logfile != 'stderr':
        try:
            logdir = os.environ['INHS_LOGDIR']
        except KeyError:
            config = Config()
            try:
                logdir = config.get('general', 'log_dir')
            except ConfigParser.NoSectionError:  # pragma: no cover
                raise "Neither env var INHS_LOGDIR nor config "\
                      "[general]log_dir defined - can't continue"
        kwargs['filename'] = os.path.join(logdir, logfile)

    logging.basicConfig(**kwargs)
    return kwargs.get('filename', None)
