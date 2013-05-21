from cStringIO import StringIO
import gzip
import os
import unittest
from tempfile import NamedTemporaryFile

from lhres.util.compression import expand_file, zip_file


class TestFile(unittest.TestCase):
    """Manages creation and clean up of a test file"""
    def setUp(self):
        super(TestFile, self).setUp()
        self.test_text = "A few simple words"

    def tearDown(self):
        super(TestFile, self).tearDown()
        if hasattr(self, 'tempfile'):
            os.remove(self.tempfile.name)

    def create_test_file(self, compression=None):
        """Helper to generate a temporary file to save

        Returns the filename, potenially pointing to a file containing
        the content of self.text and compressed as requested.

        NB File will need to be opened to use.

        """
        # In case tests loop over file used - clean as we go
        if hasattr(self, 'tempfile'):  # pragma: no cover
            os.remove(self.tempfile.name)
            del self.tempfile

        # Generate a safe filename - deletion is tearDown's job
        if compression is None:
            self.tempfile = NamedTemporaryFile(prefix='unittest',
                                               delete=False) 
            self.tempfile.write(self.test_text)
            self.tempfile.close()
        elif compression == 'gzip':
            self.tempfile = NamedTemporaryFile(prefix='unittest',
                                               suffix='.gz',
                                               delete=False) 
            self.tempfile.close()
            fh = gzip.open(self.tempfile.name, 'wb')
            fh.write(self.test_text)
            fh.close()
        elif compression == 'zip':
            self.tempfile = NamedTemporaryFile(prefix='unittest',
                                               suffix='.zip',
                                               delete=False)
            self.tempfile.close()
            os.remove(self.tempfile.name)
            content = StringIO(self.test_text)
            self.tempfile.name = zip_file(self.tempfile.name, content,
                                          compression)
        else:  # pragma: no cover
            raise ValueError("Can't handle compression '%s'",
                             compression)
        return self.tempfile.name


class ZipTests(TestFile):
    """Test the zip & expand compression functions"""
    def setUp(self):
        super(ZipTests, self).setUp()

    def tearDown(self):
        super(ZipTests, self).tearDown()

    def test_zip(self):
        filename = self.create_test_file(compression=None)
        result = zip_file(filename, open(filename, 'rb'), 'zip')
        # hand verified the contents were zipped and matched...
        self.assertTrue(os.path.exists(result))

    def test_gzip(self):
        filename = self.create_test_file(compression=None)
        result = zip_file(filename, open(filename, 'rb'), 'gzip')
        f = gzip.GzipFile(mode='rb', fileobj=open(result, 'rb'))
        self.assertEqual(f.read(), self.test_text)

    def test_gunzip_stream(self):
        compressed = self.create_test_file(compression='gzip')
        expanded = expand_file(fileobj=open(compressed, 'rb'),
                               zip_protocol='gzip')
        self.assertEqual(expanded.read(), self.test_text)

    def test_gunzip_file(self):
        compressed = self.create_test_file(compression='gzip')
        expanded = expand_file(filename=compressed, zip_protocol='gzip')
        self.assertEqual(expanded.read(), self.test_text)

    def test_gunzip_file_to_file(self):
        compressed = self.create_test_file(compression='gzip')
        expanded = expand_file(filename=compressed, zip_protocol='gzip',
                               output='file')
        with open(expanded, 'rb') as result:
            self.assertEqual(result.read(), self.test_text)

    def test_unzip_stream(self):
        compressed = self.create_test_file(compression='zip')
        expanded = expand_file(fileobj=open(compressed, 'rb'),
                               zip_protocol='zip')
        self.assertEqual(expanded.read(), self.test_text)

    def test_unzip_file(self):
        compressed = self.create_test_file(compression='zip')
        expanded = expand_file(filename=compressed,
                               zip_protocol='zip')
        self.assertEqual(expanded.read(), self.test_text)

    def test_unzip_file_to_file(self):
        compressed = self.create_test_file(compression='zip')
        expanded = expand_file(filename=compressed,
                               zip_protocol='zip',
                               output='file')
        with open(expanded, 'rb') as result:
            self.assertEqual(result.read(), self.test_text)
