from datetime import datetime, timedelta  # noqa: H301

from . import util
from .sitimeunit import SITimeUnit


class TimeDelta(object):

    __slots__ = '_timedelta', '_frac_seconds', '_frac_seconds_exponent'

    # TimeDelta resolution is virtually infinite, None represents infinity?
    resolution = None
    min = timedelta.min
    max = timedelta.max

    # Read-only field accessors
    @property
    def frac_seconds(self):
        return self._frac_seconds

    @property
    def frac_seconds_exponent(self):
        return self._frac_seconds_exponent

    @property
    def days(self):
        return self._timedelta.days

    @property
    def seconds(self):
        return self._timedelta.seconds

    @property
    def microseconds(self):
        return self._timedelta.microseconds

    @property
    def nanoseconds(self):
        return util.get_subsecond_component(self._frac_seconds,
                                            self._frac_seconds_exponent,
                                            SITimeUnit.NANOSECONDS,
                                            SITimeUnit.MICROSECONDS)

    def __init__(self, days=0, seconds=0, microseconds=0,
                 milliseconds=0, minutes=0, hours=0, weeks=0,
                 frac_seconds=0, frac_seconds_exponent=None):

        # Not allowing both microseconds or milliseconds along with arbitrary
        # frac_seconds simplifies the implementation and reduces usage errors.
        if (microseconds != 0) or (milliseconds != 0):
            if frac_seconds != 0:
                raise TypeError("Cannot specify microseconds or "
                                "milliseconds with frac_seconds")
            if frac_seconds_exponent is not None:
                raise TypeError("Cannot specify microseconds or "
                                "milliseconds with frac_seconds_exponent")

            # Set frac_second members based on microsecond or milliseconds,
            # normalize to microseconds
            frac_seconds = (milliseconds * 10 ** 3) + microseconds
            frac_seconds_exponent = SITimeUnit.MICROSECONDS
        else:
            # frac_seconds_exponent defaults to None to check if it was improperly
            # used with microseconds or milliseconds, but actual default is
            # nanoseconds.  If specified, frac_seconds_exponent must be a negative
            # integer.
            if frac_seconds_exponent is None:
                frac_seconds_exponent = SITimeUnit.NANOSECONDS
            elif ((not (isinstance(frac_seconds_exponent, long)) and
                   not (isinstance(frac_seconds_exponent, int))) or
                  frac_seconds_exponent >= 0):
                raise TypeError("frac_seconds_exponent must be a negative long/int",
                                frac_seconds_exponent)
            # Set the microseconds arg for the timedelta ctor based on frac_second
            microseconds = util.get_subsecond_component(
                frac_seconds, frac_seconds_exponent,
                SITimeUnit.MICROSECONDS, SITimeUnit.SECONDS)

        if frac_seconds != 0:
            # if (not(isinstance(frac_second, long)) and \
            #     not(isinstance(frac_second, int))):
            #     raise TypeError("fractional second must be a long/int",
            #                     frac_second)
            # Ensure fractional seconds <= 1 second
            total_frac_seconds = frac_seconds * (10 ** frac_seconds_exponent)
            if total_frac_seconds > 1:
                raise ValueError("total fractional seconds > 1 second",
                                 total_frac_seconds)

        self._timedelta = timedelta(days, seconds, microseconds,
                                    milliseconds, minutes, hours, weeks)
        self._frac_seconds = frac_seconds
        self._frac_seconds_exponent = frac_seconds_exponent

    def total_seconds(self):
        """Total seconds in the duration."""
        return (self.days * 86400) + self.seconds + \
               (self.microseconds * (10**SITimeUnit.MICROSECONDS))

    def __str__(self):
        s = str(timedelta(days=self._timedelta.days,
                          seconds=self._timedelta.seconds))
        # Since both microseconds and frac_seconds cannot be specified
        # together, return the default str only if not using frac_seconds
        if self._frac_seconds:
            # if not sub-usecond, use standard float format with leading 0's
            # stripped for compatibility with datetime.
            if self._frac_seconds_exponent >= SITimeUnit.MICROSECONDS:
                s += "{:f}".format(self._frac_seconds *
                                   (10**self._frac_seconds_exponent)).lstrip("0")
            else:
                s += "+{:d}e{:d}".format(self._frac_seconds,
                                         self._frac_seconds_exponent)
        return s

    def __repr__(self):
        """Convert to formal string, for repr()."""
        if self._frac_seconds == 0:
            return super(TimeDelta, self).__repr__()
        return "%s(%d, %d, frac_seconds=%d, frac_seconds_exponent=%d)" \
            % (self.__class__.__name__, self.days,
               self.seconds, self.frac_seconds, self.frac_seconds_exponent)

    def __eq__(self, other):
        if isinstance(other, TimeDelta) or isinstance(other, timedelta):
            # check sub-second value first since that is more likely different.
            (frac_second,
             other_frac_second,
             frac_seconds_exponent) = util.normalize_frac_seconds(self, other)

            if frac_second == other_frac_second:
                # since sub-seconds equal, check the values with 0 sub-seconds
                # using the timedelta __eq__ to properly handle datetime attrs.
                a = timedelta(days=self.days, seconds=self.seconds,
                              microseconds=0)
                b = timedelta(days=other.days, seconds=other.seconds,
                              microseconds=0)
                return timedelta.__eq__(a, b)
        return False

    def __add__(self, other):
        # DateTime already handles adding TimeDelta objs
        if isinstance(other, DateTime):
            return other + self
        elif isinstance(other, datetime):
            return DateTime.fromdatetime(other) + self
        elif isinstance(other, TimeDelta) or isinstance(other, timedelta):
            # add values without sub-seconds, then deal with normalized
            # sub-seconds separately.
            whole_seconds_self = timedelta(seconds=int(self.total_seconds()))
            whole_seconds_other = timedelta(seconds=int(other.total_seconds()))

            result = timedelta.__add__(whole_seconds_self, whole_seconds_other)

            (frac_seconds_self, frac_seconds_other,
             result_frac_seconds_exponent) = util.normalize_frac_seconds(self,
                                                                         other)

            result_frac_seconds = frac_seconds_self + frac_seconds_other
            result_frac_seconds_as_seconds = (result_frac_seconds *
                                              (10 ** result_frac_seconds_exponent))
            # adjust whole seconds if necessary
            if result_frac_seconds_as_seconds >= 1:
                result = timedelta.__add__(result, timedelta(seconds=1))
                result_frac_seconds -= 10 ** abs(result_frac_seconds_exponent)
            elif result_frac_seconds_as_seconds < 0:
                result = timedelta.__sub__(result, timedelta(seconds=1))
                result_frac_seconds += 10 ** abs(result_frac_seconds_exponent)

            return TimeDelta(days=result.days,
                             seconds=result.seconds,
                             frac_seconds=result_frac_seconds,
                             frac_seconds_exponent=result_frac_seconds_exponent)

        return NotImplemented

    __radd__ = __add__

    def __mul__(self, other):
        if isinstance(other, int):
            whole_seconds_self = timedelta(seconds=int(self.total_seconds()))
            result = whole_seconds_self * other
            result_frac_seconds = self.frac_seconds * other
            result_frac_seconds_as_seconds = (result_frac_seconds *
                                              (10 ** self.frac_seconds_exponent))
            num_extra_seconds = int(result_frac_seconds_as_seconds)

            # adjust whole seconds if necessary
            if num_extra_seconds >= 1:
                result = timedelta.__add__(result,
                                           timedelta(seconds=num_extra_seconds))
                result_frac_seconds -= ((10 ** abs(self.frac_seconds_exponent)) *
                                        num_extra_seconds)
            elif num_extra_seconds < 0:
                result = timedelta.__sub__(result,
                                           timedelta(seconds=num_extra_seconds))
                result_frac_seconds += ((10 ** abs(self.frac_seconds_exponent)) *
                                        num_extra_seconds)

            return TimeDelta(days=result.days,
                             seconds=result.seconds,
                             frac_seconds=result_frac_seconds,
                             frac_seconds_exponent=self.frac_seconds_exponent)

        if isinstance(other, float):
            return NotImplemented  # FIXME

        return NotImplemented

    __rmul__ = __mul__


# Import highdatetime module here to avoid circular import problems related to
# the definition of the TimeDelta class above.
from .highdatetime import DateTime  # noqa: E402

if(util.isPython3Compat):
    long = int
