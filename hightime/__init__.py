"""hightime

This package extends the built-in datetime types to allow for sub-microsecond values,
when possible.

The classes defined in this package are:

    datetime

        An impedance-matched subclass of datetime.datetime with sub-microsecond
        capabilities.

    timedelta

        An impedance-matched subclass of datetime.timedelta with sub-microsecond
        capabilities.

Please note that due to floating point arithmetic inaccuracies, the ability to specify
sub-microsecond values in terms of much larger units (weeks, days, seconds) has been
limited. For the exact limitation, please consult the various methods.
"""


from hightime._datetime import datetime
from hightime._timedelta import timedelta

# Hide that it was defined in a helper file
datetime.__module__ = __name__
timedelta.__module__ = __name__


datetime.min = datetime(1, 1, 1)
datetime.max = datetime(9999, 12, 31, 23, 59, 59, 999999, 999999999, 999999999)
datetime.resolution = timedelta(yoctoseconds=1)

timedelta.min = timedelta(-999999999)
timedelta.max = timedelta(
    days=999999999,
    hours=23,
    minutes=59,
    seconds=59,
    microseconds=999999,
    femtoseconds=999999999,
    yoctoseconds=999999999,
)
timedelta.resolution = timedelta(yoctoseconds=1)
