from tempfile import NamedTemporaryFile
import gzip
import os
import zipfile


def expand_file(filename=None, fileobj=None, zip_protocol=None,
                output='stream'):
    """Expand the contents of the compressed fileobj

    :param filename: Full system path to file containing the
      compressed content.  Either fileobj OR filename should have a
      value.

    :param fileobj: A file like object containing the compressed
      content.  Either fileobj OR filename should have a value

    :param zip_protocol: The zip protocol used, 'zip' or 'gzip'

    :param output: Desired return type, accepts 'file' or 'stream' 
    
    Returns a cStringIO containing expanded contents, or the full path
    to the file, depending on 'output' parameter.  NB: caller's
    responsiblity to clean up / delete returned file. 

    """
    if output not in ('file', 'stream'):  #pragma: no cover
        raise ValueError("output types accepted: {file|stream}")
    if zip_protocol not in ('gzip', 'zip'):  #pragma: no cover
        raise ValueError("zip_protocol types accepted: {gzip|zip}")
    if filename and fileobj:  # pragma: no cover
        raise ValueError("Only one of filename or fileobj should have "\
                         "a value")

    def gzip_expand(filename, fileobj):
        if not fileobj:
            fileobj = open(filename, 'rb')
        return gzip.GzipFile(fileobj=fileobj, mode='rb')

    def zip_expand(filename, fileobj):
        tmpfile = None
        if fileobj:
            with NamedTemporaryFile(suffix='.zip', delete=False,
                                    mode='wb') as tmpfile:
                tmpfile.write(fileobj.read())
            filename = tmpfile.name

        with zipfile.ZipFile(filename, 'r') as zfile:
            filelist = zfile.namelist()
            if len(filelist) != 1:  # pragma: no cover
                raise ValueError("Only expecting single file in archive")
            content = zfile.open(filelist[0])
        if tmpfile:
            os.remove(tmpfile.name)
        return content

    def desired_output(content, output):
        if output == 'file':
            with NamedTemporaryFile(delete=False, mode='wb') as outfile:
                outfile.write(content.read())
            return outfile.name
        else:
            return content

    expander = gzip_expand if zip_protocol == 'gzip' else zip_expand
    return desired_output(expander(filename, fileobj), output)


def zip_file(filename, fileobj, zip_protocol):
    """Zip the file using the requested protocol

    :param filename: zip filepath to generate on filesystem

    :param fileobj: file like object with contents to be compresed

    :param zip_protocol: The zip protocol to use, 'zip' or 'gzip'

    Given a file like object, zip the contents, save to a file and
    return the path to the zipped file
    
    """
    if zip_protocol == 'gzip':
        if not filename.endswith('.gz'):
            filename += '.gz'
        fh = gzip.open(filename, 'wb')
        fh.write(fileobj.read())
        fh.close()
        return filename
    if zip_protocol == 'zip':
        if not filename.endswith('.zip'):
            filename += '.zip'
        with zipfile.ZipFile(filename, 'w') as zfile:
            # crop off the .zip from the filename
            zfile.writestr(filename[:-4],fileobj.read())
        return filename
    else:  # pragma: no cover
        raise ValueError("can't handle requesed zip protocol: %s" %\
            zip_protocol)
