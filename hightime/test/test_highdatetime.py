import sys
import unittest
import time
import datetime

from .. import (
    SITimeUnit,
    DateTime,
    TimeDelta,
)


_isPython3Compat = (sys.version_info.major == 3)
_isPython36Compat = (_isPython3Compat and (sys.version_info.minor >= 6))
_isPython2Compat = (sys.version_info.major == 2)


class DateTimeTestCase(unittest.TestCase):

    @unittest.skipIf(not(_isPython36Compat),
                     "not supported in this version of Python")
    def test_datetimePy36CompatibleCtor(self):
        DateTime(year=1, month=1, day=1, hour=1, minute=1, second=1,
                     microsecond=1, tzinfo=None, fold=1)

    @unittest.skipIf(_isPython36Compat,
                     "not supported in this version of Python")
    def test_datetimeCompatibleCtor(self):
        DateTime(year=1, month=1, day=1, hour=1, minute=1, second=1,
                     microsecond=1, tzinfo=None)

    def test_basicCtor(self):
        DateTime(year=1, month=1, day=1,
                     frac_second=1, frac_second_exponent=SITimeUnit.NANOSECONDS)

    def test_ctorInvalidKWArgs(self):
        with self.assertRaises(TypeError):
            DateTime(year=1, month=1, day=1, somethingelse=4, frac_second=1)

    def test_ctorBadType(self):
        with self.assertRaises(TypeError):
            DateTime(year=1, month=1, day=1, frac_second="")
        with self.assertRaises(TypeError):
            DateTime(year=1, month=1, day=1, microsecond="")

    def test_repr(self):
        hdt = DateTime(year=1, month=1, day=1, second=1, microsecond=1)
        self.assertEqual(hdt, eval(repr(hdt)))
        hdt = DateTime(year=1, month=1, day=1, second=1,
                           frac_second=1, frac_second_exponent=-1)
        self.assertEqual(hdt, eval(repr(hdt)))

    def test_nanosecondDefaultFracSecondExponent(self):
        hdt = DateTime(year=1, month=1, day=1, frac_second=1)

    def test_highdatetimeEqual(self):
        hdt1 = DateTime(year=1, month=1, day=1, frac_second=1)
        hdt2 = DateTime(year=1, month=1, day=1, frac_second=1)
        self.assertEqual(hdt1, hdt2)

    def test_highdatetimeEqualDatetime(self):
        dt = datetime.datetime(year=1, month=1, day=1)
        hdt = DateTime(year=1, month=1, day=1)
        self.assertEqual(dt, hdt)

    def test_highdatetimeWithFracEqualDatetime(self):
        dt = datetime.datetime(year=1, month=1, day=1, microsecond=1)
        hdt = DateTime(year=1, month=1, day=1,
                           frac_second=1, frac_second_exponent=SITimeUnit.MICROSECONDS)
        self.assertEqual(dt, hdt)

        hdt = DateTime(year=1, month=1, day=1, microsecond=1)
        self.assertEqual(dt, hdt)

    def test_highdatetimeNotEqual(self):
        hdt1 = DateTime(year=1, month=1, day=1, frac_second=1)
        hdt2 = DateTime(year=1, month=1, day=1, frac_second=2)
        self.assertNotEqual(hdt1, hdt2)

    def test_highdatetimeNotEqualDatetime(self):
        dt = datetime.datetime(year=1, month=1, day=1)
        hdt = DateTime(year=1, month=1, day=1, frac_second=1)
        self.assertNotEqual(dt, hdt)

    def test_highdatetimeMinAttr(self):
        self.assertEqual(DateTime.min, datetime.datetime.min)

    def test_highdatetimeMaxAttr(self):
        # DateTime.max could be higher than datetime.max, but not easy to
        # represent the actual max due to the virtually-infinite about of
        # sub-microseconds that can be represented. Just re-use datetime.max?
        self.assertEqual(DateTime.max, datetime.datetime.max)

    def test_highdatetimeResolutionAttr(self):
        # DateTime resolution is virtually infinite. Return None to
        # represent infinity?
        self.assertEqual(DateTime.resolution, None)

    def test_highdatetimeFracsecondAttr(self):
        hdt = DateTime(year=1, month=1, day=1, hour=1, minute=1, second=1,
                           frac_second=1, frac_second_exponent=-9)
        self.assertEqual(hdt.frac_second, 1)
        self.assertEqual(hdt.frac_second_exponent, -9)

    def test_highdatetimeFracsecondFracsecondexponentAndMicrosecondCtor(self):
        with self.assertRaises(TypeError) as exc:
            DateTime(year=1, month=1, day=1,
                         microsecond=1, frac_second=1, frac_second_exponent=-1)
        self.assertEqual(exc.exception.args,
                         ("Cannot specify both microsecond and frac_second",))

    def test_highdatetimeFracsecondAndMicrosecondCtor(self):
        with self.assertRaises(TypeError) as exc:
            DateTime(year=1, month=1, day=1,
                         microsecond=1, frac_second=1)
        self.assertEqual(exc.exception.args,
                         ("Cannot specify both microsecond and frac_second",))

    def test_highdatetimeFracsecondExponentAndMicrosecondCtor(self):
        with self.assertRaises(TypeError) as exc:
            DateTime(year=1, month=1, day=1,
                         microsecond=1, frac_second_exponent=-1)
        self.assertEqual(exc.exception.args,
                         ("Cannot specify both microsecond and frac_second_exponent",))

    def test_highdatetimePositiveFracsecondExponent(self):
        with self.assertRaises(TypeError) as exc:
            DateTime(year=1, month=1, day=1,
                         frac_second=1, frac_second_exponent=1)
        self.assertEqual(exc.exception.args,
                         ("frac_second_exponent must be a negative long/int", 1))

    def test_highdatetimeFloatFracsecondExponent(self):
        with self.assertRaises(TypeError) as exc:
            DateTime(year=1, month=1, day=1,
                         frac_second=1, frac_second_exponent=-1.1)
        self.assertEqual(exc.exception.args,
                         ("frac_second_exponent must be a negative long/int", -1.1))

    def test_highdatetimeNonNumFracsecondExponent(self):
        with self.assertRaises(TypeError) as exc:
            DateTime(year=1, month=1, day=1,
                         frac_second=1, frac_second_exponent="1")
        self.assertEqual(exc.exception.args,
                         ("frac_second_exponent must be a negative long/int", "1"))

    def test_highdatetimeFracsecondGreaterThanSecond(self):
        with self.assertRaises(ValueError) as exc:
            DateTime(year=1, month=1, day=1,
                         frac_second=11, frac_second_exponent=-1)
        self.assertEqual(exc.exception.args,
                         ("total fractional seconds >= 1 second", 1.1))
        with self.assertRaises(ValueError) as exc:
            DateTime(year=1, month=1, day=1, microsecond=1000000)
        self.assertEqual(exc.exception.args,
                         ("total fractional seconds >= 1 second", 1.0))

    def test_highdatetimeFracSecondStr(self):
        hdt = DateTime(year=1, month=1, day=1, microsecond=1)
        self.assertEqual("0001-01-01 00:00:00.000001", str(hdt))

        # default frac_second_exponent
        hdt = DateTime(year=1, month=1, day=1,
                           hour=1, minute=1, second=1,
                           frac_second=1)
        self.assertEqual("0001-01-01 01:01:01+1e-9", str(hdt))
        # frac_second_exponent that should not use sci notation
        hdt = DateTime(year=1, month=1, day=1,
                           hour=1, minute=1, second=1,
                           frac_second=1, frac_second_exponent=-5)
        self.assertEqual("0001-01-01 01:01:01.00001", str(hdt))
        # very small frac_second_exponent
        hdt = DateTime(year=1, month=1, day=1,
                           hour=1, minute=1, second=1,
                           frac_second=1, frac_second_exponent=-9999999)
        self.assertEqual("0001-01-01 01:01:01+1e-9999999", str(hdt))

    def test_highdatetimeSubtractDateTime(self):
        hdt1 = DateTime(year=1, month=1, day=1,
                            frac_second=1, frac_second_exponent=-1)
        hdt2 = DateTime(year=1, month=1, day=1,
                            frac_second=2, frac_second_exponent=-1)

        expected = TimeDelta(frac_seconds=1, frac_seconds_exponent=-1)
        actual = hdt2 - hdt1
        self.assertEqual(expected, actual)

        expected = TimeDelta(frac_seconds=-1, frac_seconds_exponent=-1)
        actual = hdt1 - hdt2
        self.assertEqual(expected, actual)

        expected = TimeDelta(frac_seconds=0)
        actual = hdt1 - hdt1
        self.assertEqual(expected, actual)

    def test_highdatetimeSubtractDatetime(self):
        hdt = DateTime(year=1, month=1, day=1,
                           frac_second=1, frac_second_exponent=-1)
        dt = datetime.datetime(year=1, month=1, day=1)
        expected = TimeDelta(frac_seconds=1, frac_seconds_exponent=-1)
        actual = hdt - dt
        self.assertEqual(expected, actual)

        expected = TimeDelta(frac_seconds=-1, frac_seconds_exponent=-1)
        actual = dt - hdt
        self.assertEqual(expected, actual)

    def test_highdatetimeAddDatetime(self):
        hdt = DateTime(year=1, month=1, day=1,
                           frac_second=1, frac_second_exponent=-1)
        dt = datetime.datetime(year=1, month=1, day=1)
        with self.assertRaises(TypeError) as exc:
            result = hdt + dt
        with self.assertRaises(TypeError) as exc:
            result = dt + hdt

    def test_highdatetimeAddTimedelta(self):
        hdt = DateTime(year=1, month=1, day=1,
                           frac_second=1, frac_second_exponent=-1)
        td = datetime.timedelta(seconds=1, microseconds=1)
        expected = DateTime(year=1, month=1, day=1, second=1,
                                frac_second=100001,
                                frac_second_exponent=SITimeUnit.MICROSECONDS)
        actual = hdt + td
        self.assertEqual(expected, actual)
        actual = td + hdt
        self.assertEqual(expected, actual)

        # ensure proper rollover to the next second
        hdt2 = DateTime(year=1, month=1, day=1,
                            frac_second=999999,
                            frac_second_exponent=SITimeUnit.MICROSECONDS)
        expected = DateTime(year=1, month=1, day=1, second=2,
                                frac_second=0,
                                frac_second_exponent=SITimeUnit.MICROSECONDS)
        actual = hdt2 + td
        self.assertEqual(expected, actual)

        td2 = datetime.timedelta(seconds=1, microseconds=2)
        expected = DateTime(year=1, month=1, day=1, second=2,
                                frac_second=1,
                                frac_second_exponent=SITimeUnit.MICROSECONDS)
        actual = hdt2 + td2
        self.assertEqual(expected, actual)

    @unittest.expectedFailure
    def test_highdatetimeAddNegativeTimedelta(self):
        """FIXME: this needs to work"""
        # ensure negative deltas are subtracted
        hdt = DateTime(year=1, month=1, day=1, microsecond=1)
        td = datetime.timedelta(microseconds=-1)
        expected = DateTime(year=1, month=1, day=1)
        actual = hdt + td
        self.assertEqual(expected, actual)

    def test_highdatetimeAddTimeDelta(self):
        hdt = DateTime(year=1, month=1, day=1,
                           frac_second=1, frac_second_exponent=-1)
        htd = TimeDelta(seconds=1, frac_seconds=1, frac_seconds_exponent=-2)
        expected = DateTime(year=1, month=1, day=1, second=1,
                                frac_second=11, frac_second_exponent=-2)
        actual = hdt + htd
        self.assertEqual(expected, actual)
        actual = htd + hdt
        self.assertEqual(expected, actual)

        # ensure proper rollover to the next second
        hdt2 = DateTime(year=1, month=1, day=1,
                            frac_second=999999,
                            frac_second_exponent=SITimeUnit.MICROSECONDS)
        htd2 = TimeDelta(seconds=1, frac_seconds=1,
                             frac_seconds_exponent=SITimeUnit.MICROSECONDS)
        expected = DateTime(year=1, month=1, day=1, second=2,
                                frac_second=0,
                                frac_second_exponent=SITimeUnit.MICROSECONDS)
        actual = hdt2 + htd2
        self.assertEqual(expected, actual)

        htd3 = TimeDelta(seconds=1, frac_seconds=999999,
                             frac_seconds_exponent=SITimeUnit.MICROSECONDS)
        expected = DateTime(year=1, month=1, day=1, second=2,
                                frac_second=999998,
                                frac_second_exponent=SITimeUnit.MICROSECONDS)
        actual = hdt2 + htd3
        self.assertEqual(expected, actual)

    def test_highdatetimeAddSubtractSmallTimeDelta(self):
        now = DateTime.now()
        increment = TimeDelta(frac_seconds=135, frac_seconds_exponent=-13)
        later = now + increment
        self.assertNotEqual(now, later)
        before = later
        later += increment
        self.assertNotEqual(before, later)
        self.assertEqual(increment, later-before)

    def test_microsecondProp(self):
        hdt = DateTime(1, 1, 1)
        self.assertEqual(hdt.microsecond, 0)
        hdt = DateTime(1, 1, 1, microsecond=1)
        self.assertEqual(hdt.microsecond, 1)
        hdt = DateTime(1, 1, 1,
                           frac_second=1,
                           frac_second_exponent=SITimeUnit.MICROSECONDS)
        self.assertEqual(hdt.microsecond, 1)
        hdt = DateTime(1, 1, 1,
                           frac_second=1,
                           frac_second_exponent=SITimeUnit.MILLISECONDS)
        self.assertEqual(hdt.microsecond, 1000)
        hdt = DateTime(1, 1, 1,
                           frac_second=1,
                           frac_second_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(hdt.microsecond, 0)
        hdt = DateTime(1, 1, 1,
                           frac_second=1111,
                           frac_second_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(hdt.microsecond, 1)

    def test_nanosecondProp(self):
        hdt = DateTime(1, 1, 1)
        self.assertEqual(hdt.nanosecond, 0)
        hdt = DateTime(1, 1, 1,
                           frac_second=1,
                           frac_second_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(hdt.nanosecond, 1)
        hdt = DateTime(1, 1, 1,
                           frac_second=1,
                           frac_second_exponent=SITimeUnit.MICROSECONDS)
        self.assertEqual(hdt.nanosecond, 0)
        hdt = DateTime(1, 1, 1,
                           frac_second=1,
                           frac_second_exponent=SITimeUnit.PICOSECONDS)
        self.assertEqual(hdt.nanosecond, 0)
        hdt = DateTime(1, 1, 1,
                           frac_second=1111,
                           frac_second_exponent=SITimeUnit.PICOSECONDS)
        self.assertEqual(hdt.nanosecond, 1)

    def test_fromtimestamp(self):
        t = time.time()
        hdt = DateTime.fromtimestamp(t)
        self.assertTrue(isinstance(hdt, DateTime))
        self.assertEqual(hdt, eval(repr(hdt)))

    def test_utcfromtimestamp(self):
        t = time.time()
        hdt = DateTime.utcfromtimestamp(t)
        self.assertTrue(isinstance(hdt, DateTime))
        self.assertEqual(hdt, eval(repr(hdt)))

    def test_now(self):
        hdt = DateTime.now()
        self.assertTrue(isinstance(hdt, DateTime))
        self.assertEqual(hdt, eval(repr(hdt)))

    def test_utcnow(self):
        hdt = DateTime.utcnow()
        self.assertTrue(isinstance(hdt, DateTime))
        self.assertEqual(hdt, eval(repr(hdt)))

    def test_combine(self):
        d = datetime.date(1, 1, 1)
        t = datetime.time(1)
        hdt = DateTime.combine(d, t)
        self.assertTrue(isinstance(hdt, DateTime))
        self.assertEqual(hdt, eval(repr(hdt)))
        self.assertEqual(hdt, DateTime(1, 1, 1, 1))

if __name__ == "__main__":
    unittest.main()


"""
datetime
'__format__'
'__ge__'
'__gt__'
'__hash__'
'__le__'
'__lt__'
'__reduce__'
'__reduce_ex__'
'__sizeof__'


timedelta
'__abs__'
'__add__'
'__div__'
'__eq__'
'__floordiv__'
'__format__'
'__ge__'
'__gt__'
'__hash__'
'__le__'
'__lt__'
'__mul__'
'__ne__'
'__neg__'
'__nonzero__'
'__pos__'
'__radd__'
'__rdiv__'
'__reduce__'
'__reduce_ex__'
'__repr__'
'__rfloordiv__'
'__rmul__'
'__rsub__'
'__sizeof__'
'__str__'
'__sub__'

"""
