import datetime

import pytest

from .. import (
    TimeDelta,
    DateTime,
    SITimeUnit,
)


def test_ctorErrorChecking():
    # Ensure cannot mix milli/microseconds and frac_seconds
    with pytest.raises(TypeError):
        TimeDelta(milliseconds=1, frac_seconds=1)
    with pytest.raises(TypeError):
        TimeDelta(microseconds=1, frac_seconds=1)
    # Ensure frac_seconds_exponent is a negative int
    with pytest.raises(TypeError):
        TimeDelta(frac_seconds=1, frac_seconds_exponent=1)
    with pytest.raises(TypeError):
        TimeDelta(frac_seconds=1, frac_seconds_exponent="one")
    # Ensure total frac_seconds is <1 second
    with pytest.raises(ValueError):
        TimeDelta(frac_seconds=11, frac_seconds_exponent=-1)


def test_addTodatetime():
    dt = datetime.datetime(1, 1, 1)
    htd = TimeDelta(frac_seconds=1, frac_seconds_exponent=SITimeUnit.NANOSECONDS)
    # To support adding a TimeDelta to a standard datetime to get a
    # DateTime, the datetime object must be on the right-hand side. This
    # is because datetime defines a __add__ that tries to support all
    # timedelta types (including derived classes). The __radd__() on a
    # TimeDelta never even gets called because of this.
    actual = htd + dt
    expected = DateTime(
        1, 1, 1, frac_second=1, frac_second_exponent=SITimeUnit.NANOSECONDS
    )
    assert actual == expected


def test_addToTimedelta():
    htd1 = TimeDelta(1)
    htd2 = TimeDelta(2)
    actual = htd1 + htd2
    expected = TimeDelta(3)
    assert actual == expected


def test_multiply():
    with pytest.raises(TypeError) as exc:
        actual = TimeDelta(2) * TimeDelta(2)

    htd1 = TimeDelta(
        seconds=2, frac_seconds=1, frac_seconds_exponent=SITimeUnit.MILLISECONDS
    )

    actual = htd1 * 2
    expected = TimeDelta(
        seconds=4, frac_seconds=2, frac_seconds_exponent=SITimeUnit.MILLISECONDS
    )
    assert actual == expected

    actual = 2 * htd1
    assert actual == expected

    # resulting frac_second > 1 second
    multiplier = 1000000000
    one_millisecond = 10 ** SITimeUnit.MILLISECONDS
    additional_seconds = int(one_millisecond * multiplier)
    actual = htd1 * multiplier
    expected = TimeDelta(seconds=(2 * multiplier) + additional_seconds)
    assert actual == expected

    # FIXME
    # multiplier = -1000000000
    # one_millisecond = 10**SITimeUnit.MILLISECONDS
    # additional_seconds = int(one_millisecond * multiplier)
    # actual = htd1 * multiplier
    # expected = TimeDelta(seconds=(2*multiplier)+additional_seconds)
    # assert actual == expected


def test_total_seconds():
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.MICROSECONDS)
    assert htd.total_seconds() == 86400.000001
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.NANOSECONDS)
    assert htd.total_seconds() == 86400.000000001
    htd = TimeDelta(frac_seconds=29, frac_seconds_exponent=-12)
    assert htd.total_seconds() == 29e-12


def test_highdatetimeFracSecondStr():
    htd = TimeDelta(days=1, seconds=1, microseconds=1)
    assert "1 day, 0:00:01.000001" == str(htd)
    htd = TimeDelta(
        days=1,
        seconds=1,
        frac_seconds=1,
        frac_seconds_exponent=SITimeUnit.MILLISECONDS,
    )
    assert "1 day, 0:00:01.001000" == str(htd)
    htd = TimeDelta(
        days=1, seconds=1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.NANOSECONDS,
    )
    assert "1 day, 0:00:01+1e-9" == str(htd)
    # very small frac_second_exponent
    htd = TimeDelta(days=1, seconds=1, frac_seconds=1, frac_seconds_exponent=-9999999)
    assert "1 day, 0:00:01+1e-9999999" == str(htd)


def test_repr():
    htd = TimeDelta(days=1, seconds=1, microseconds=1)
    assert htd == eval(repr(htd))
    htd = TimeDelta(days=1, seconds=1, frac_seconds=1, frac_seconds_exponent=-1)
    assert htd == eval(repr(htd))


def test_microsecondsProp():
    htd = TimeDelta(1)
    assert htd.microseconds == 0
    htd = TimeDelta(1, microseconds=1)
    assert htd.microseconds == 1
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.MICROSECONDS)
    assert htd.microseconds == 1
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.MILLISECONDS)
    assert htd.microseconds == 1000
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.NANOSECONDS)
    assert htd.microseconds == 0
    htd = TimeDelta(1, frac_seconds=1111, frac_seconds_exponent=SITimeUnit.NANOSECONDS)
    assert htd.microseconds == 1


def test_nanosecondsProp():
    htd = TimeDelta(1)
    assert htd.nanoseconds == 0
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.NANOSECONDS)
    assert htd.nanoseconds == 1
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.MICROSECONDS)
    assert htd.nanoseconds == 0
    htd = TimeDelta(1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.PICOSECONDS)
    assert htd.nanoseconds == 0
    htd = TimeDelta(1, frac_seconds=1111, frac_seconds_exponent=SITimeUnit.PICOSECONDS)
    assert htd.nanoseconds == 1
