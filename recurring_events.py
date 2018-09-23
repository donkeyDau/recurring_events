# -*- coding: utf-8 -*-
from datetime import timedelta, date
import calendar

########################
# Date functions
########################


def get_next_workday_by_interval(cur_date, interval):
    '''
    Get the next workday starting from a certain date which is interval ahead

    @param cur_date: date of which the month will be taken
    @param interval: 1: every
                     2: every 2nd
                     ..
                     12: every 12th

    @rtype: datetime.datetime
    @return: date of the nth weekday of the month
    '''
    cur_date += timedelta(interval)

    # skip weekend
    if cur_date.weekday() > 4:
        cur_date += timedelta(days=2)
    return cur_date


def get_next_weekday(cur_date, weekday):
    '''
    Get the next weekday starting from a certain date.

    @param cur_date: date of which the month will be taken
    @param weekday: 1: Monday
                    2: Tuesday
                    3: Wednesday
                    4: Thursday
                    5: Friday
                    6: Saturday
                    7: Sunday
                    8: workday

    @rtype: datetime.datetime
    @return: date of the nth weekday of the month
    '''
    days_ahead = weekday - 1 - cur_date.weekday()
    return cur_date + timedelta(days_ahead)


def get_nth_weekday_of_month(cur_date, ordinal, weekday):
    '''
    Get the nth weekday of a certain month.

    @param cur_date: date of which the month will be taken
    @param ordinal: 1: first
                    2: second
                    3: third
                    4: fourth
                    5: last
    @param weekday: 1
    @rtype: datetime.datetime
    @return: date of the nth weekday of the month
    '''
    if weekday > 7:
        raise ValueError('Weekday exceeds maximum value of 7')
    if ordinal > 5:
        raise ValueError('Ordinal exceeds maximum value of 5')

    # last nth weekday of a month
    if ordinal == 5:
        if cur_date.month < 12:
           next_month_date = cur_date.replace(day=1, month=cur_date.month + 1)
        else:
           next_month_date = cur_date.replace(day=1, month=1, year=cur_date.year + 1)

        reference_date = get_nth_weekday_of_month(next_month_date, 1, weekday)
        return reference_date - timedelta(weeks=1)
    else:
        reference_date = cur_date.replace(day=1)
        adj = (weekday - 1 - reference_date.weekday()) % 7
        reference_date += timedelta(days=adj)
        reference_date += timedelta(weeks=ordinal - 1)
        return reference_date


def get_last_workday_of_month(cur_date):
    '''
    Get the last workday of a certain month.

    @param cur_date: date of which the month will be taken

    @rtype: datetime.datetime
    @return: date of the last workday of the month
    '''
    # date of last day in month
    last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
    cur_date = cur_date.replace(day=last_day_of_month)
    weekday = cur_date.weekday()

    if cur_date.weekday() in (5, 6):
        return cur_date - timedelta(days=weekday - 4)
    else:
        return cur_date


def get_first_workday_of_month(cur_date):
    '''
    Get the first workday of a certain month.

    @param cur_date: date of which the month will be taken

    @rtype: datetime.datetime
    @return: date of the first workday of the month
    '''
    # date of first day in month
    cur_date = cur_date.replace(day=1)
    weekday = cur_date.weekday()

    if cur_date.weekday() in (5, 6):
        return cur_date + timedelta(days=7 - weekday)
    else:
        return cur_date


def get_nth_workday_of_month(cur_date, ordinal):
    '''
    Get the nth workday of a certain month.

    @param cur_date: date of which the month will be taken
    @param ordinal: 1: first
                    2: second
                    3: third
                    4: fourth
                    5: last

    @rtype: datetime.datetime
    @return: date of the requested workday
    '''
    day_delta = 0
    first_workday = get_first_workday_of_month(cur_date)
    nth_workday = first_workday + timedelta(days=ordinal - 1)
    if first_workday.weekday() + ordinal - 1 > 4:
        day_delta = 2
    return nth_workday + timedelta(days=day_delta)

# Every 4 weeks on Saturday
# RecurringEvent(3, 4, weekday=5)

# Every three months on the first Friday
# RecurringEvent(4, 3, ordinal=1, weekday=4)

# Every last day of month
# RecurringEvent(4, 1, ordinal=5)

# Every second month on the 15th
# RecurringEvent(4, 2, day=15)


class RecurringEvent(object):
    '''
    Takes information about an reccuring event and can tell how often the issue
     occured since it last took place.

    The last occurence date has to be a valid execution date.
    '''

    def __init__(self, last_occurence, recurs, interval, day=None, ordinal=None,
                 weekday=None, first_occurence=None):
        '''
        @param last_occurence: last occurence of the event
        @param recurs: 1: daily
                       2: workdaily
                       3: weekly
                       4: monthly
        @param interval: 1: every
                         2: every 2nd
                         ..
                         12: every 12th
        @param day: 1: every 1st
                    2: every 2nd
                    ..
                    31: every 31th
        @param ordinal: 1: first
                        2: second
                        3: third
                        4: fourth
                        5: last
        @param weekday: 1: Monday
                        2: Tuesday
                        3: Wednesday
                        4: Thursday
                        5: Friday
                        6: Saturday
                        7: Sunday
                        8: workday
        @param first_occurence: first occurence of the event

        '''
        self._last_occurence = last_occurence if last_occurence is not None \
                               else first_occurence
        self._recurs = recurs
        self._interval = interval
        self._day = day if day else None
        self._ordinal = ordinal if ordinal else None
        self._weekday = weekday if weekday else None

        self._interval_end = None

        self._check_consistency()

    def _check_consistency(self):
        '''
        Checks consistency of passed arguments. Not every combination is valid.
        '''
        if not isinstance(self._last_occurence, date):
            raise ValueError('last_occurence needs to be datetime object not {0}'.format(type(self._last_occurence)))

        if self._day:
            if self._day < 1 or self._day > 31:
                raise ValueError('day needs to be in between 1 and 31. Is {0}'.format(self._day))
        if self._ordinal:
            if self._ordinal < 1 or self._ordinal > 5:
                raise ValueError(
                    'ordinal needs to be in between 1 and 5. Is {0}'.format(self._ordinal))

        if self._day and self._ordinal:
            raise AssertionError('Assigning day and ordinal at the same time is not valid')
        if self._day and self._weekday:
            raise AssertionError('Assigning day and weekday at the same time is not valid')

        if self._weekday == 8 and self._recurs != 4:
            raise AssertionError('Assigning workday without monthly ocurrence is not valid')
        if self._weekday == 8 and not self._ordinal:
            raise AssertionError('Assigning workday without ordinal is not valid')

        if self._recurs != 4 and self._day:
            raise AssertionError('Assigning day without monthly ocurrence is not valid')
        if self._recurs not in (2, 4) and self._ordinal:
            raise AssertionError('Assigning ordinal without monthly or workdaily ocurrence'
                                 ' is not valid')
        if self._recurs not in (3, 4) and self._weekday:
            raise AssertionError('Assigning weekday without weekly or monthly ocurrence'
                                 ' is not valid')

    def set_interval_end(self, interval_end=None):
        '''
        Sets the end of the interval to the passed date. If no date is passed
        the current date is taken.

        @param interval_end: End of the interval to check
        '''
        if interval_end is None:
            self._interval_end = datetime.now().date()
        else:
            if isinstance(interval_end, date):
                self._interval_end = interval_end
            else:
                self._interval_end = interval_end.date()

    def get_next_date(self, starting_date):
        '''
        Returns the next date of event to take place.

        @param starting_date: date from which the next occurence of the event
                              shall be evaluated

        @rtype: datetime.datetime
        @return: next occurence of event
        '''
        if self._weekday:
            if self._weekday < 8:
                return self._get_weekday_period(starting_date)
            else:
                return self._get_ordinal_workday_period(starting_date)
        elif self._day:
            return self._get_day_period(starting_date)
        else:
            if self._recurs == 1:
                # daily occurence
                return self._get_daily_period(starting_date)
            elif self._recurs == 2:
                # workdaily occurence
                return self._get_workdaily_period(starting_date)

    def number_of_periods(self, interval_end=None):
        '''
        Get the number of occurences until interval_end.

        @param interval_end: date until the number of occurences shall be
                             evaluated

        @rtype: int
        @return: number of periods until the end of the interval
        '''
        return len(self.get_events(interval_end))

    def get_events(self, interval_end=None):
        '''
        Get the dates of occurences until interval_end.

        @param interval_end: date until the number of occurences shall be
                             evaluated

        @rtype: int
        @return: number of periods until the end of the interval
        '''
        self.set_interval_end(interval_end)

        periods = []

        observed_date = self._last_occurence

        while True:
            observed_date = self.get_next_date(observed_date)
            if observed_date > self._interval_end:
                break
            periods.append(observed_date)
            self._last_occurence = observed_date
        return periods

    @property
    def last_occurence(self):
        return self._last_occurence

    #########################################
    # Period calculations
    #########################################
    def _get_daily_period(self, starting_date):
        '''
        Get the date of next daily occurence starting from starting_date.

        @param starting_date: date to start evalution from

        @rtype: datetime.datetime
        @return: date of the next occurence
        '''
        return starting_date + timedelta(days=self._interval)

    def _get_workdaily_period(self, starting_date):
        '''
        Get the date of next workdaily occurence starting from starting_date.

        @param starting_date: date to start evalution from

        @rtype: datetime.datetime
        @return: date of the next occurence
        '''
        if self._ordinal:
            raise NotImplementedError
        else:
            return get_next_workday_by_interval(starting_date, self._interval)

    def _get_ordinal_workday_period(self, starting_date):
        '''
        Get the date of next ordinal workday occurence starting from
        starting_date.
        Example: Every three months on the first workday

        @param starting_date: date to start evalution from

        @rtype: datetime.datetime
        @return: date of the next occurence
        '''
        # ordinal weekday period must be monthly recurrence
        month = starting_date.month + self._interval
        year_incr = int(month / 13)
        starting_date = starting_date.replace(day=1,
                                              month=month - year_incr * 12,
                                              year=starting_date.year + year_incr)
        if self._ordinal == 5:
            return get_last_workday_of_month(starting_date)
        else:
            return get_nth_workday_of_month(starting_date, self._ordinal)

    def _get_weekday_period(self, starting_date):
        '''
        Get the date of next weekday occurence starting from starting_date.
        Example: Every three months on the first Friday

        @param starting_date: date to start evalution from

        @rtype: datetime.datetime
        @return: date of the next occurence
        '''
        if self._ordinal:
            # ordinal weekday period must be monthly recurrence
            month = starting_date.month + self._interval
            year_incr = int(month / 13)
            starting_date = starting_date.replace(day=1,
                                                  month=month - year_incr * 12,
                                                  year=starting_date.year + year_incr)
            return get_nth_weekday_of_month(starting_date, self._ordinal, self._weekday)
        else:
            # Example: Every 4 weeks on Saturday
            starting_date = starting_date + timedelta(weeks=self._interval)
            return get_next_weekday(starting_date, self._weekday)

    def _get_day_period(self, starting_date):
        '''
        Get the date of next day occurence starting from starting_date.
        Every second month on the 15th: RecurringEvent(4, 2, day=15)

        @param starting_date: date to start evalution from

        @rtype: datetime.datetime
        @return: date of the next occurence
        '''
        month = starting_date.month + self._interval
        year_incr = int(month / 13)
        try:
            event = starting_date.replace(day=self._day,
                                          month=month - year_incr * 12,
                                          year=starting_date.year + year_incr)
        except ValueError:
            starting_date = starting_date.replace(day=1,
                                                  month=month - year_incr * 12 + 1,
                                                  year=starting_date.year + year_incr)
            event = starting_date - timedelta(days=1)
        return event

# EOF
