import datetime as std_datetime
from collections import OrderedDict
from itertools import dropwhile

import hightime


# Mostly ripped from `datetime`'s
def _checkArg(name, value):
    if not isinstance(value, int):
        if isinstance(value, float):
            raise TypeError("integer argument expected, got float")
        try:
            value = value.__index__()
        except AttributeError:
            raise TypeError(
                "an integer is required (got type %s)" % type(value).__name__
            ) from None
        else:
            if not isinstance(value, int):
                raise TypeError(
                    "__index__ returned non-int (type %s)" % type(value).__name__
                )

    if not 0 <= value <= 999999999:
        raise ValueError("{} must be in 0..999999999".format(name), value)

    return value


class datetime(std_datetime.datetime):
    __slots__ = (
        "_femtosecond",
        "_yoctosecond",
    )

    @classmethod
    def __new__impl__(
        cls,
        year,
        month=None,
        day=None,
        hour=0,
        minute=0,
        second=0,
        # No millisecond because microsecond takes in 0-999999
        microsecond=0,
        # The following are between 0-999999999
        femtosecond=0,
        yoctosecond=0,
        tzinfo=None,
        *,
        fold=0,
    ):
        if (
            isinstance(year, (bytes, str))
            and len(year) == 18
            and 1 <= ord(year[2:3]) & 0x7F <= 12
        ):
            # Pickle support
            if isinstance(year, str):
                try:
                    year = bytes(year, "latin1")
                except UnicodeEncodeError:
                    raise ValueError(
                        "Failed to encode latin1 string when unpickling a datetime "
                        "object. pickle.load(data, encoding='latin1') is assumed."
                    )
            # datetime pickle support uses special constructor arguments: a 10-byte
            # basestate and an optional tzinfo. hightime adds 8 more bytes for
            # femtoseconds and yoctoseconds.
            self = super().__new__(cls, year[0:10], month)
            fs1, fs2, fs3, fs4, ys1, ys2, ys3, ys4 = year[10:18]
            self._femtosecond = (((((fs1 << 8) | fs2) << 8) | fs3) << 8) | fs4
            self._yoctosecond = (((((ys1 << 8) | ys2) << 8) | ys3) << 8) | ys4
            return self
        self = super().__new__(
            cls,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            tzinfo=tzinfo,
            fold=fold,
        )

        femtosecond = _checkArg("femtosecond", femtosecond)
        yoctosecond = _checkArg("yoctosecond", yoctosecond)
        self._femtosecond = femtosecond
        self._yoctosecond = yoctosecond
        return self

    # See __new__impl__ for actual signature
    def __new__(cls, *args, **kwargs):
        if len(args) == 8 and "tzinfo" not in kwargs:
            # Allow the user to positionally specify timezone as the 8th param,
            # to be compatible with datetime.datetime
            if isinstance(args[-1], (std_datetime.timezone, type(None))):
                kwargs["tzinfo"] = args[-1]
                args = args[:-1]

        return cls.__new__impl__(*args, **kwargs)

    # Public properties

    year = std_datetime.datetime.year
    month = std_datetime.datetime.month
    day = std_datetime.datetime.day
    hour = std_datetime.datetime.hour
    minute = std_datetime.datetime.minute
    second = std_datetime.datetime.second
    microsecond = std_datetime.datetime.microsecond
    tzinfo = std_datetime.datetime.tzinfo
    fold = std_datetime.datetime.fold

    @property
    def femtosecond(self):
        """femtosecond (0-999999999)"""
        return self._femtosecond

    @property
    def yoctosecond(self):
        """yoctosecond (0-999999999)"""
        return self._yoctosecond

    # Public classmethods

    @classmethod
    def fromtimestamp(cls, t, tz=None):
        # NOTE: Does not support sub-microsecond values!
        result = std_datetime.datetime.fromtimestamp(t, tz)
        return cls._fromBase(result)

    @classmethod
    def utcfromtimestamp(cls, t):
        # NOTE: Does not support sub-microsecond values!
        result = std_datetime.datetime.utcfromtimestamp(t)
        return cls._fromBase(result)

    # Public methods

    def astimezone(self, tz=None):
        # astimezone doesn't always return type(self), so convert it back to a
        # hightime.datetime
        result = super().astimezone(tz)
        return (
            type(self)
            ._fromBase(result)
            .replace(femtosecond=self.femtosecond, yoctosecond=self.yoctosecond)
        )

    def isoformat(self, sep="T", timespec="auto"):
        specs = OrderedDict(
            [
                ("yoctoseconds", "{:06d}{:018d}"),
                ("zeptoseconds", "{:06d}{:015d}"),
                ("attoseconds", "{:06d}{:012d}"),
                ("femtoseconds", "{:06d}{:09d}"),
                ("picoseconds", "{:06d}{:06d}"),
                ("nanoseconds", "{:06d}{:03d}"),
            ]
        )

        if timespec == "auto":
            for spec in specs:
                if getattr(self, spec[:-1], 0) != 0:
                    timespec = spec
                    break

        if timespec not in specs:
            return super().isoformat(sep, timespec)

        value = self._yoctosecond + (self._femtosecond * 1000000000)
        for spec in specs:
            if spec == timespec:
                break
            value //= 1000

        fmt = specs[timespec]
        iso_strs = super().isoformat(sep).split("+")
        iso_strs[0] = iso_strs[0].split(".")[0]
        iso_strs[0] += "." + fmt.format(self.microsecond, value)
        return "+".join(iso_strs)

    def replace(
        self,
        year=None,
        month=None,
        day=None,
        hour=None,
        minute=None,
        second=None,
        microsecond=None,
        femtosecond=None,
        yoctosecond=None,
        tzinfo=True,
        *,
        fold=None,
    ):
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
        if femtosecond is None:
            femtosecond = self.femtosecond
        if yoctosecond is None:
            yoctosecond = self.yoctosecond
        if tzinfo is True:
            tzinfo = self.tzinfo
        if fold is None:
            fold = self.fold
        return type(self)(
            year,
            month,
            day,
            hour,
            minute,
            second,
            microsecond,
            femtosecond,
            yoctosecond,
            tzinfo=tzinfo,
            fold=fold,
        )

    # String operators

    def __repr__(self):
        """Convert to formal string, for repr()."""
        s = "{}.{}".format(self.__class__.__module__, self.__class__.__qualname__)

        # We only expose subminute fields if they aren't 0
        subminute_fields = reversed(
            list(
                dropwhile(
                    lambda x: x == 0,
                    [
                        self.yoctosecond,
                        self.femtosecond,
                        self.microsecond,
                        self.second,
                    ],
                )
            )
        )

        values = [self.year, self.month, self.day, self.hour, self.minute] + list(
            subminute_fields
        )
        s += "({}".format(", ".join(map(str, values)))

        if self.tzinfo is not None:
            s += ", tzinfo={!r}".format(self.tzinfo)
        if getattr(self, "fold", 0):
            s += ", fold=1"
        s += ")"
        return s

    __str__ = std_datetime.datetime.__str__

    # Comparison operators

    def __eq__(self, other):
        if isinstance(other, std_datetime.datetime):
            offset_type_mismatch = (
                (self.utcoffset() is None) + (other.utcoffset() is None)
            ) == 1
            return not offset_type_mismatch and not bool(self - other)
        elif not isinstance(other, std_datetime.date):
            return NotImplemented
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    # Arithmetic operators

    def __add__(self, other):
        "Add a datetime and a timedelta."
        if not isinstance(other, std_datetime.timedelta):
            return NotImplemented

        delta = hightime.timedelta(
            self.toordinal(),
            hours=self.hour,
            minutes=self.minute,
            seconds=self.second,
            microseconds=self.microsecond,
            femtoseconds=self.femtosecond,
            yoctoseconds=self.yoctosecond,
        )
        delta += other
        if 0 < delta.days <= datetime.max.toordinal():
            date = std_datetime.date.fromordinal(delta.days)
            hour, minute = divmod(delta.seconds, 3600)
            minute, second = divmod(minute, 60)

            return datetime(
                date.year,
                date.month,
                date.day,
                hour,
                minute,
                second,
                delta.microseconds,
                delta.femtoseconds,
                delta.yoctoseconds,
                tzinfo=self.tzinfo,
            )

        raise OverflowError("result out of range")

    __radd__ = __add__

    def __sub__(self, other):
        "Subtract two datetimes, or a datetime and a timedelta."
        if not isinstance(other, std_datetime.datetime):
            if isinstance(other, std_datetime.timedelta):
                return self + -other
            return NotImplemented

        base = hightime.timedelta(
            days=self.toordinal() - other.toordinal(),
            hours=self.hour - other.hour,
            minutes=self.minute - other.minute,
            seconds=self.second - other.second,
            microseconds=self.microsecond - other.microsecond,
            femtoseconds=self.femtosecond - getattr(other, "femtosecond", 0),
            yoctoseconds=self.yoctosecond - getattr(other, "yoctosecond", 0),
        )
        if self.tzinfo is other.tzinfo:
            return base

        my_offset = self.utcoffset()
        other_offset = other.utcoffset()

        if my_offset == other_offset:
            return base

        if my_offset is None or other_offset is None:
            raise TypeError("cannot mix naive and timezone-aware time")

        return base + other_offset - my_offset

    # Hash support

    def __hash__(self):
        t = self.replace(fold=0) if getattr(self, "fold", 0) else self
        offset = t.utcoffset()
        if offset is None:
            return hash(
                (
                    self.year,
                    self.month,
                    self.day,
                    self.hour,
                    self.minute,
                    self.second,
                    self.microsecond,
                    self.femtosecond,
                    self.yoctosecond,
                )
            )
        else:
            return hash(
                hightime.timedelta(
                    days=self.toordinal(),
                    hours=self.hour,
                    minutes=self.minute,
                    seconds=self.second,
                    microseconds=self.microsecond,
                    femtoseconds=self.femtosecond,
                    yoctoseconds=self.yoctosecond,
                )
                - offset
            )

    # Pickle support

    # The pure-Python implementation of datetime.datetime has a _getstate() method. Do
    # not override it because that would cause infinite recursion when running under
    # PyPy.
    def _hightime_getstate(self, protocol=3):
        reduce_value = super().__reduce_ex__(protocol)
        if not isinstance(reduce_value, tuple):
            raise TypeError(
                f"expected __reduce_ex__ to return tuple, not '{type(reduce_value)}'"
            )
        ctor_args = reduce_value[1]
        if not isinstance(ctor_args, tuple):
            raise TypeError(f"expected ctor args to be tuple, not '{type(ctor_args)}'")
        basestate = ctor_args[0]
        if not isinstance(basestate, bytes):
            raise TypeError(f"expected basestate to be bytes, not '{type(basestate)}'")
        if len(basestate) != 10:
            raise ValueError(f"expected basestate length 10, not {len(basestate)}")
        fs3, fs4 = divmod(self._femtosecond, 256)
        fs2, fs3 = divmod(fs3, 256)
        fs1, fs2 = divmod(fs2, 256)
        ys3, ys4 = divmod(self._yoctosecond, 256)
        ys2, ys3 = divmod(ys3, 256)
        ys1, ys2 = divmod(ys2, 256)
        basestate += bytes([fs1, fs2, fs3, fs4, ys1, ys2, ys3, ys4])
        return (basestate,) + ctor_args[1:]

    def __reduce_ex__(self, protocol):
        return (self.__class__, self._hightime_getstate(protocol))

    def __reduce__(self):
        return self.__reduce_ex__(2)

    # Helper methods

    def _cmp(self, other):
        if isinstance(other, std_datetime.datetime):
            diff = self - other  # this will take offsets into account
            if diff.days < 0:
                return -1
            return diff and 1 or 0
        elif not isinstance(other, std_datetime.date):
            return NotImplemented
        else:
            raise TypeError(
                "can't compare '{}' to '{}'".format(
                    type(self).__name__, type(other).__name__
                )
            )

    @classmethod
    def _fromBase(cls, base_datetime):
        return cls(
            year=base_datetime.year,
            month=base_datetime.month,
            day=base_datetime.day,
            hour=base_datetime.hour,
            minute=base_datetime.minute,
            second=base_datetime.second,
            microsecond=base_datetime.microsecond,
            tzinfo=base_datetime.tzinfo,
            fold=base_datetime.fold,
        )
