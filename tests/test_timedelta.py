import datetime as datetime

import hightime

import pytest

from .shorthands import timedelta


@pytest.mark.parametrize(
    "left, right",
    [
        (
            timedelta(),
            timedelta(
                w=0,
                d=0,
                h=0,
                m=0,
                s=0,
                ms=0,
                us=0,
                ns=0,
                ps=0,
                fs=0,
                as_=0,
                zs=0,
                ys=0,
            ),
        ),
        (timedelta(1), timedelta(d=1)),
        (timedelta(0, 1), timedelta(s=1)),
        (timedelta(0, 0, 1), timedelta(us=1)),
        (timedelta(w=1), timedelta(d=7)),
        (timedelta(d=1), timedelta(h=24)),
        (timedelta(h=1), timedelta(m=60)),
        (timedelta(m=1), timedelta(s=60)),
        (timedelta(s=1), timedelta(ms=1000)),
        (timedelta(ms=1), timedelta(us=1000)),
        (timedelta(us=1), timedelta(ns=1000)),
        (timedelta(ns=1), timedelta(ps=1000)),
        (timedelta(ps=1), timedelta(fs=1000)),
        (timedelta(fs=1), timedelta(as_=1000)),
        (timedelta(as_=1), timedelta(zs=1000)),
        (timedelta(zs=1), timedelta(ys=1000)),
        (timedelta(w=1.0 / 7), timedelta(d=1)),
        (timedelta(d=1.0 / 24), timedelta(h=1)),
        (timedelta(h=1.0 / 60), timedelta(m=1)),
        (timedelta(m=1.0 / 60), timedelta(s=1)),
        (timedelta(s=0.001), timedelta(ms=1)),
        (timedelta(ms=0.001), timedelta(us=1)),
        # Boundary values
        (timedelta(w=1 / (7 * 24 * 60 * 60 * 1000 * 1000)), timedelta(us=1)),
        (timedelta(d=1 / (24 * 60 * 60 * 1000 * 1000)), timedelta(us=1)),
        (timedelta(m=1 / (60 * 1000000000000)), timedelta(ps=1)),
        (timedelta(s=1 / 1000000000000000), timedelta(fs=1)),
        (timedelta(ms=1 / 1000000000000000), timedelta(as_=1)),
        (timedelta(us=1 / 1000000000000000), timedelta(zs=1)),
        (timedelta(ns=1 / 1000000000000000), timedelta(ys=1)),
        (timedelta(ps=1 / 1000000000000), timedelta(ys=1)),
        (timedelta(fs=1 / 1000000000), timedelta(ys=1)),
        (timedelta(as_=1 / 1000000), timedelta(ys=1)),
        (timedelta(zs=1 / 1000), timedelta(ys=1)),
        # larger unit clipping
        (timedelta(w=1 / (7 * 24 * 60 * 60 * 1000 * 1000 * 1000)), timedelta()),
        (timedelta(d=1 / (24 * 60 * 60 * 1000 * 1000 * 1000)), timedelta()),
        # Test rounding as well
        (timedelta(ys=0.50), timedelta()),
        (timedelta(ys=0.51), timedelta(ys=1)),
        (timedelta(ys=0.50, zs=1 / 100000), timedelta(ys=1)),
        # Negatives
        (timedelta(m=-1, s=60), timedelta()),
        (timedelta(d=-1, h=23), timedelta(d=-1, s=82800)),
        # Whatever else
        (timedelta(w=0.8), timedelta(d=5, s=51840)),
        (timedelta(w=2.8), timedelta(d=19, s=51840)),
        (timedelta(d=19.6), timedelta(d=19, s=51840)),
        (timedelta(d=1, w=2), timedelta(d=15)),
        (timedelta(d=7, w=2), timedelta(d=21)),
        (timedelta(d=1.5, w=2, h=7), timedelta(d=15, s=68400)),
        (timedelta(d=1.5, w=2, h=7, m=4), timedelta(d=15, s=68640)),
        (timedelta(d=1.5, s=15, w=2, h=7, m=4), timedelta(d=15, s=68655),),
        (timedelta(d=1.5, s=15, w=2.8, h=7.9, m=4.3), timedelta(d=21, s=37353),),
        (timedelta(m=0.3), timedelta(s=18)),
        (timedelta(s=0.3), timedelta(ms=300)),
        (timedelta(s=0.003), timedelta(us=3000)),
        (timedelta(ms=0.3), timedelta(us=300)),
        (timedelta(us=0.3), timedelta(ns=300)),
        (timedelta(ns=0.3), timedelta(ps=300)),
        (timedelta(s=0.1), timedelta(ms=100)),
        (timedelta(s=0.9), timedelta(ms=900)),
        (timedelta(fs=4), timedelta(as_=4000)),
        (timedelta(s=0.123456), timedelta(us=123456)),
    ],
)
def test_timedelta_constuctor(left, right):
    assert left == right


def test_timedelta_properties():
    assert 99 == timedelta(d=99).days
    assert 99 == timedelta(s=99).seconds
    assert 99 == timedelta(us=99).microseconds
    assert 99 == timedelta(fs=99).femtoseconds
    assert 99 == timedelta(ys=99).yoctoseconds


@pytest.mark.parametrize(
    "td, expected",
    [
        (timedelta(d=1), 86400.0),
        (timedelta(d=2), 172800.0),
        (timedelta(s=1), 1.0),
        (timedelta(s=2), 2.0),
        (timedelta(us=1), 0.000001),
        (timedelta(us=2), 0.000002),
        (timedelta(fs=1), 1e-15),
        (timedelta(fs=2), 2e-15),
        (timedelta(ys=1), 1e-24),
        (timedelta(ys=2), 2e-24),
        (timedelta(d=1, s=2, us=3, fs=4, ys=5), 86402.000003000000004000000005,),
    ],
)
def test_timedelta_total_seconds(td, expected):
    assert td.total_seconds() == expected


@pytest.mark.parametrize(
    "td, middle_part",
    [
        (timedelta(d=1), "days=1"),
        (timedelta(d=1, s=2), "days=1, seconds=2"),
        (timedelta(d=1, s=2, us=3), "days=1, seconds=2, microseconds=3"),
        (
            timedelta(d=1, s=2, us=3, fs=4),
            "days=1, seconds=2, microseconds=3, femtoseconds=4",
        ),
        (
            timedelta(d=1, s=2, us=3, fs=4, ys=5),
            "days=1, seconds=2, microseconds=3, femtoseconds=4, yoctoseconds=5",
        ),
        (timedelta(d=1, s=0, us=3), "days=1, microseconds=3"),
        (timedelta(d=1, s=0, us=3, ys=5), "days=1, microseconds=3, yoctoseconds=5"),
    ],
)
def test_timedelta_repr(td, middle_part):
    assert repr(td) == "hightime.timedelta({})".format(middle_part)
    assert td == eval(repr(td))


@pytest.mark.parametrize(
    "td, expected",
    [
        (timedelta(d=1), "1 day, 0:00:00"),
        (timedelta(d=2), "2 days, 0:00:00"),
        (timedelta(d=1, s=2), "1 day, 0:00:02"),
        (timedelta(d=1, s=2, us=3), "1 day, 0:00:02.000003"),
        (timedelta(d=1, s=2, us=30), "1 day, 0:00:02.000030"),
        (timedelta(d=1, s=2, us=3, fs=4), "1 day, 0:00:02.000003000000004",),
        (timedelta(d=1, s=2, us=3, fs=40), "1 day, 0:00:02.000003000000040",),
        (timedelta(d=1, s=2, us=0, fs=40), "1 day, 0:00:02.000000000000040",),
        (
            timedelta(d=1, s=2, us=3, fs=4, ys=5),
            "1 day, 0:00:02.000003000000004000000005",
        ),
        (
            timedelta(d=1, s=2, us=3, fs=4, ys=50),
            "1 day, 0:00:02.000003000000004000000050",
        ),
        (
            timedelta(d=1, s=2, us=3, fs=0, ys=50),
            "1 day, 0:00:02.000003000000000000000050",
        ),
        (
            timedelta(d=1, s=2, us=0, fs=4, ys=50),
            "1 day, 0:00:02.000000000000004000000050",
        ),
        (
            timedelta(d=1, s=2, us=0, fs=0, ys=50),
            "1 day, 0:00:02.000000000000000000000050",
        ),
    ],
)
def test_timedelta_str(td, expected):
    assert str(td) == expected


@pytest.mark.parametrize(
    "left, right, eq, lt",
    [
        (timedelta(d=1), timedelta(d=1), True, False),
        (timedelta(d=1, ys=1), timedelta(d=1, ys=1), True, False,),
        (timedelta(d=1), timedelta(d=-1), False, False),
        (timedelta(d=1), timedelta(d=-1), False, False),
        (timedelta(d=1), timedelta(s=1), False, False),
        (timedelta(2, 3, 4, fs=5, ys=6), timedelta(3, 3, 3, fs=3, ys=3), False, True,),
        (timedelta(2, 3, 4, fs=5, ys=6), timedelta(2, 3, 4, fs=5, ys=7), False, True,),
        (timedelta(2, 3, 4, fs=5, ys=6), timedelta(2, 3, 4, fs=6, ys=6), False, True,),
        (timedelta(2, 3), timedelta(2, 3, 5), False, True),
        (timedelta(2, 3, 4, ys=1), datetime.timedelta(2, 3, 4), False, False,),
    ],
)
def test_timedelta_comparison(left, right, eq, lt):
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
    "td", [timedelta(), timedelta(d=1)],
)
@pytest.mark.parametrize(
    "other", [False, True, 0, 1, (0, 0, 0, 0, 0), (1, 0, 0, 0, 0), "", [], ()],
)
def test_timedelta_comparison_unrelated_type(td, other):
    assert not (td == other)
    assert not (other == td)
    assert td != other
    assert other != td

    with pytest.raises(TypeError):
        assert td < other
    with pytest.raises(TypeError):
        assert other < td

    with pytest.raises(TypeError):
        assert td <= other
    with pytest.raises(TypeError):
        assert other <= td

    with pytest.raises(TypeError):
        assert td > other
    with pytest.raises(TypeError):
        assert other > td

    with pytest.raises(TypeError):
        assert td >= other
    with pytest.raises(TypeError):
        assert other >= td


def test_timedelta_bool():
    assert not timedelta()
    assert timedelta(d=1)
    assert timedelta(s=1)
    assert timedelta(us=1)
    assert timedelta(fs=1)
    assert timedelta(ys=1)


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (timedelta(), timedelta(d=1), timedelta(d=1)),
        (timedelta(d=1), timedelta(fs=1), timedelta(d=1, fs=1)),
        (timedelta(d=1), timedelta(ys=1), timedelta(d=1, ys=1)),
        (timedelta(fs=1), timedelta(fs=2), timedelta(fs=3)),
        (timedelta(fs=-1), timedelta(fs=2), timedelta(fs=1)),
        (
            timedelta(),
            timedelta(fs=-1),
            timedelta(d=-1, s=86399, us=999999, fs=999999999),
        ),
        (
            timedelta(ys=10),
            timedelta(fs=-1),
            timedelta(d=-1, s=86399, us=999999, fs=999999999, ys=10),
        ),
        # Also test datetime.timedelta
        (timedelta(fs=1), datetime.timedelta(seconds=1), timedelta(s=1, fs=1)),
        # @TODO: Test boundary values
    ],
)
def test_timedelta_add(left, right, expected):
    result = left + right
    assert left + right == expected
    assert isinstance(result, hightime.timedelta)

    result = right + left
    assert right + left == expected
    assert isinstance(result, hightime.timedelta)


def test_timedelta_add_integrals():
    for val in 1, 1.0:
        with pytest.raises(TypeError):
            timedelta(fs=1) + val
        with pytest.raises(TypeError):
            val + timedelta(fs=1)


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (timedelta(), timedelta(d=1), timedelta(d=-1)),
        (timedelta(d=1), timedelta(), timedelta(d=1)),
        (timedelta(d=1), timedelta(fs=1), timedelta(d=1, fs=-1)),
        (timedelta(d=1), timedelta(ys=1), timedelta(d=1, ys=-1)),
        (timedelta(fs=2), timedelta(fs=1), timedelta(fs=1)),
        (timedelta(fs=-1), timedelta(fs=2), timedelta(fs=-3)),
        (timedelta(), timedelta(fs=-1), timedelta(fs=1)),
        # Also test datetime.timedelta
        (timedelta(fs=1), datetime.timedelta(seconds=1), timedelta(s=-1, fs=1)),
        # Some special values: https://bugs.python.org/issue11576
        (
            timedelta(d=999999999, s=86399, us=999999, fs=999999999, ys=999999999),
            timedelta(d=999999999, s=86399, us=999999, fs=999999999, ys=999999998),
            timedelta(ys=1),
        ),
        (
            timedelta(d=999999999, s=1, us=1, fs=1, ys=1),
            timedelta(d=999999999, s=1, us=1, fs=1, ys=0),
            timedelta(ys=1),
        ),
        # @TODO: Test boundary values
    ],
)
def test_timedelta_sub(left, right, expected):
    result = left - right

    assert result == expected
    assert isinstance(result, hightime.timedelta)
    # Not commutative


def test_timedelta_sub_integrals():
    for val in 1, 1.0:
        with pytest.raises(TypeError):
            timedelta(fs=1) - val
        with pytest.raises(TypeError):
            val - timedelta(fs=1)


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (timedelta(), 0, timedelta()),
        (timedelta(), 1, timedelta()),
        (timedelta(fs=1), 0, timedelta()),
        (timedelta(fs=1), 1, timedelta(fs=1)),
        (timedelta(fs=1), 2, timedelta(fs=2)),
        (timedelta(fs=1), -1, timedelta(fs=-1)),
        (timedelta(fs=1), -2, timedelta(fs=-2)),
        (
            timedelta(d=1, s=2, us=3, fs=4, ys=5),
            2,
            timedelta(d=2, s=4, us=6, fs=8, ys=10),
        ),
        (timedelta(ys=1000), 1000000, timedelta(fs=1)),
        (timedelta(ys=1000), 0.5, timedelta(ys=500)),
        # Some special values: https://bugs.python.org/issue23521
        (timedelta(s=1), 0.123456, timedelta(us=123456)),
        (timedelta(s=1), 0.6112295, timedelta(us=611229, fs=500000000)),
        # @TODO: Test boundary values
    ],
)
def test_timedelta_mul(left, right, expected):
    def test(left, right, expected):
        result = left * right
        assert result == expected
        assert isinstance(result, hightime.timedelta)

        result = right * left
        assert result == expected
        assert isinstance(result, hightime.timedelta)

    test(left, right, expected)
    if isinstance(right, int):
        test(left, float(right), expected)


def test_timedelta_mul_nan():
    with pytest.raises(ValueError):
        timedelta(fs=1) * float("nan")


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (timedelta(fs=1), 1, timedelta(fs=1)),
        (timedelta(fs=1), 2, timedelta(ys=500000000)),
        (timedelta(fs=1), 10, timedelta(ys=100000000)),
        (timedelta(w=1), 7, timedelta(d=1)),
        (timedelta(w=1), 7 * 24, timedelta(h=1)),
        (timedelta(w=1), 7 * 24 * 60, timedelta(m=1)),
        (timedelta(ys=1), 2, timedelta()),
        # Divide by timedelta, get integer
        (timedelta(fs=1), timedelta(fs=1), 1),
        (timedelta(fs=1), timedelta(ys=1), 1000000000),
        (timedelta(fs=1), timedelta(us=1), 0),
        # Also test datetime.timedelta
        (timedelta(s=1), datetime.timedelta(microseconds=1), 1000000),
        (timedelta(fs=1), datetime.timedelta(microseconds=1), 0),
        # @TODO: Test boundary values
    ],
)
def test_timedelta_floordiv(left, right, expected):
    result = left // right

    assert result == expected
    assert isinstance(
        result, int if isinstance(right, datetime.timedelta) else hightime.timedelta,
    )


def test_timedelta_floordiv_unrelated_type():
    with pytest.raises(TypeError):
        0 // timedelta(fs=1)

    with pytest.raises(TypeError):
        timedelta(fs=1) // 1.0


def test_timedelta_floordiv_dividebyzero():
    with pytest.raises(ZeroDivisionError):
        timedelta(fs=1) // 0


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (timedelta(fs=1), 1, timedelta(fs=1)),
        (timedelta(fs=1), 2, timedelta(ys=500000000)),
        (timedelta(fs=1), 10, timedelta(ys=100000000)),
        (timedelta(w=1), 7, timedelta(d=1)),
        (timedelta(w=1), 7 * 24, timedelta(h=1)),
        (timedelta(w=1), 7 * 24 * 60, timedelta(m=1)),
        # Divide by timedelta, get integer
        (timedelta(fs=1), timedelta(fs=1), 1),
        (timedelta(fs=1), timedelta(ys=1), 1000000000),
        (timedelta(fs=1), timedelta(us=1), 0.000000001),
        # Also test datetime.timedelta
        (timedelta(s=1), datetime.timedelta(microseconds=1), 1000000),
        (timedelta(fs=1), datetime.timedelta(microseconds=1), 0.000000001),
        # Some special values: https://bugs.python.org/issue23521
        (timedelta(s=1), 1 / 0.6112295, timedelta(us=611229, fs=500000000),),
        # @TODO: Test boundary values
    ],
)
def test_timedelta_truediv(left, right, expected):
    def test(left, right, expected):
        result = left / right
        assert result == expected
        assert isinstance(result, (hightime.timedelta, int, float))

    test(left, right, expected)
    if isinstance(right, int):
        test(left, float(right), expected)


def test_timedelta_truediv_unrelated_type():
    with pytest.raises(TypeError):
        0 / timedelta(fs=1)


def test_timedelta_truediv_dividebyzero():
    with pytest.raises(ZeroDivisionError):
        timedelta(fs=1) / 0

    with pytest.raises(ZeroDivisionError):
        timedelta(fs=1) / 0.0


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (timedelta(m=2, s=30), timedelta(m=1), timedelta(s=30)),
        (timedelta(m=-2, s=30), timedelta(m=1), timedelta(s=30)),
        (timedelta(fs=10, ys=1), timedelta(ys=1), timedelta()),
        (timedelta(fs=10, ys=1), timedelta(ys=3), timedelta(ys=2)),
        # Also test datetime.timedelta
        (
            timedelta(m=-2, s=30, ys=1),
            datetime.timedelta(minutes=1),
            timedelta(s=30, ys=1),
        ),
        # @TODO: Test boundary values
    ],
)
def test_timedelta_mod(left, right, expected):
    result = left % right
    assert result == expected
    assert isinstance(result, hightime.timedelta)


def test_timedelta_mod_dividebyzero():
    with pytest.raises(ZeroDivisionError):
        timedelta(fs=1) % timedelta()


@pytest.mark.parametrize(
    "left, right, expected_q, expected_r",
    [
        (timedelta(m=2, s=30), timedelta(m=1), 2, timedelta(s=30)),
        (timedelta(m=-2, s=30), timedelta(m=1), -2, timedelta(s=30)),
        (timedelta(fs=10, ys=1), timedelta(ys=1), 10000000001, timedelta()),
        (timedelta(fs=10, ys=1), timedelta(ys=3), 3333333333, timedelta(ys=2)),
        # Also test datetime.timedelta
        (
            timedelta(m=-2, s=30, ys=1),
            datetime.timedelta(minutes=1),
            -2,
            timedelta(s=30, ys=1),
        ),
        # @TODO: Test boundary values
    ],
)
def test_timedelta_divmod(left, right, expected_q, expected_r):
    result_q, result_r = divmod(left, right)
    assert result_q == expected_q
    assert result_r == expected_r
    assert isinstance(result_q, int)
    assert isinstance(result_r, hightime.timedelta)


def test_timedelta_divmod_unrelated_type():
    with pytest.raises(TypeError):
        divmod(timedelta(fs=1), 10)


def test_timedelta_divmod_dividebyzero():
    with pytest.raises(ZeroDivisionError):
        divmod(timedelta(fs=1), timedelta())


def test_stddatetime_leftside_arithmetic():
    with pytest.raises(ZeroDivisionError):
        datetime.timedelta(microseconds=1) // timedelta(ys=3)

    with pytest.raises(ZeroDivisionError):
        datetime.timedelta(microseconds=1) / timedelta(ys=3)

    with pytest.raises(ZeroDivisionError):
        datetime.timedelta(microseconds=1) % timedelta(ys=3)


def test_timedelta_unary_arithmetic():
    td = timedelta(fs=1)

    assert +td == timedelta(fs=1)
    assert isinstance(+td, hightime.timedelta)

    assert -td == timedelta(fs=-1)
    assert isinstance(-td, hightime.timedelta)


def test_timedelta_abs():
    assert abs(timedelta(fs=1)) == timedelta(fs=1)
    assert abs(timedelta(fs=-1)) == timedelta(fs=1)
    assert isinstance(abs(timedelta(fs=1)), hightime.timedelta)


def test_timedelta_resolution():
    assert isinstance(hightime.timedelta.min, hightime.timedelta)
    assert isinstance(hightime.timedelta.max, hightime.timedelta)
    assert isinstance(hightime.timedelta.resolution, hightime.timedelta)
    assert hightime.timedelta.max > hightime.timedelta.min
    assert hightime.timedelta.min == timedelta(-999999999)
    assert hightime.timedelta.max == timedelta(
        999999999, 24 * 3600 - 1, 1e6 - 1, fs=1e9 - 1, ys=1e9 - 1
    )
    assert hightime.timedelta.resolution == timedelta(ys=1)


def test_timedelta_hash():
    assert hash(timedelta()) == hash(timedelta())
    assert hash(timedelta(fs=1)) == hash(timedelta(fs=1))
    assert hash(timedelta(fs=1)) != hash(timedelta(ys=1))
