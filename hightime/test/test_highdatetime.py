import sys
import time
import datetime

import pytest

from .. import (
    SITimeUnit,
    DateTime,
    TimeDelta,
)


_isPython36OrHigher = sys.version_info < (3, 6)


@pytest.mark.skipif(not _isPython36OrHigher, reason="requires python3.6 or higher")
def test_datetimePy36CompatibleCtor():
    DateTime(
        year=1,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        microsecond=1,
        tzinfo=None,
        fold=1,
    )


@pytest.mark.skipif(_isPython36OrHigher, reason="requires python3.6 or higher")
def test_datetimeCompatibleCtor():
    DateTime(
        year=1, month=1, day=1, hour=1, minute=1, second=1, microsecond=1, tzinfo=None,
    )


def test_basicCtor():
    DateTime(
        year=1,
        month=1,
        day=1,
        frac_second=1,
        frac_second_exponent=SITimeUnit.NANOSECONDS,
    )


def test_ctorInvalidKWArgs():
    with pytest.raises(TypeError):
        DateTime(year=1, month=1, day=1, somethingelse=4, frac_second=1)


def test_ctorBadType():
    with pytest.raises(TypeError):
        DateTime(year=1, month=1, day=1, frac_second="")
    with pytest.raises(TypeError):
        DateTime(year=1, month=1, day=1, microsecond="")


def test_repr():
    hdt = DateTime(year=1, month=1, day=1, second=1, microsecond=1)
    assert hdt == eval(repr(hdt))
    hdt = DateTime(
        year=1, month=1, day=1, second=1, frac_second=1, frac_second_exponent=-1
    )
    assert hdt == eval(repr(hdt))


def test_nanosecondDefaultFracSecondExponent():
    hdt = DateTime(year=1, month=1, day=1, frac_second=1)


def test_highdatetimeEqual():
    hdt1 = DateTime(year=1, month=1, day=1, frac_second=1)
    hdt2 = DateTime(year=1, month=1, day=1, frac_second=1)
    assert hdt1 == hdt2


def test_highdatetimeEqualDatetime():
    dt = datetime.datetime(year=1, month=1, day=1)
    hdt = DateTime(year=1, month=1, day=1)
    assert dt == hdt


def test_highdatetimeWithFracEqualDatetime():
    dt = datetime.datetime(year=1, month=1, day=1, microsecond=1)
    hdt = DateTime(
        year=1,
        month=1,
        day=1,
        frac_second=1,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    assert dt == hdt

    hdt = DateTime(year=1, month=1, day=1, microsecond=1)
    assert dt == hdt


def test_highdatetimeNotEqual():
    hdt1 = DateTime(year=1, month=1, day=1, frac_second=1)
    hdt2 = DateTime(year=1, month=1, day=1, frac_second=2)
    assert hdt1 != hdt2


def test_highdatetimeNotEqualDatetime():
    dt = datetime.datetime(year=1, month=1, day=1)
    hdt = DateTime(year=1, month=1, day=1, frac_second=1)
    assert dt != hdt


def test_highdatetimeMinAttr():
    assert DateTime.min == datetime.datetime.min


def test_highdatetimeMaxAttr():
    # DateTime.max could be higher than datetime.max, but not easy to
    # represent the actual max due to the virtually-infinite about of
    # sub-microseconds that can be represented. Just re-use datetime.max?
    assert DateTime.max == datetime.datetime.max


def test_highdatetimeResolutionAttr():
    # DateTime resolution is virtually infinite. Return None to
    # represent infinity?
    assert DateTime.resolution == None


def test_highdatetimeFracsecondAttr():
    hdt = DateTime(
        year=1,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        frac_second=1,
        frac_second_exponent=-9,
    )
    assert hdt.frac_second == 1
    assert hdt.frac_second_exponent == -9


def test_highdatetimeFracsecondFracsecondexponentAndMicrosecondCtor():
    with pytest.raises(TypeError) as exc:
        DateTime(
            year=1,
            month=1,
            day=1,
            microsecond=1,
            frac_second=1,
            frac_second_exponent=-1,
        )
    assert exc.value.args == ("Cannot specify both microsecond and frac_second",)


def test_highdatetimeFracsecondAndMicrosecondCtor():
    with pytest.raises(TypeError) as exc:
        DateTime(year=1, month=1, day=1, microsecond=1, frac_second=1)
    assert exc.value.args == ("Cannot specify both microsecond and frac_second",)


def test_highdatetimeFracsecondExponentAndMicrosecondCtor():
    with pytest.raises(TypeError) as exc:
        DateTime(year=1, month=1, day=1, microsecond=1, frac_second_exponent=-1)
    assert exc.value.args == (
        "Cannot specify both microsecond and frac_second_exponent",
    )


def test_highdatetimePositiveFracsecondExponent():
    with pytest.raises(TypeError) as exc:
        DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent=1)
    assert exc.value.args == ("frac_second_exponent must be a negative long/int", 1)


def test_highdatetimeFloatFracsecondExponent():
    with pytest.raises(TypeError) as exc:
        DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent=-1.1)
    assert exc.value.args == ("frac_second_exponent must be a negative long/int", -1.1,)


def test_highdatetimeNonNumFracsecondExponent():
    with pytest.raises(TypeError) as exc:
        DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent="1")
    assert exc.value.args == ("frac_second_exponent must be a negative long/int", "1",)


def test_highdatetimeFracsecondGreaterThanSecond():
    with pytest.raises(ValueError) as exc:
        DateTime(year=1, month=1, day=1, frac_second=11, frac_second_exponent=-1)
    assert exc.value.args, "total fractional seconds >= 1 second" == 1.1
    with pytest.raises(ValueError) as exc:
        DateTime(year=1, month=1, day=1, microsecond=1000000)
    assert exc.value.args, "total fractional seconds >= 1 second" == 1.0


def test_highdatetimeFracSecondStr():
    hdt = DateTime(year=1, month=1, day=1, microsecond=1)
    assert "0001-01-01 00:00:00.000001" == str(hdt)

    # default frac_second_exponent
    hdt = DateTime(year=1, month=1, day=1, hour=1, minute=1, second=1, frac_second=1)
    assert "0001-01-01 01:01:01+1e-9" == str(hdt)
    # frac_second_exponent that should not use sci notation
    hdt = DateTime(
        year=1,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        frac_second=1,
        frac_second_exponent=-5,
    )
    assert "0001-01-01 01:01:01.00001" == str(hdt)
    # very small frac_second_exponent
    hdt = DateTime(
        year=1,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        frac_second=1,
        frac_second_exponent=-9999999,
    )
    assert "0001-01-01 01:01:01+1e-9999999" == str(hdt)


def test_highdatetimeSubtractDateTime():
    hdt1 = DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent=-1)
    hdt2 = DateTime(year=1, month=1, day=1, frac_second=2, frac_second_exponent=-1)

    expected = TimeDelta(frac_seconds=1, frac_seconds_exponent=-1)
    actual = hdt2 - hdt1
    assert expected == actual

    expected = TimeDelta(frac_seconds=-1, frac_seconds_exponent=-1)
    actual = hdt1 - hdt2
    assert expected == actual

    expected = TimeDelta(frac_seconds=0)
    actual = hdt1 - hdt1
    assert expected == actual


def test_highdatetimeSubtractDatetime():
    hdt = DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent=-1)
    dt = datetime.datetime(year=1, month=1, day=1)
    expected = TimeDelta(frac_seconds=1, frac_seconds_exponent=-1)
    actual = hdt - dt
    assert expected == actual

    expected = TimeDelta(frac_seconds=-1, frac_seconds_exponent=-1)
    actual = dt - hdt
    assert expected == actual


def test_highdatetimeAddDatetime():
    hdt = DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent=-1)
    dt = datetime.datetime(year=1, month=1, day=1)
    with pytest.raises(TypeError) as exc:
        result = hdt + dt
    with pytest.raises(TypeError) as exc:
        result = dt + hdt


def test_highdatetimeAddTimedelta():
    hdt = DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent=-1)
    td = datetime.timedelta(seconds=1, microseconds=1)
    expected = DateTime(
        year=1,
        month=1,
        day=1,
        second=1,
        frac_second=100001,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    actual = hdt + td
    assert expected == actual
    actual = td + hdt
    assert expected == actual

    # ensure proper rollover to the next second
    hdt2 = DateTime(
        year=1,
        month=1,
        day=1,
        frac_second=999999,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    expected = DateTime(
        year=1,
        month=1,
        day=1,
        second=2,
        frac_second=0,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    actual = hdt2 + td
    assert expected == actual

    td2 = datetime.timedelta(seconds=1, microseconds=2)
    expected = DateTime(
        year=1,
        month=1,
        day=1,
        second=2,
        frac_second=1,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    actual = hdt2 + td2
    assert expected == actual


@pytest.mark.xfail
def test_highdatetimeAddNegativeTimedelta():
    """FIXME: this needs to work"""
    # ensure negative deltas are subtracted
    hdt = DateTime(year=1, month=1, day=1, microsecond=1)
    td = datetime.timedelta(microseconds=-1)
    expected = DateTime(year=1, month=1, day=1)
    actual = hdt + td
    assert expected == actual


def test_highdatetimeAddTimeDelta():
    hdt = DateTime(year=1, month=1, day=1, frac_second=1, frac_second_exponent=-1)
    htd = TimeDelta(seconds=1, frac_seconds=1, frac_seconds_exponent=-2)
    expected = DateTime(
        year=1, month=1, day=1, second=1, frac_second=11, frac_second_exponent=-2
    )
    actual = hdt + htd
    assert expected == actual
    actual = htd + hdt
    assert expected == actual

    # ensure proper rollover to the next second
    hdt2 = DateTime(
        year=1,
        month=1,
        day=1,
        frac_second=999999,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    htd2 = TimeDelta(
        seconds=1, frac_seconds=1, frac_seconds_exponent=SITimeUnit.MICROSECONDS
    )
    expected = DateTime(
        year=1,
        month=1,
        day=1,
        second=2,
        frac_second=0,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    actual = hdt2 + htd2
    assert expected == actual

    htd3 = TimeDelta(
        seconds=1, frac_seconds=999999, frac_seconds_exponent=SITimeUnit.MICROSECONDS,
    )
    expected = DateTime(
        year=1,
        month=1,
        day=1,
        second=2,
        frac_second=999998,
        frac_second_exponent=SITimeUnit.MICROSECONDS,
    )
    actual = hdt2 + htd3
    assert expected == actual


def test_highdatetimeAddSubtractSmallTimeDelta():
    now = DateTime.now()
    increment = TimeDelta(frac_seconds=135, frac_seconds_exponent=-13)
    later = now + increment
    assert now != later
    before = later
    later += increment
    assert before != later
    assert increment == later - before


def test_microsecondProp():
    hdt = DateTime(1, 1, 1)
    assert hdt.microsecond == 0
    hdt = DateTime(1, 1, 1, microsecond=1)
    assert hdt.microsecond == 1
    hdt = DateTime(1, 1, 1, frac_second=1, frac_second_exponent=SITimeUnit.MICROSECONDS)
    assert hdt.microsecond == 1
    hdt = DateTime(1, 1, 1, frac_second=1, frac_second_exponent=SITimeUnit.MILLISECONDS)
    assert hdt.microsecond == 1000
    hdt = DateTime(1, 1, 1, frac_second=1, frac_second_exponent=SITimeUnit.NANOSECONDS)
    assert hdt.microsecond == 0
    hdt = DateTime(
        1, 1, 1, frac_second=1111, frac_second_exponent=SITimeUnit.NANOSECONDS
    )
    assert hdt.microsecond == 1


def test_nanosecondProp():
    hdt = DateTime(1, 1, 1)
    assert hdt.nanosecond == 0
    hdt = DateTime(1, 1, 1, frac_second=1, frac_second_exponent=SITimeUnit.NANOSECONDS)
    assert hdt.nanosecond == 1
    hdt = DateTime(1, 1, 1, frac_second=1, frac_second_exponent=SITimeUnit.MICROSECONDS)
    assert hdt.nanosecond == 0
    hdt = DateTime(1, 1, 1, frac_second=1, frac_second_exponent=SITimeUnit.PICOSECONDS)
    assert hdt.nanosecond == 0
    hdt = DateTime(
        1, 1, 1, frac_second=1111, frac_second_exponent=SITimeUnit.PICOSECONDS
    )
    assert hdt.nanosecond == 1


def test_fromtimestamp():
    t = time.time()
    hdt = DateTime.fromtimestamp(t)
    assert isinstance(hdt, DateTime)
    assert hdt == eval(repr(hdt))


def test_utcfromtimestamp():
    t = time.time()
    hdt = DateTime.utcfromtimestamp(t)
    assert isinstance(hdt, DateTime)
    assert hdt == eval(repr(hdt))


def test_now():
    hdt = DateTime.now()
    assert isinstance(hdt, DateTime)
    assert hdt == eval(repr(hdt))


def test_utcnow():
    hdt = DateTime.utcnow()
    assert isinstance(hdt, DateTime)
    assert hdt == eval(repr(hdt))


def test_combine():
    d = datetime.date(1, 1, 1)
    t = datetime.time(1)
    hdt = DateTime.combine(d, t)
    assert isinstance(hdt, DateTime)
    assert hdt == eval(repr(hdt))
    assert hdt, DateTime(1, 1, 1 == 1)
