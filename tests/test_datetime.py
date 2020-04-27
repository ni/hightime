import datetime as std_datetime
import sys

import hightime

import pytest

from .shorthands import datetime
from .shorthands import timedelta

_isPython36OrHigher = sys.version_info < (3, 6)


_SUBMICROSECOND_FIELDS = [
    "femtosecond",
    "yoctosecond",
]

_ALL_FIELDS = [
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "second",
    "microsecond",
] + _SUBMICROSECOND_FIELDS


class IntLike(object):
    def __init__(self, value=1):
        self.value = value

    def __int__(self):
        return self.value


def tzinfo(*, hours):
    return std_datetime.timezone(std_datetime.timedelta(hours=hours))


def test_datetime_isinstance():
    assert isinstance(datetime(), std_datetime.datetime)


@pytest.mark.parametrize("argname", _ALL_FIELDS)
@pytest.mark.parametrize("argvalue", ["1", 4.5, IntLike("1"), IntLike(4.5)])
def test_datetime_arg_wrong_type(argname, argvalue):
    with pytest.raises(TypeError):
        datetime(**{argname: argvalue})


@pytest.mark.parametrize(
    "argname, smallest, biggest",
    [
        ("year", 1, 9999),
        ("month", 1, 12),
        ("day", 1, 31),
        ("hour", 0, 23),
        ("minute", 0, 59),
        ("second", 0, 59),
        ("microsecond", 0, 999999),
        ("femtosecond", 0, 999999999),
        ("yoctosecond", 0, 999999999),
    ],
)
@pytest.mark.parametrize("argtype", [int, IntLike])
def test_datetime_arg_wrong_value(argname, smallest, biggest, argtype):
    with pytest.raises(ValueError):
        datetime(**{argname: argtype(smallest - 1)})

    with pytest.raises(ValueError):
        datetime(**{argname: argtype(biggest + 1)})


def test_datetime_tzinfo_as_femtoseconds():
    dt = datetime(1, 1, 1, 1, 1, 1, 1, std_datetime.timezone.utc)
    assert dt.femtosecond == 0
    assert dt.tzinfo == std_datetime.timezone.utc


def test_datetime_properties():
    dt = datetime(**{field: index + 1 for index, field in enumerate(_ALL_FIELDS)})
    for index, field in enumerate(_ALL_FIELDS):
        assert getattr(dt, field) == index + 1


@pytest.mark.parametrize(
    "dt, middle_part",
    [
        (datetime(2020, 4, 21), "2020, 4, 21, 0, 0"),
        (datetime(1, 1, 1, h=4), "1, 1, 1, 4, 0"),
        (datetime(1, 1, 1, h=1, m=4), "1, 1, 1, 1, 4"),
        (datetime(1, 1, 1, h=1, m=1, s=4), "1, 1, 1, 1, 1, 4"),
        (datetime(1, 1, 1, h=1, m=1, s=1, us=4), "1, 1, 1, 1, 1, 1, 4",),
        (datetime(1, 1, 1, fs=4), "1, 1, 1, 0, 0, 0, 0, 4"),
        (datetime(1, 1, 1, ys=4), "1, 1, 1, 0, 0, 0, 0, 0, 4"),
        (
            datetime(2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102),
            "2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102",
        ),
    ],
)
def test_datetime_repr(dt, middle_part):
    assert repr(dt) == "hightime.datetime({})".format(middle_part)
    assert dt == eval(repr(dt))
    # @TODO: tzinfo and fold


@pytest.mark.parametrize(
    "dt, expected",
    [
        (datetime(2020, 4, 21, 15, 29, 34), "2020-04-21T15:29:34"),
        (datetime(1, 1, 1, us=12345), "0001-01-01T00:00:00.012345"),
        (datetime(1, 1, 1, us=10), "0001-01-01T00:00:00.000010"),
        (datetime(1, 1, 1, fs=40), "0001-01-01T00:00:00.000000000000040"),
        (datetime(1, 1, 1, ys=40), "0001-01-01T00:00:00.000000000000000000000040",),
        (
            datetime(2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102),
            "2020-04-20T15:10:33.976508569718000529850102",
        ),
        # @TODO: Test timezone
    ],
)
def test_datetime_isoformat(dt, expected):
    assert dt.isoformat() == expected
    assert dt.isoformat(sep="X") == expected.replace("T", "X")

    if _isPython36OrHigher:
        assert dt.isoformat(timespec="hours") == expected[:13]
        assert dt.isoformat(timespec="minutes") == expected[:16]
        assert dt.isoformat(timespec="seconds") == expected[:19]

        if len(expected) < 20:
            expected += "."
        expected = expected.ljust(44, "0")

        assert dt.isoformat(timespec="milliseconds") == expected[:23]
        assert dt.isoformat(timespec="microseconds") == expected[:26]
        assert dt.isoformat(timespec="nanoseconds") == expected[:29]
        assert dt.isoformat(timespec="picoseconds") == expected[:32]
        assert dt.isoformat(timespec="femtoseconds") == expected[:35]
        assert dt.isoformat(timespec="attoseconds") == expected[:38]
        assert dt.isoformat(timespec="zeptoseconds") == expected[:41]
        assert dt.isoformat(timespec="yoctoseconds") == expected[:44]


@pytest.mark.parametrize(
    "dt, expected",
    [
        (datetime(2020, 4, 21, 15, 29, 34), "2020-04-21 15:29:34"),
        (datetime(1, 1, 1, us=12345), "0001-01-01 00:00:00.012345"),
        (datetime(1, 1, 1, us=10), "0001-01-01 00:00:00.000010"),
        (datetime(1, 1, 1, fs=40), "0001-01-01 00:00:00.000000000000040"),
        (datetime(1, 1, 1, ys=40), "0001-01-01 00:00:00.000000000000000000000040",),
        (
            datetime(2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102),
            "2020-04-20 15:10:33.976508569718000529850102",
        ),
        # @TODO: Test timezone
    ],
)
def test_datetime_str(dt, expected):
    assert str(dt) == expected
    assert "{}".format(dt) == expected


@pytest.mark.parametrize(
    "left, right, eq, lt",
    [
        (
            datetime(**{field: index + 1 for index, field in enumerate(_ALL_FIELDS)}),
            datetime(**{field: index + 1 for index, field in enumerate(_ALL_FIELDS)}),
            True,
            False,
        ),
        (datetime(), datetime(m=1), False, True),
        (datetime(), datetime(ys=1), False, True),
        (datetime(), datetime(ys=1), False, True),
        # Test with timezones
        (
            datetime(ys=1, tzinfo=tzinfo(hours=1)),
            datetime(ys=1, tzinfo=tzinfo(hours=1)),
            True,
            False,
        ),
        (
            datetime(ys=1, tzinfo=std_datetime.timezone.utc),
            datetime(ys=1, tzinfo=tzinfo(hours=0)),
            True,
            False,
        ),
        (
            datetime(ys=1, tzinfo=tzinfo(hours=0)),
            datetime(h=1, ys=1, tzinfo=tzinfo(hours=1)),
            True,
            False,
        ),
        (
            datetime(h=1, ys=1, tzinfo=tzinfo(hours=-1)),
            datetime(h=1, ys=1, tzinfo=tzinfo(hours=0)),
            False,
            False,
        ),
        # Also test datetime.datetime
        (datetime(2020, 4, 21, ys=1), std_datetime.datetime(2020, 4, 21), False, False),
    ],
)
def test_datetime_comparison(left, right, eq, lt):
    assert (left == right) == eq
    assert (right == left) == eq

    assert (left != right) == (not eq)
    assert (right != left) == (not eq)

    assert (left < right) == (lt and not eq)
    assert (right > left) == (lt and not eq)

    assert (left <= right) == (lt or eq)
    assert (right >= left) == (lt or eq)

    assert (left > right) == (not lt and not eq)
    assert (right < left) == (not lt and not eq)

    assert (left >= right) == (not lt or eq)
    assert (right <= left) == (not lt or eq)


def test_datetime_comparison_tzinfo_mismatch():
    without_tz = datetime()
    with_tz = datetime(tzinfo=tzinfo(hours=0))

    # Allowed to call eq and ne
    assert not (without_tz == with_tz)
    assert not (with_tz == without_tz)
    assert without_tz != with_tz
    assert with_tz != without_tz

    with pytest.raises(TypeError):
        without_tz < with_tz
    with pytest.raises(TypeError):
        with_tz > without_tz
    with pytest.raises(TypeError):
        without_tz <= with_tz
    with pytest.raises(TypeError):
        with_tz >= without_tz
    with pytest.raises(TypeError):
        without_tz > with_tz
    with pytest.raises(TypeError):
        with_tz < without_tz
    with pytest.raises(TypeError):
        without_tz >= with_tz
    with pytest.raises(TypeError):
        with_tz <= without_tz


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (
            datetime(2020, 4, 21, 15, 29, 34),
            timedelta(),
            datetime(2020, 4, 21, 15, 29, 34),
        ),
        (
            datetime(2020, 4, 21, 15, 29, 34),
            timedelta(ys=1),
            datetime(2020, 4, 21, 15, 29, 34, ys=1),
        ),
        (
            datetime(2020, 4, 21, 1, 29, 34, tzinfo=tzinfo(hours=1)),
            timedelta(ys=1),
            datetime(2020, 4, 21, 0, 29, 34, ys=1, tzinfo=tzinfo(hours=0)),
        ),
        (
            datetime(2020, 4, 21, 1, 29, 34, tzinfo=tzinfo(hours=1)),
            timedelta(w=2, d=4, s=44, ys=1),
            datetime(2020, 5, 9, 0, 30, 18, ys=1, tzinfo=tzinfo(hours=0)),
        ),
    ],
)
def test_datetime_add(left, right, expected):
    result = left + right
    assert result == expected
    assert isinstance(result, hightime.datetime)

    result = right + left
    assert result == expected
    assert isinstance(result, hightime.datetime)


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (
            datetime(2020, 4, 21, 15, 29, 34),
            datetime(2020, 4, 21, 15, 29, 34),
            timedelta(),
        ),
        (
            datetime(2020, 4, 21, 15, 29, 34, ys=1),
            datetime(2020, 4, 21, 15, 29, 34),
            timedelta(ys=1),
        ),
        (
            datetime(2020, 4, 21, 0, 29, 34, ys=1, tzinfo=tzinfo(hours=0)),
            datetime(2020, 4, 21, 1, 29, 34, tzinfo=tzinfo(hours=1)),
            timedelta(ys=1),
        ),
    ],
)
def test_datetime_sub(left, right, expected):
    result = left - right
    assert result == expected
    assert isinstance(result, hightime.timedelta)


def test_datetime_hash():
    assert hash(datetime(1, 1, 1)) == hash(datetime(1, 1, 1))
    assert hash(datetime(1, 1, 1, h=1, tzinfo=tzinfo(hours=1))) == hash(
        datetime(1, 1, 1, tzinfo=tzinfo(hours=0))
    )
    assert hash(datetime(1, 1, 1)) != hash(datetime(1, 1, 1, tzinfo=tzinfo(hours=0)))


def test_datetime_strptime_type():
    assert isinstance(
        hightime.datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M"),
        hightime.datetime,
    )


def test_datetime_tzname():
    assert datetime().tzname() is None
    assert datetime(tzinfo=std_datetime.timezone.utc).tzname().startswith("UTC")
    assert datetime(tzinfo=tzinfo(hours=1)).tzname() == "UTC+01:00"


def test_datetime_dst():
    assert datetime().dst() is None
    assert datetime(tzinfo=std_datetime.timezone.utc).dst() is None
    assert datetime(tzinfo=tzinfo(hours=1)).dst() is None


def test_datetime_utcoffset():
    assert datetime().utcoffset() is None
    assert (
        datetime(tzinfo=std_datetime.timezone.utc).utcoffset()
        == std_datetime.timedelta()
    )
    assert datetime(tzinfo=tzinfo(hours=1)).utcoffset() == std_datetime.timedelta(
        hours=1
    )
    assert datetime(
        tzinfo=std_datetime.timezone(hightime.timedelta(hours=1))
    ).utcoffset() == hightime.timedelta(hours=1)


def test_datetime_ctime():
    assert datetime(2020, 4, 21, 12, 33, 5, 44).ctime() == "Tue Apr 21 12:33:05 2020"
    assert (
        datetime(2020, 4, 21, 12, 33, 5, 44, tzinfo=tzinfo(hours=1)).ctime()
        == "Tue Apr 21 12:33:05 2020"
    )


def test_datetime_combine_type():
    assert isinstance(
        hightime.datetime.combine(std_datetime.date(1, 1, 1), std_datetime.time()),
        hightime.datetime,
    )


def test_datetime_utcnow_type():
    assert isinstance(hightime.datetime.utcnow(), hightime.datetime)


def test_datetime_now_type():
    assert isinstance(hightime.datetime.now(), hightime.datetime)


def test_datetime_fromtimestamp_type():
    assert isinstance(
        hightime.datetime.fromtimestamp(1587500974.003), hightime.datetime
    )


def test_datetime_utcfromtimestamp_type():
    assert isinstance(
        hightime.datetime.utcfromtimestamp(1587500974.003), hightime.datetime
    )


def test_datetime_astimezone_type():
    assert isinstance(
        datetime(tzinfo(hours=2)).astimezone(tzinfo(hours=1)), hightime.datetime
    )


def test_datetime_replace():
    dt = datetime()
    assert dt == dt.replace()
    assert datetime(year=1) == datetime(year=2).replace(year=1)
    assert datetime(month=1) == datetime(month=2).replace(month=1)
    assert datetime(day=1) == datetime(day=2).replace(day=1)
    assert datetime(hour=1) == datetime(hour=2).replace(hour=1)
    assert datetime(minute=1) == datetime(minute=2).replace(minute=1)
    assert datetime(second=1) == datetime(second=2).replace(second=1)
    assert datetime(microsecond=1) == datetime(microsecond=2).replace(microsecond=1)
    assert datetime(femtosecond=1) == datetime(femtosecond=2).replace(femtosecond=1)
    assert datetime(yoctosecond=1) == datetime(yoctosecond=2).replace(yoctosecond=1)

    assert datetime(hour=1, tzinfo=tzinfo(hours=1)) == datetime(hour=2).replace(
        tzinfo=tzinfo(hours=2)
    )
    dt = datetime(
        year=1,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        microsecond=1,
        femtosecond=1,
        yoctosecond=1,
    )
    assert dt == dt.replace()


@pytest.mark.parametrize(
    "dt, expected",
    [
        # I'd love to just put the float as expected, but if we don't pass the timezone,
        # it defaults to the system-timezone. There isn't a reliable way to override the
        # timezone on Windows, so this can't be fixed by a fixture.
        (
            datetime(2020, 4, 21, 15, 29, 34),
            std_datetime.datetime(2020, 4, 21, 15, 29, 34).timestamp(),
        ),
        (
            datetime(2020, 4, 21, 15, 29, 34, us=3000),
            std_datetime.datetime(
                2020, 4, 21, 15, 29, 34, microsecond=3000
            ).timestamp(),
        ),
        (
            datetime(2020, 4, 21, 15, 29, 34, us=30),
            std_datetime.datetime(2020, 4, 21, 15, 29, 34, microsecond=30).timestamp(),
        ),
        # Note the binary representation isn't exactly equal to our expected value
        # >>> from decimal import Decimal
        # >>> from hightime import datetime
        # >>> Decimal(
        # ...    datetime(2020, 4, 21, 15, 29, 34, microsecond=30, femtosecond=200)
        # ...    .timestamp()
        # ... )
        # Decimal('1587500974.000030040740966796875')
        (
            datetime(2020, 4, 21, 15, 29, 34, us=30, fs=200),
            std_datetime.datetime(2020, 4, 21, 15, 29, 34, microsecond=30).timestamp()
            + 0.000000002,
        ),
        (
            datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1),
            std_datetime.datetime(2020, 4, 21, 15, 29, 34, microsecond=30).timestamp()
            + 0.0000000020000001,
        ),
        (
            datetime(2020, 4, 21, 15, us=30, fs=2, ys=1, tzinfo=tzinfo(hours=2)),
            1587474000.0000300000000020000001,
        ),
    ],
)
def test_datetime_timestamp(dt, expected):
    assert dt.timestamp() == expected
