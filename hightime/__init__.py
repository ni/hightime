"""hightime - rick.ratzel@ni.com

FIXME: update this docstring to reflect the name change to "hightime" and that
it extends datetime.

This package defines a universal timestamp type which can be used to represent
a point in time - in whole or arbitrary fractional units of seconds - since a
predetermined Epoch.  This type is currently "Epoch-less" in that it simply
maintains a count, but may be extended in the future to also indicate the Epoch
for which the count is relative to in describing the point in time.  In
practice, the Epoch is understood to be part of a larger application context
which is known by users, for example, time.time() returns a count from the
POSIX Epoch on a Linux system.

The classes defined in this package are intended to provide utilities that make
it easy to work with timestamps.  This includes common operators (subtraction,
addition, comparisons) and human-readable string representations using standard
units.  Other helper utilities will be added as needed.

These classes are based on Python's "long" (for Python versions 2.x that
support it) or "int" (for Python version 3.x that support int as long) types,
which are implementations of BIGNUM
(https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic) and allow users
to express timestamps to virtually limitless precision.  This seems more
"pythonic" in that it is consistent with other numeric types that do not
require the user to know the size upfront.

The classes defined in this package are:

   Timespan

      A Timespan represents a time duration.  Instances of Timespans are
      commonly used when adding or subtracting to or from a Timestamp to get a
      different Timestamp that represents a different point in time.  A
      Timespan is also returned when two Timestamps are subtracted from each
      other, and in this case, it represents the difference in time between the
      two points. Timespans can have a negative value that can be used during
      Timestamp subtractions to indicate if a Timestamp is "ahead" or "behind"
      another.

      A Timespan can be constructed in a number of different ways:
         Timespan( <int n seconds>, [exponent=<multiplier>] )

            Create a timespan of length n seconds.  exponent defaults to a 1.0
            multiplier, representing whole seconds.  If a unit is specified,
            the span will be a duration of length n exponent.

         Timespan( <float n seconds>, [exponent=<multiplier>] )

            Create a timespan of length n seconds with potential fractional
            seconds included.  The exponent of the fractional seconds depends on
            the number of sig figs after the decimal point, as determined by
            the default string repr of the float.

            NOTE: the nature of floating point numbers could lead to excessive
            false precision when represented in a timespan. To get exactly the
            precision needed, construct with either a string repr of the
            floating point (inconvenient, but used frequently in examples for
            the Python Decimal module), or use separate seconds,
            fractionalSeconds constructor args.

         Timespan( <string n seconds>, [exponent=<multiplier>] )

            Like the float constructor, but allows for exact number
            representation rather than floating point noise.

         Timespan( <int n seconds>,
                   <int m fractional_seconds>, [frac_exponent=<multiplier>] )

            Constructs a timespan using whole seconds and separate fractional
            seconds both represented as integers.  The default exponent for
            fractional seconds is nanoseconds, but if frac_exponent is specified,
            will be in frac_exponent.

      A Timespan also supports __add__(), __sub__(), __eq__(), __lt__(),
      __gt__() which should work "as expected".


   Timestamp

      Timestamp inherits from Timespan and adds a restriction that it cannot be
      negative, since it represents a moment in time.


Other useful constants are:

   seconds, milliseconds, microseconds, nanoseconds, picoseconds,
   femtoseconds, attoseconds, zeptoseconds, yoctoseconds

      These can be used as values to the "exponent" or "frac_exponent" kwargs when
      constructing a Timestamp or Timespan.  Their values are the
      multiplication factor corresponding to the metric prefix they represent.
      For example, nanoseconds is 1e-9.

Examples:
>>> from hightime import *

>>> print Hightime( 22 )
22s

>>> print Hightime( 22.23 )
22s 230ms

>>> print Hightime( 22.23, exponent=microseconds )
0s 22230ns

>>> print Hightime( 22.23, exponent=microseconds ) + 12345e6
12345000000s 22230ns

>>> print Hightime( 22.23, exponent=microseconds ) + 12345.1
12345s 100022230ns

>>> print Hightime( time.time() )
1504804266s 472007036209ps

>>> print Hightime( 1234567890, 123456789 )
1234567890s 123456789ns

>>> print Hightime( 0, 1000000000 )
1s 0ns

>>> print Hightime( 1, 2222222222 )
3s 222222222ns

>>> print Hightime( "9" * 99, exponent=yoctoseconds )
999999999999999999999999999999999999999999999999999999999999999999999999999s 999999999999999999999999000e-27s

>>> delta_t = Hightime( 22.23 ) - Hightime( 0.1 )
>>> delta_t
<hightimedelta.TimeDelta object at 0x7f682e322cd0>
>>> print delta_t
22s 130ms

"""

from .highdatetime import DateTime  # noqa: F401
from .hightimedelta import TimeDelta  # noqa: F401
from .sitimeunit import SITimeUnit  # noqa: F401
