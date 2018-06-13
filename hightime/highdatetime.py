from datetime import datetime, timedelta  # noqa: H301
from . import util
from .sitimeunit import SITimeUnit


class DateTime(object):

    __slots__ = '_datetime', '_frac_second', '_frac_second_exponent'

    # DateTime resolution is virtually infinite, None represents infinity?
    resolution = None
    min = datetime.min
    max = datetime.max

    # Read-only field accessors
    @property
    def year(self):
        return self._datetime.year

    @property
    def month(self):
        return self._datetime.month

    @property
    def day(self):
        return self._datetime.day

    @property
    def hour(self):
        return self._datetime.hour

    @property
    def minute(self):
        return self._datetime.minute

    @property
    def second(self):
        return self._datetime.second

    @property
    def microsecond(self):
        return self._datetime.microsecond

    @property
    def tzinfo(self):
        return self._datetime.tzinfo

    if util.isPython36Compat:
        @property
        def fold(self):
            return self._datetime.fold

    @property
    def nanosecond(self):
        return util.get_subsecond_component(self._frac_second,
                                            self._frac_second_exponent,
                                            SITimeUnit.NANOSECONDS,
                                            SITimeUnit.MICROSECONDS)

    @property
    def frac_second(self):
        return self._frac_second

    @property
    def frac_second_exponent(self):
        return self._frac_second_exponent

    def __init__(self, year, month=None, day=None, hour=0, minute=0, second=0,
                 microsecond=0, tzinfo=None, fold=0,
                 frac_second=0, frac_second_exponent=None):

        # Not allowing both microsecond and frac_second simplifies the
        # implementation and reduces usage errors.
        if microsecond != 0:
            if frac_second != 0:
                raise TypeError("Cannot specify both microsecond and frac_second")
            if frac_second_exponent is not None:
                raise TypeError("Cannot specify both microsecond and frac_second_exponent")
            # Set frac_second members based on microsecond
            frac_second = microsecond
            frac_second_exponent = SITimeUnit.MICROSECONDS
        else:
            # frac_second_exponent defaults to None to check if it was improperly
            # used with microsecond, but the actual default is nanoseconds.  If
            # specified, frac_second_exponent must be a negative integer.
            if frac_second_exponent is None:
                frac_second_exponent = SITimeUnit.NANOSECONDS
            elif ((not(isinstance(frac_second_exponent, long)) and
                   not(isinstance(frac_second_exponent, int))) or
                  frac_second_exponent >= 0):
                raise TypeError("frac_second_exponent must be a negative long/int",
                                frac_second_exponent)

        if frac_second != 0:
            if ((not (isinstance(frac_second, long)) and
                 not (isinstance(frac_second, int)))):
                raise TypeError("fractional second must be a long/int",
                                frac_second)
            # Ensure fractional seconds <= 1 second
            total_frac_second = frac_second * (10 ** frac_second_exponent)
            if total_frac_second >= 1:
                raise ValueError("total fractional seconds >= 1 second",
                                 total_frac_second)
            # Set the microsecond arg for the datetime ctor based on frac_second
            if microsecond == 0:
                microsecond = util.get_subsecond_component(
                    frac_second, frac_second_exponent,
                    SITimeUnit.MICROSECONDS, SITimeUnit.SECONDS)

        # FIXME: deal with fold
        self._datetime = datetime(year, month, day, hour, minute,
                                  second, microsecond, tzinfo)
        self._frac_second = frac_second
        self._frac_second_exponent = frac_second_exponent

    def __repr__(self):
        """Convert to formal string, for repr()."""
        tmp = [self.year, self.month, self.day,  # These are never zero
               self.hour, self.minute, self.second]
        if tmp[-1] == 0:
            del tmp[-1]
        if tmp[-1] == 0:
            del tmp[-1]
        s = "%s(%s)" % (self.__class__.__name__, ", ".join(map(str, tmp)))
        if self._frac_second != 0:
            assert s[-1:] == ")"
            s = s[:-1] + ", frac_second=%d, frac_second_exponent=%d)" \
                % (self._frac_second, self._frac_second_exponent)
        if self.tzinfo is not None:
            assert s[-1:] == ")"
            s = s[:-1] + ", tzinfo=%r)" % self.tzinfo
        if util.isPython36Compat and self.fold:
            assert s[-1:] == ")"
            s = s[:-1] + ", fold=1)"
        return s

    def __str__(self):
        s = str(self.todatetime().replace(microsecond=0))
        if self._frac_second:
            # if not sub-usecond, use standard float format with leading &
            # trailing 0's stripped for compatibility with datetime useconds.
            if self._frac_second_exponent >= SITimeUnit.MICROSECONDS:
                s += "{:f}".format(self._frac_second *
                                   (10**self._frac_second_exponent)).strip("0")
            else:
                s += "+{:d}e{:d}".format(self._frac_second,
                                         self._frac_second_exponent)
        return s

    def __format__(self):
        raise NotImplementedError

    def __ge__(self):
        raise NotImplementedError

    def __gt__(self):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __le__(self):
        raise NotImplementedError

    def __lt__(self):
        raise NotImplementedError

    def __reduce__(self):
        raise NotImplementedError

    def __reduce_ex__(self):
        raise NotImplementedError

    def __sizeof__(self):
        raise NotImplementedError

    def __eq__(self, other):
        # FIXME: is isinstance() the right way to check this?
        if isinstance(other, DateTime) or isinstance(other, datetime):
            # check sub-second value first since that is more likely different.
            (frac_second,
             other_frac_second,
             frac_second_exponent) = util.normalize_frac_seconds(self, other)

            if frac_second == other_frac_second:
                # since sub-seconds equal, check the values with 0 sub-seconds
                # using the datetime __eq__ to properly handle datetime attrs.
                a = self.todatetime().replace(microsecond=0)
                # FIXME: deal with fold
                b = datetime(other.year, other.month, other.day,
                             other.hour, other.minute, other.second,
                             microsecond=0, tzinfo=other.tzinfo)
                return a == b
        return False

    def __add__(self, other):
        if isinstance(other, TimeDelta) or isinstance(other, timedelta):
            # add values without sub-seconds, then deal with normalized
            # sub-seconds separately.
            # FIXME: this results in 2 ctor calls, make more efficient
            whole_seconds_self = self.todatetime().replace(microsecond=0)
            whole_seconds_other = timedelta(seconds=int(other.total_seconds()))

            result = datetime.__add__(whole_seconds_self, whole_seconds_other)

            (frac_second_self, frac_second_other,
             result_frac_second_exponent) = util.normalize_frac_seconds(self,
                                                                        other)

            result_frac_second = frac_second_self + frac_second_other
            result_frac_second_multiplied = (result_frac_second *
                                             (10 ** result_frac_second_exponent))
            if result_frac_second_multiplied >= 1:
                result += timedelta(seconds=1)
                result_frac_second -= 10 ** abs(result_frac_second_exponent)
            elif result_frac_second_multiplied < 0:
                result -= timedelta(seconds=1)
                result_frac_second = ((10 ** abs(result_frac_second_exponent)) +
                                      result_frac_second)

            # FIXME: fold?
            return DateTime(year=result.year,
                            month=result.month,
                            day=result.day,
                            hour=result.hour,
                            minute=result.minute,
                            second=result.second,
                            tzinfo=result.tzinfo,
                            frac_second=result_frac_second,
                            frac_second_exponent=result_frac_second_exponent)

        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, DateTime) or isinstance(other, datetime):
            return self.__subtract_highdatetime__(self, other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, DateTime) or isinstance(other, datetime):
            return self.__subtract_highdatetime__(other, self)
        return NotImplemented

    def __ne__(self, other):
        return not(self.__eq__(other))

    def replace(self, year=None, month=None, day=None, hour=None,
                minute=None, second=None, microsecond=None, tzinfo=True,
                frac_second=None, frac_second_exponent=None,
                **kwargs):
        """
        Return a new DateTime with new values for the specified fields.
        """
        # Same args as __new__, see note about "fold" in __new__
        if util.isPython36Compat:
            fold = kwargs.pop("fold", None)
        if kwargs:
            raise TypeError("invalid keyword arg(s): %s" % kwargs.keys())

        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        if tzinfo is True:
            tzinfo = self.tzinfo
        if frac_second is None:
            frac_second = self.frac_second
        if frac_second_exponent is None:
            frac_second_exponent = self.frac_second_exponent

        if util.isPython36Compat:
            if fold is None:
                fold = self.fold
            return DateTime(year, month, day, hour, minute, second,
                            microsecond, tzinfo, fold=fold)
        else:
            return DateTime(year, month, day, hour, minute, second,
                            microsecond, tzinfo)

    def weekday(self):
        return self._datetime.weekday()

    def isoweekday(self):
        return self._datetime.isoweekday()

    def isocalendar(self):
        return self._datetime.isocalendar()

    def astimezone(self, tz=None):
        return self._datetime.isocalendar(tz)

    def isoformat(self, sep='T'):
        return self._datetime.isoformat(sep)

    def ctime(self):
        return self._datetime.ctime()

    def utcoffset(self):
        return self._datetime.utcoffset()

    def tzname(self):
        return self._datetime.tzname()

    def dst(self):
        return self._datetime.dst()

    def strftime(self, fmt):
        return self._datetime.strftime(fmt)

    def utctimetuple(self):
        return self._datetime.utctimetuple()

    def date(self):
        return self._datetime.date()

    def time(self):
        return self._datetime.time()

    def timetz(self):
        return self._datetime.timetz()

    def timetuple(self):
        return self._datetime.timetuple()

    def toordinal(self):
        return self._datetime.toordinal()

    def todatetime(self):
        # FIXME: deal with fold
        return datetime(self.year, self.month, self.day,
                        self.hour, self.minute, self.second,
                        self.microsecond, self.tzinfo)

    @staticmethod
    def fromdatetime(dt):
        assert isinstance(dt, datetime)

        if util.isPython36Compat:
            return DateTime(dt.year, dt.month, dt.day,
                            dt.hour, dt.minute, dt.second,
                            dt.microsecond, dt.tzinfo, fold=dt.fold)
        else:
            return DateTime(dt.year, dt.month, dt.day,
                            dt.hour, dt.minute, dt.second,
                            dt.microsecond, dt.tzinfo)

    @staticmethod
    def fromtimestamp(t, tz=None):
        return DateTime.fromdatetime(datetime.fromtimestamp(t, tz))

    @staticmethod
    def utcfromtimestamp(t):
        return DateTime.fromdatetime(datetime.utcfromtimestamp(t))

    @staticmethod
    def today():
        return DateTime.fromdatetime(datetime.today())

    @staticmethod
    def now(tz=None):
        return DateTime.fromdatetime(datetime.now(tz))

    @staticmethod
    def utcnow():
        return DateTime.fromdatetime(datetime.utcnow())

    @staticmethod
    def fromordinal(ordinal):
        return DateTime.fromdatetime(datetime.fromordinal(ordinal))

    @staticmethod
    def combine(date, time, tzinfo=None):
        if tzinfo is None:
            tzinfo = time.tzinfo
        elif not util.isPython36Compat:
            raise TypeError  # FIXME, support this
        if util.isPython36Compat:
            return DateTime.fromdatetime(datetime.combine(date, time, tzinfo))
        else:
            return DateTime.fromdatetime(datetime.combine(date, time))

    @staticmethod
    def strptime(date_string, format):
        return DateTime.fromdatetime(datetime.strptime(date_string, format))

    @staticmethod
    def __subtract_highdatetime__(a, b):
        assert (isinstance(a, datetime) or isinstance(a, DateTime)) and \
               (isinstance(b, datetime) or isinstance(b, DateTime))

        # Subtract values without sub-seconds, then deal with normalized
        # sub-seconds separately.
        # FIXME: deal with fold
        whole_seconds_a = datetime(a.year, a.month, a.day,
                                   a.hour, a.minute, a.second,
                                   microsecond=0, tzinfo=a.tzinfo)
        whole_seconds_b = datetime(b.year, b.month, b.day,
                                   b.hour, b.minute, b.second,
                                   microsecond=0, tzinfo=b.tzinfo)

        result = whole_seconds_a - whole_seconds_b

        (frac_seconds_a, frac_seconds_b,
         result_frac_seconds_exponent) = util.normalize_frac_seconds(a, b)

        result_frac_seconds = frac_seconds_a - frac_seconds_b

        # If the result is 0, then simply allow frac_seconds to go negative, but
        # if the result is >= 1 second, then remove 1 second from the result if
        # the frac_seconds difference is negative, and add the negative
        # frac_seconds to a second's-worth of fractional seconds to get the
        # remainder.
        if (result > timedelta(0)) and (result_frac_seconds < 0):
            result -= timedelta(seconds=1)
            result_frac_seconds = ((10 ** abs(result_frac_seconds_exponent)) +
                                   result_frac_seconds)

        return TimeDelta(days=result.days,
                         seconds=result.seconds,
                         frac_seconds=result_frac_seconds,
                         frac_seconds_exponent=result_frac_seconds_exponent)


# Import hightimedelta module here to avoid circular import problems related to
# the definition of the DateTime class above.
from .hightimedelta import TimeDelta  # noqa: E402

if(util.isPython3Compat):
    long = int
