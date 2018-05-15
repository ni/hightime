import sys
import unittest
import datetime

from .. import (
    Hightimedelta,
    Highdatetime,
    SITimeUnit,
)


_isPython3Compat = (sys.version_info.major == 3)
_isPython36Compat = (_isPython3Compat and (sys.version_info.minor >= 6))
_isPython2Compat = (sys.version_info.major == 2)


class HightimedeltaTestCase(unittest.TestCase):
    def test_ctorErrorChecking(self):
        # Ensure cannot mix milli/microseconds and frac_seconds
        with self.assertRaises(TypeError):
            Hightimedelta(milliseconds=1, frac_seconds=1)
        with self.assertRaises(TypeError):
            Hightimedelta(microseconds=1, frac_seconds=1)
        # Ensure frac_seconds_exponent is a negative int
        with self.assertRaises(TypeError):
            Hightimedelta(frac_seconds=1, frac_seconds_exponent=1)
        with self.assertRaises(TypeError):
            Hightimedelta(frac_seconds=1, frac_seconds_exponent="one")
        # Ensure total frac_seconds is <1 second
        with self.assertRaises(ValueError):
            Hightimedelta(frac_seconds=11, frac_seconds_exponent=-1)

    def test_addToDatetime(self):
        dt = datetime.datetime(1,1,1)
        htd = Hightimedelta(frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.NANOSECONDS)
        # To support adding a Hightimedelta to a standard datetime to get a
        # Highdatetime, the datetime object must be on the right-hand side. This
        # is because datetime defines a __add__ that tries to support all
        # timedelta types (including derived classes). The __radd__() on a
        # Hightimedelta never even gets called because of this.
        actual = htd + dt
        expected = Highdatetime(1,1,1,
                                frac_second=1,
                                frac_second_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(actual, expected)

    def test_addToTimedelta(self):
        htd1 = Hightimedelta(1)
        htd2 = Hightimedelta(2)
        actual = htd1 + htd2
        expected = Hightimedelta(3)
        self.assertEqual(actual, expected)

    def test_multiply(self):
        with self.assertRaises(TypeError) as exc:
            actual = Hightimedelta(2) * Hightimedelta(2)

        htd1 = Hightimedelta(seconds=2, frac_seconds=1,
                             frac_seconds_exponent=SITimeUnit.MILLISECONDS)

        actual = htd1 * 2
        expected = Hightimedelta(seconds=4, frac_seconds=2,
                                 frac_seconds_exponent=SITimeUnit.MILLISECONDS)
        self.assertEqual(actual, expected)

        actual = 2 * htd1
        self.assertEqual(actual, expected)

        # resulting frac_second > 1 second
        multiplier = 1000000000
        one_millisecond = 10**SITimeUnit.MILLISECONDS
        additional_seconds = int(one_millisecond * multiplier)
        actual = htd1 * multiplier
        expected = Hightimedelta(seconds=(2*multiplier)+additional_seconds)
        self.assertEqual(actual, expected)

        # FIXME
        # multiplier = -1000000000
        # one_millisecond = 10**SITimeUnit.MILLISECONDS
        # additional_seconds = int(one_millisecond * multiplier)
        # actual = htd1 * multiplier
        # expected = Hightimedelta(seconds=(2*multiplier)+additional_seconds)
        # self.assertEqual(actual, expected)

    def test_total_seconds(self):
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.MICROSECONDS)
        self.assertEqual(htd.total_seconds(), 86400.000001)
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(htd.total_seconds(), 86400.0)

    def test_highdatetimeFracSecondStr(self):
        htd = Hightimedelta(days=1, seconds=1, microseconds=1)
        self.assertEqual("1 day, 0:00:01.000001", str(htd))
        htd = Hightimedelta(days=1, seconds=1, frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.MILLISECONDS)
        self.assertEqual("1 day, 0:00:01.001000", str(htd))
        htd = Hightimedelta(days=1, seconds=1, frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual("1 day, 0:00:01+1e-9", str(htd))
        # very small frac_second_exponent
        htd = Hightimedelta(days=1, seconds=1, frac_seconds=1,
                            frac_seconds_exponent=-9999999)
        self.assertEqual("1 day, 0:00:01+1e-9999999", str(htd))

    def test_repr(self):
        htd = Hightimedelta(days=1, seconds=1, microseconds=1)
        self.assertEqual(htd, eval(repr(htd)))
        htd = Hightimedelta(days=1, seconds=1,
                            frac_seconds=1, frac_seconds_exponent=-1)
        self.assertEqual(htd, eval(repr(htd)))

    def test_microsecondsProp(self):
        htd = Hightimedelta(1)
        self.assertEqual(htd.microseconds, 0)
        htd = Hightimedelta(1, microseconds=1)
        self.assertEqual(htd.microseconds, 1)
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.MICROSECONDS)
        self.assertEqual(htd.microseconds, 1)
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.MILLISECONDS)
        self.assertEqual(htd.microseconds, 1000)
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(htd.microseconds, 0)
        htd = Hightimedelta(1,
                            frac_seconds=1111,
                            frac_seconds_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(htd.microseconds, 1)

    def test_nanosecondsProp(self):
        htd = Hightimedelta(1)
        self.assertEqual(htd.nanoseconds, 0)
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.NANOSECONDS)
        self.assertEqual(htd.nanoseconds, 1)
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.MICROSECONDS)
        self.assertEqual(htd.nanoseconds, 0)
        htd = Hightimedelta(1,
                            frac_seconds=1,
                            frac_seconds_exponent=SITimeUnit.PICOSECONDS)
        self.assertEqual(htd.nanoseconds, 0)
        htd = Hightimedelta(1,
                            frac_seconds=1111,
                            frac_seconds_exponent=SITimeUnit.PICOSECONDS)
        self.assertEqual(htd.nanoseconds, 1)
