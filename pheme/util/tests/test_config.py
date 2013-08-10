import ConfigParser
import os
import unittest

from pheme.util.config import Config, configure_logging


class TestConfig(unittest.TestCase):
    """Tests for the Config class"""

    # Bogus configuration files for test
    config_files = ('bogus.conf',
                    os.path.expanduser('~/bogus.conf'))

    def tearDown(self):
        # make sure we don't leave bogus config files around
        for f in self.config_files:
            try:
                os.remove(f)
            except:
                pass

    def test_absent(self):
        "no config files present shouldn't raise"
        c = Config(self.config_files)
        self.assertTrue(c)

    def test_override(self):
        "same key in second file should override"
        section = 'SECTION'
        key = 'unittest'
        for i in range(2):
            cp = ConfigParser.RawConfigParser()
            cp.add_section(section)
            cp.set(section, key, i)
            with open(self.config_files[i], 'w') as f:
                cp.write(f)
        c = Config(self.config_files)
        self.assertEquals(1, c.get(section, key))

    def test_truthiness(self):
        "truth value should be case insensitive"
        section = 'SECTION'
        key = 'unittest'
        values = ['TRUE', 'true', 'True', ' t ']
        cp = ConfigParser.RawConfigParser()
        cp.add_section(section)
        for i in range(len(values)):
            cp.set(section, key+str(i), values[i])
        with open(self.config_files[0], 'w') as f:
            cp.write(f)
        c = Config(self.config_files)
        for i in range(len(values)):
            self.assertEquals(True, c.get(section, key+str(i)))

    def test_falseness(self):
        "false values should be case insensitive"
        section = 'SECTION'
        key = 'unittest'
        values = ['FALSE', 'false', 'False', ' f ']
        cp = ConfigParser.RawConfigParser()
        cp.add_section(section)
        for i in range(len(values)):
            cp.set(section, key+str(i), values[i])
        with open(self.config_files[0], 'w') as f:
            cp.write(f)
        c = Config(self.config_files)
        for i in range(len(values)):
            self.assertEquals(False, c.get(section, key+str(i)))

    def test_default(self):
        "Asking for missing value with a default"
        c = Config(self.config_files)
        self.assertEquals(42, c.get('Lifes', 'Answer',  42))

    def test_float(self):
        "Looks like a float, should be one"
        section = 'SECTION'
        key = 'unittest'
        values = ['0.01', '42.0', '-67.3']
        cp = ConfigParser.RawConfigParser()
        cp.add_section(section)
        for i in range(len(values)):
            cp.set(section, key+str(i), values[i])
        with open(self.config_files[0], 'w') as f:
            cp.write(f)
        c = Config(self.config_files)
        for i in range(len(values)):
            self.assertEquals(float(values[i]),
                              c.get(section, key+str(i)))

    def test_int(self):
        "Looks like an int, should be one (including 0,1)"
        section = 'SECTION'
        key = 'unittest'
        values = ['0', '1', '-67', 42, -1]
        cp = ConfigParser.RawConfigParser()
        cp.add_section(section)
        for i in range(len(values)):
            cp.set(section, key+str(i), values[i])
        with open(self.config_files[0], 'w') as f:
            cp.write(f)
        c = Config(self.config_files)
        for i in range(len(values)):
            self.assertEquals(int(values[i]),
                              c.get(section, key+str(i)))

    def test_missing(self):
        "Asking for missing value without a default should raise"
        c = Config(self.config_files)
        self.assertRaises(RuntimeError, c.get, 'section', 'value')

    def test_tilde(self):
        "support tilde in directory paths"
        section = 'SECTION'
        key = 'unittest'
        value = "~/tempfile"
        cp = ConfigParser.RawConfigParser()
        cp.add_section(section)
        cp.set(section, key, value)
        with open(self.config_files[0], 'w') as f:
            cp.write(f)
        c = Config(self.config_files)
        self.assertEquals(os.path.expanduser("~/tempfile"),
                          c.get(section, key))


def test_configure_logging():

    logfile = configure_logging(verbosity=2, logfile='unittest.log',
                                append=False)
    # Thanks to nose working so hard to capture logging, it's quit
    # difficult to test - hand verified.
    assert(logfile == os.path.join(Config().get('general', 'log_dir'),
                                   'unittest.log'))


if '__main__' == __name__:  # pragma: no cover
    unittest.main()
