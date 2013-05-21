from datetime import datetime, date

from lhres.util.util import inProduction, getYearDiff, getDobDatetime
from lhres.util.util import parseDate, stringFields
from lhres.util.util import none_safe_min, none_safe_max

def test_inProcution():
    """testing - shouldn't be inProduction!"""
    assert(inProduction() == False)

def test_getYearDiff():
    start = datetime(2001, 1, 1)
    # less than a year should return 0
    assert(getYearDiff(start, datetime(2001, 9, 1)) == 0)

    assert(getYearDiff(start, datetime(2002, 1, 1)) == 1)
    assert(getYearDiff(start, datetime(2006, 3, 2)) == 5)

def test_getDobDatetime():
    expected = {'200101': datetime(2001, 1, 15),
                '2001,01': datetime(2001, 1, 15),
                '199403': datetime(1994, 3, 15),
                '1994,03': datetime(1994, 3, 15),
                199403: datetime(1994, 3, 15),
                200101: datetime(2001, 1, 15),
                '': None,
                }

    for dob, wanted in expected.items():
        assert(getDobDatetime(dob) == wanted)

def test_parseDate():
    assert(parseDate('20090131') == date(2009, 1, 31))
    assert(parseDate('2009-01-31') == date(2009, 1, 31))
    try:
        parseDate('20093101')
    except ValueError:
        pass  # desired as month & day are inverted
    else:  # pragma: no cover
        assert(not "inverted month & day should raise")

def test_stringFields():
    assert('' == stringFields((None,)))
    assert('1:2:3:four' == stringFields((1,2,None,3,"four")))


def test_none_safe_min_max():
    none_safe_min(None, None)
    none_safe_max(None, None)
    now = datetime.now()
    assert(now == none_safe_min(None, now))
    assert(now == none_safe_min(now, None))
    assert(now == none_safe_max(None, now))
    assert(now == none_safe_max(now, None))
