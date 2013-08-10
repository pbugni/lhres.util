import os
import logging
from datetime import datetime, timedelta


class Datefile(object):
    """ For clients that are initiated via cron, and need a persistent
    way to move through calendar days on each invocation.

    """

    def __init__(self, initial_date, persistence_file=None,
                 direction=None, step=None):
        """Set up a DateFile instance.

        initial_date - date to initialize with, should there not be
            one found in the named persistence_file

        persistence_file - filepath used to persist the date between
            invocations.  not required unless `direction` is set.

        direction - set to 'forwards' to move forward, or increment the
            date, 'backwards' for the inverse, and None to not persist at
            all.  (Useful in clients that optionally use such a
            feature).

        step - number of days to step - defaults to one.  a value of
            30 would mean increment or decrement by 30 days as per
            direction setting.  w/o direction set, it has no meaning.

        The dates are treated as "inclusive".  As an example, a start
        date of 1/1/2010, and an end date of 1/10/2010 would have a
        step of 10.  Moving forward would give the next pair 1/11/2010
        and 1/20/2010.

        """
        self.initial_date = initial_date
        self.direction = direction
        self.datefile = persistence_file
        self.step = step and step or 1

        if direction:
            valid_directions = ('forwards', 'backwards')
            if direction not in valid_directions:  # pragma: no cover
                raise ValueError('Valid directions restricted to %s' %
                                 valid_directions)
            if not persistence_file:  # pragma: no cover
                raise ValueError('`persistence_file` required to track '
                                 'date')

    def get_date(self):
        """ Get the appropriate date.  If there was a direction set,
        and a value in the persisted file, return it.  Otherwise, return
        the initial_date

        Note also the get_date_range() method.

        """
        if self.direction and os.path.exists(self.datefile):
            file = open(self.datefile, 'r')
            line = file.readline()
            self.initial_date = datetime.strptime(line.rstrip(), '%Y-%m-%d')

        return self.initial_date

    def get_date_range(self):
        """Get the start and end dates for current invocation

        Depending on step and direction, return the inclusive start
        and end dates.

        If direction wasn't set, treat get_date() as 'end' and 'start'
        should be (step-1) days beforhand.

        If direction was set to 'forwards', start date will be the
        same as get_date() returns, the end date will be step-1 days
        forward of that.

        If direction was set to 'backwards', end date will be the
        same as get_date() returns, the start date will be step-1 days
        before that.

        Returns two tuple(start_date,end_date)

        """
        if self.direction == 'forwards':
            start = self.get_date()
            end = start + timedelta(days=(self.step - 1))
        elif self.direction == 'backwards':
            end = self.get_date()
            start = end - timedelta(days=(self.step - 1))
        elif self.step != 1:
            end = self.get_date()
            start = end - timedelta(days=(self.step - 1))
        else:
            start = end = self.get_date()
        return start, end

    def bump_date(self):
        """Either increment or decrement the persisted date as per
        initialized values (optionally does nothing)

        """
        if self.direction == 'forwards':
            self._increment_datefile()
        elif self.direction == 'backwards':
            self._decrement_datefile()

    def _decrement_datefile(self):
        """in countdown mode (direction=='backwards'), persist to the
        filesystem the previous day needing to be processed.

        """
        assert(self.direction == 'backwards')
        dayback = self.initial_date - timedelta(days=self.step)
        logging.info("writing to datefile %s : %s", self.datefile, dayback)
        file = open(self.datefile, 'w')
        file.write(dayback.strftime('%Y-%m-%d'))
        file.close()

    def _increment_datefile(self):
        """in countup mode (direction=='forwards'), persist to the filesystem
        the next day needing to be processed.

        """
        assert(self.direction == 'forwards')
        dayforward = self.initial_date + timedelta(days=self.step)
        logging.info("writing to datefile %s : %s", self.datefile, dayforward)
        file = open(self.datefile, 'w')
        file.write(dayforward.strftime('%Y-%m-%d'))
        file.close()
