""" Module for formatting, encoding and decoding utility methods """
from datetime import datetime
import re

isoformat_pattern = re.compile('\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d*')


def decode_isofomat_datetime(dict_to_decode):
    """JSON doesn't handle datetime.  Convert string in isoformat()

    :param dict_to_decode: dictionary potentially containing values
      matching the isoformat_pattern.  Nested dictionaries supported.

    Note recursion use as a search dictionary may include nested
    dictionaries, i.e. a client may have encoded:
      {'start_time': {'$gt', start_time.isoformat()}}

    returns the dictionary given with any strings matching the
    isoformat_pattern converted into datetime instances.

    """
    for k, v in dict_to_decode.items():
        if isinstance(v, dict):
            dict_to_decode[k] = decode_isofomat_datetime(v)
        elif isinstance(v, basestring) and isoformat_pattern.search(v):
            try:
                dict_to_decode[k] =\
                    datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:  # pragma no cover
                # Couldn't convert, assume the pattern match failed
                pass
    return dict_to_decode
