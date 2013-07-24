#!/usr/bin/env python
""" Unit tests for the datefile module.

"""

from datetime import datetime
import os
import unittest

from pheme.util.datefile import Datefile


class DatefileTest(unittest.TestCase):

    def setUp(self):
        self.persistence_file = '/tmp/datefiletest'

    def tearDown(self):
        if os.path.exists(self.persistence_file):
            os.remove(self.persistence_file)

    def testNoDirection(self):
        df = Datefile(datetime.now())
        self.assert_(df.get_date(), "Even w/o direction, should get "
                     "initial date back")
        datebefore = df.get_date()
        df.bump_date()
        dateafter = df.get_date()
        self.assertEquals(datebefore, dateafter)

    def testForwards(self):
        df = Datefile(datetime.strptime('2009-01-01', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='forwards')
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2009-01-01')
        df.bump_date()
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2009-01-02')

    def testBackwards(self):
        df = Datefile(datetime.strptime('2009-01-01', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='backwards')
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2009-01-01')
        df.bump_date()
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2008-12-31')

    def testStep(self):
        df = Datefile(datetime.strptime('2009-01-01', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='backwards', step=10)
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2009-01-01')
        df.bump_date()
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2008-12-22')

    def testStepDatesFwd(self):
        "steping forward, end date should be step-1 days after start"
        df = Datefile(datetime.strptime('2009-02-01', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='forwards', step=10)
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2009-02-01')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2009-02-10')

    def testStepDatesBack(self):
        "steping backward, end date should be step-1 days before start"
        df = Datefile(datetime.strptime('2009-01-31', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='backwards', step=10)
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2009-01-22')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2009-01-31')

    def testStepDatesBackThrice(self):
        "steping backward three times, duplication avoided?"
        df = Datefile(datetime.strptime('2011-04-30', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='backwards', step=10)
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2011-04-21')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2011-04-30')
        df.bump_date()
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2011-04-11')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2011-04-20')
        df.bump_date()
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2011-04-01')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2011-04-10')

    def testRangeSansStep(self):
        "range w/o step"
        df = Datefile(datetime.strptime('2009-10-31', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='forwards')
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2009-10-31')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2009-10-31')

    def testRangeStepSansDirection(self):
        "give step and no directon"
        df = Datefile(datetime.strptime('2009-10-31', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      step=30)
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2009-10-02')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2009-10-31')

    def testRangeSansFile(self):
        "range w/o step"
        df = Datefile(datetime.strptime('2009-10-31', '%Y-%m-%d'))
        start, end = df.get_date_range()
        self.assertEquals(start.strftime('%Y-%m-%d'),
                          '2009-10-31')
        self.assertEquals(end.strftime('%Y-%m-%d'),
                          '2009-10-31')

    def testInitialDate(self):
        # write a date to the file, then call with a different initial
        # date.  should get the date from the file.
        with open(self.persistence_file, 'w') as p_file:
            p_file.write('2009-06-06')

        df = Datefile(datetime.strptime('2009-01-01', '%Y-%m-%d'),
                      persistence_file=self.persistence_file,
                      direction='backwards')
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2009-06-06')
        df.bump_date()
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2009-06-05')

    def testDefaultAccess(self):
        df = Datefile(initial_date=
                      datetime.strptime('2009-01-01', '%Y-%m-%d'))
        self.assertEquals(df.get_date().strftime('%Y-%m-%d'),
                          '2009-01-01')


if '__main__' == __name__:  # pragma: no cover
    unittest.main()
