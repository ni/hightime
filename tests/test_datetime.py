from __future__ import annotations

import copy
import datetime as std_datetime
import pickle
from decimal import Decimal
from typing import Any, SupportsIndex, Type

import pytest

import hightime
from tests.othertime import OtherDateTime
from tests.shorthands import datetime, timedelta

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
    """An object that supports conversion to int."""

    def __init__(self, value: int = 1):
        """Initialize the IntLike object."""
        self.value = value

    def __index__(self) -> int:
        """Return self converted to an integer."""
        return self.value


def tzinfo(*, hours: int) -> std_datetime.timezone:
    return std_datetime.timezone(std_datetime.timedelta(hours=hours))


def test_datetime_isinstance() -> None:
    assert isinstance(datetime(), std_datetime.datetime)


@pytest.mark.parametrize("argname", _ALL_FIELDS)
@pytest.mark.parametrize(
    "argvalue", ["1", 4.5, IntLike("1"), IntLike(4.5)]  # type: ignore[arg-type]
)
def test_datetime_arg_wrong_type(argname: str, argvalue: float | int | SupportsIndex) -> None:
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
def test_datetime_arg_wrong_value(argname: str, smallest: int, biggest: int, argtype: Type) -> None:
    with pytest.raises(ValueError):
        datetime(**{argname: argtype(smallest - 1)})

    with pytest.raises(ValueError):
        datetime(**{argname: argtype(biggest + 1)})


def test_datetime_tzinfo_as_femtoseconds() -> None:
    dt = datetime(1, 1, 1, 1, 1, 1, 1, std_datetime.timezone.utc)
    assert dt.femtosecond == 0
    assert dt.tzinfo == std_datetime.timezone.utc


def test_datetime_properties() -> None:
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
        (
            datetime(1, 1, 1, h=1, m=1, s=1, us=4),
            "1, 1, 1, 1, 1, 1, 4",
        ),
        (datetime(1, 1, 1, fs=4), "1, 1, 1, 0, 0, 0, 0, 4"),
        (datetime(1, 1, 1, ys=4), "1, 1, 1, 0, 0, 0, 0, 0, 4"),
        (
            datetime(2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102),
            "2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102",
        ),
        (
            datetime(2020, 4, 21, tzinfo=tzinfo(hours=1)),
            "2020, 4, 21, 0, 0, " "tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))",
        ),
        (
            datetime(1, 1, 1, ys=4, tzinfo=tzinfo(hours=-1)),
            "1, 1, 1, 0, 0, 0, 0, 0, 4, "
            "tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=82800))",
        ),
        (
            datetime(1, 1, 1, ys=4, tzinfo=tzinfo(hours=-1), fold=1),
            "1, 1, 1, 0, 0, 0, 0, 0, 4, "
            "tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=82800)), "
            "fold=1",
        ),
        (datetime(2020, 4, 21, fold=1), "2020, 4, 21, 0, 0, fold=1"),
        (datetime(1, 1, 1, ys=4, fold=1), "1, 1, 1, 0, 0, 0, 0, 0, 4, fold=1"),
    ],
)
def test_datetime_repr(dt: hightime.datetime, middle_part: str) -> None:
    import datetime as datetime  # noqa: F401 - for tzinfo eval

    assert repr(dt) == "hightime.datetime({})".format(middle_part)
    assert dt == eval(repr(dt))


@pytest.mark.parametrize(
    "dt, expected, expected_tz",
    [
        (datetime(2020, 4, 21, 15, 29, 34), "2020-04-21T15:29:34", ""),
        (datetime(1, 1, 1, us=12345), "0001-01-01T00:00:00.012345", ""),
        (datetime(1, 1, 1, us=10), "0001-01-01T00:00:00.000010", ""),
        (datetime(1, 1, 1, fs=40), "0001-01-01T00:00:00.000000000000040", ""),
        (
            datetime(1, 1, 1, ys=40),
            "0001-01-01T00:00:00.000000000000000000000040",
            "",
        ),
        (
            datetime(2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102),
            "2020-04-20T15:10:33.976508569718000529850102",
            "",
        ),
        (
            datetime(2020, 4, 21, 15, 29, 34, tzinfo=tzinfo(hours=1)),
            "2020-04-21T15:29:34",
            "+01:00",
        ),
        (
            datetime(2020, 4, 21, 15, 29, 34, tzinfo=tzinfo(hours=23)),
            "2020-04-21T15:29:34",
            "+23:00",
        ),
        (
            datetime(1, 1, 1, ys=40, tzinfo=tzinfo(hours=1)),
            "0001-01-01T00:00:00.000000000000000000000040",
            "+01:00",
        ),
        pytest.param(
            datetime(1, 1, 1, ys=40, tzinfo=tzinfo(hours=-1)),
            "0001-01-01T00:00:00.000000000000000000000040",
            "-01:00",
            marks=pytest.mark.xfail(reason="https://github.com/ni/hightime/issues/52"),
        ),
        (
            datetime(1, 1, 1, ys=40, fold=1),
            "0001-01-01T00:00:00.000000000000000000000040",
            "",
        ),
        (
            datetime(1, 1, 1, ys=40, fold=1),
            "0001-01-01T00:00:00.000000000000000000000040",
            "",
        ),
    ],
)
def test_datetime_isoformat(dt: hightime.datetime, expected: str, expected_tz: str) -> None:
    assert dt.isoformat() == expected + expected_tz
    assert dt.isoformat(sep="X") == expected.replace("T", "X") + expected_tz

    assert dt.isoformat(timespec="hours") == expected[:13] + expected_tz
    assert dt.isoformat(timespec="minutes") == expected[:16] + expected_tz
    assert dt.isoformat(timespec="seconds") == expected[:19] + expected_tz

    if len(expected) < 20:
        expected += "."
    expected = expected.ljust(44, "0")

    assert dt.isoformat(timespec="milliseconds") == expected[:23] + expected_tz
    assert dt.isoformat(timespec="microseconds") == expected[:26] + expected_tz
    assert dt.isoformat(timespec="nanoseconds") == expected[:29] + expected_tz
    assert dt.isoformat(timespec="picoseconds") == expected[:32] + expected_tz
    assert dt.isoformat(timespec="femtoseconds") == expected[:35] + expected_tz
    assert dt.isoformat(timespec="attoseconds") == expected[:38] + expected_tz
    assert dt.isoformat(timespec="zeptoseconds") == expected[:41] + expected_tz
    assert dt.isoformat(timespec="yoctoseconds") == expected[:44] + expected_tz


@pytest.mark.parametrize(
    "dt, expected",
    [
        (datetime(2020, 4, 21, 15, 29, 34), "2020-04-21 15:29:34"),
        (datetime(1, 1, 1, us=12345), "0001-01-01 00:00:00.012345"),
        (datetime(1, 1, 1, us=10), "0001-01-01 00:00:00.000010"),
        (datetime(1, 1, 1, fs=40), "0001-01-01 00:00:00.000000000000040"),
        (
            datetime(1, 1, 1, ys=40),
            "0001-01-01 00:00:00.000000000000000000000040",
        ),
        (
            datetime(2020, 4, 20, 15, 10, 33, 976508, 569718000, 529850102),
            "2020-04-20 15:10:33.976508569718000529850102",
        ),
        # @TODO: Test timezone
    ],
)
def test_datetime_str(dt: hightime.datetime, expected: str) -> None:
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
def test_datetime_comparison(
    left: hightime.datetime, right: hightime.datetime, eq: bool, lt: bool
) -> None:
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


def test_datetime_comparison_tzinfo_mismatch() -> None:
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
    "dt",
    [datetime(), datetime(d=1)],
)
@pytest.mark.parametrize(
    "other",
    [False, True, 0, 1, (0, 0, 0, 0, 0), (1, 0, 0, 0, 0), "", [], ()],
)
def test_datetime_comparison_unrelated_type(dt: hightime.datetime, other: Any) -> None:
    assert not (dt == other)
    assert not (other == dt)
    assert dt != other
    assert other != dt

    with pytest.raises(TypeError):
        assert dt < other
    with pytest.raises(TypeError):
        assert other < dt

    with pytest.raises(TypeError):
        assert dt <= other
    with pytest.raises(TypeError):
        assert other <= dt

    with pytest.raises(TypeError):
        assert dt > other
    with pytest.raises(TypeError):
        assert other > dt

    with pytest.raises(TypeError):
        assert dt >= other
    with pytest.raises(TypeError):
        assert other >= dt


@pytest.mark.parametrize(
    "left, right, eq, lt",
    [
        (datetime(2020, 4, 21), OtherDateTime(datetime(2020, 4, 21).timestamp()), True, False),
        (datetime(2020, 4, 21), OtherDateTime(datetime(2020, 4, 22).timestamp()), False, True),
        (OtherDateTime(datetime(2020, 4, 21).timestamp()), datetime(2020, 4, 21), True, False),
        (OtherDateTime(datetime(2020, 4, 21).timestamp()), datetime(2020, 4, 22), False, True),
    ],
)
def test_datetime_comparison_compatible_type(
    left: hightime.datetime | OtherDateTime,
    right: hightime.datetime | OtherDateTime,
    eq: bool,
    lt: bool,
) -> None:
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
        (
            datetime(1850, 1, 1),
            timedelta(d=43829, fs=1),
            datetime(1970, 1, 1, 0, 0, 0, fs=1),
        ),
    ],
)
def test_datetime_add(
    left: hightime.datetime, right: hightime.timedelta, expected: hightime.datetime
) -> None:
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
        (
            datetime(2020, 1, 1, femtosecond=20),
            datetime(1970, 1, 1, 0, 0, 0),
            timedelta(days=50 * 365.24, femtoseconds=20),
        ),
        (
            datetime(2020, 1, 1, yoctosecond=1),
            datetime(1970, 1, 1, 0, 0, 0),
            timedelta(days=50 * 365.24, yoctoseconds=1),
        ),
        (
            datetime(1850, 1, 1, femtosecond=1),
            datetime(1970, 1, 1, 0, 0, 0),
            # -(120 * 365.24) = -43828.8 = -43829
            timedelta(days=-43829, femtoseconds=1),
        ),
    ],
)
def test_datetime_sub(
    left: hightime.datetime, right: hightime.datetime, expected: hightime.timedelta
) -> None:
    result = left - right
    assert result == expected
    assert isinstance(result, hightime.timedelta)


def test_datetime_hash() -> None:
    assert hash(datetime(1, 1, 1)) == hash(datetime(1, 1, 1))
    assert hash(datetime(1, 1, 1, h=1, tzinfo=tzinfo(hours=1))) == hash(
        datetime(1, 1, 1, tzinfo=tzinfo(hours=0))
    )
    assert hash(datetime(1, 1, 1)) != hash(datetime(1, 1, 1, tzinfo=tzinfo(hours=0)))


def test_datetime_strptime_type() -> None:
    assert isinstance(
        hightime.datetime.strptime("21/11/06 16:30", "%d/%m/%y %H:%M"),
        hightime.datetime,
    )


def test_datetime_tzname() -> None:
    assert datetime().tzname() is None
    tzname = datetime(tzinfo=std_datetime.timezone.utc).tzname()
    assert tzname is not None and tzname.startswith("UTC")
    assert datetime(tzinfo=tzinfo(hours=1)).tzname() == "UTC+01:00"


def test_datetime_dst() -> None:
    assert datetime().dst() is None
    assert datetime(tzinfo=std_datetime.timezone.utc).dst() is None
    assert datetime(tzinfo=tzinfo(hours=1)).dst() is None


def test_datetime_utcoffset() -> None:
    assert datetime().utcoffset() is None
    assert datetime(tzinfo=std_datetime.timezone.utc).utcoffset() == std_datetime.timedelta()
    assert datetime(tzinfo=tzinfo(hours=1)).utcoffset() == std_datetime.timedelta(hours=1)
    assert datetime(
        tzinfo=std_datetime.timezone(hightime.timedelta(hours=1))
    ).utcoffset() == hightime.timedelta(hours=1)


def test_datetime_ctime() -> None:
    assert datetime(2020, 4, 21, 12, 33, 5, 44).ctime() == "Tue Apr 21 12:33:05 2020"
    assert (
        datetime(2020, 4, 21, 12, 33, 5, 44, tzinfo=tzinfo(hours=1)).ctime()
        == "Tue Apr 21 12:33:05 2020"
    )


def test_datetime_combine_type() -> None:
    assert isinstance(
        hightime.datetime.combine(std_datetime.date(1, 1, 1), std_datetime.time()),
        hightime.datetime,
    )


@pytest.mark.filterwarnings("ignore:.*utcnow.*is deprecated.*:DeprecationWarning")
def test_datetime_utcnow_type() -> None:
    assert isinstance(hightime.datetime.utcnow(), hightime.datetime)


def test_datetime_now_type() -> None:
    assert isinstance(hightime.datetime.now(), hightime.datetime)


def test_datetime_fromtimestamp_type() -> None:
    assert isinstance(hightime.datetime.fromtimestamp(1587500974.003), hightime.datetime)


@pytest.mark.filterwarnings("ignore:.*utcfromtimestamp.*is deprecated.*:DeprecationWarning")
def test_datetime_utcfromtimestamp_type() -> None:
    assert isinstance(hightime.datetime.utcfromtimestamp(1587500974.003), hightime.datetime)


def test_datetime_astimezone_type() -> None:
    assert isinstance(
        datetime(tzinfo=tzinfo(hours=2)).astimezone(tzinfo(hours=1)), hightime.datetime
    )


def test_datetime_replace() -> None:
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
    assert datetime(hour=1, fold=1) == datetime(hour=1).replace(fold=1)
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
            std_datetime.datetime(2020, 4, 21, 15, 29, 34, microsecond=3000).timestamp(),
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
def test_datetime_timestamp(dt: hightime.datetime, expected: object) -> None:
    assert dt.timestamp() == expected


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (
            datetime(2020, 4, 21, 15, 29, 34),
            datetime(2020, 4, 21, 15, 29, 34),
            Decimal("0"),
        ),
        (
            datetime(2020, 1, 1, femtosecond=1),
            datetime(1970, 1, 1),
            Decimal("1577836800.000000000000001"),
        ),
        (
            datetime(2020, 1, 1, yoctosecond=1),
            datetime(1970, 1, 1),
            Decimal("1577836800.000000000000000000000001"),
        ),
        (
            datetime(1850, 1, 1, femtosecond=1),
            datetime(1970, 1, 1),
            Decimal("-3786825599.999999999999999"),
        ),
    ],
)
def test_datetime_sub_total_seconds_precision(
    left: hightime.datetime, right: hightime.datetime, expected: Decimal
) -> None:
    result = left - right
    assert result.precision_total_seconds() == expected
    assert isinstance(result, hightime.timedelta)


@pytest.mark.parametrize(
    "dt",
    [
        datetime(2020, 4, 21, 15, 29, 34),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=0x12345678, ys=0x23456789),
        datetime(2020, 4, 21, 15, 29, 34, us=999999, fs=999999999, ys=999999999),
        datetime(2020, 1, 1),
        datetime(1970, 1, 1),
        datetime(1850, 1, 1),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, tzinfo=tzinfo(hours=2)),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, tzinfo=tzinfo(hours=23)),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, tzinfo=tzinfo(hours=-1)),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, fold=1),
    ],
)
def test_datetime_copy(dt: hightime.datetime) -> None:
    dt_copy = copy.copy(dt)
    assert isinstance(dt_copy, hightime.datetime)
    assert dt_copy == dt


@pytest.mark.parametrize(
    "dt",
    [
        datetime(2020, 4, 21, 15, 29, 34),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=0x12345678, ys=0x23456789),
        datetime(2020, 4, 21, 15, 29, 34, us=999999, fs=999999999, ys=999999999),
        datetime(2020, 1, 1),
        datetime(1970, 1, 1),
        datetime(1850, 1, 1),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, tzinfo=tzinfo(hours=2)),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, tzinfo=tzinfo(hours=23)),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, tzinfo=tzinfo(hours=-1)),
        datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1, fold=1),
    ],
)
def test_datetime_pickle(dt: hightime.datetime) -> None:
    dt_copy = pickle.loads(pickle.dumps(dt))
    assert isinstance(dt_copy, hightime.datetime)
    assert dt_copy == dt


def test_datetime_pickle_uses_public_package_name() -> None:
    dt = datetime(2020, 4, 21, 15, 29, 34, us=30, fs=2, ys=1)
    dt_bytes = pickle.dumps(dt)
    assert b"hightime" in dt_bytes
    assert b"hightime._datetime" not in dt_bytes
