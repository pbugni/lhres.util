from datetime import datetime

from pheme.util.format import decode_isofomat_datetime


def test_isoformat_decode_nothing():
    # should get back dict passed if no isoformats are present
    d = {1: 'one', 'two': 2, 'nested': {'a': 'eh'}, 'tup': (1, 2, 3)}
    e = decode_isofomat_datetime(d)
    assert(d == e)


def test_isoformat_decode_datetime():
    d = {'now': datetime.now()}
    e = decode_isofomat_datetime(d)
    assert(d == e)


def test_isoformat_decode():
    d = {'now': datetime.now().isoformat()}
    e = decode_isofomat_datetime(d)
    assert(d == e)
