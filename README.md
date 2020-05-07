# Hightime

## Overview

Hightime allows for up to yoctosecond precision replacements for the datetime datetime
and timedelta types.

## Installation

Hightime can be installed by cloning the master branch and then in a command
line in the directory of setup.py run:

```bash
pip install --pre .
```

Or by installing from PyPI using:

```bash
pip install hightime
```

## Examples

```python
>>> from hightime import datetime
>>> from hightime import timedelta

>>> high_noon = datetime(
...   year=1952,
...   month=7,
...   day=24,
...   hour=12,
...   minute=0,
...   second=30,
...   microsecond=0,
... )

>>> print(high_noon)
1952-07-24 12:00:30

>>> hesitation = timedelta(microseconds=10, femtoseconds=203456)

>>> print(hesitation)
0:00:00.000010000203456

>>> reaction = high_noon + hesitation

>>> print(reaction)
1952-07-24 12:00:30.000010000203456

>>> print(high_noon + high_noon)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unsupported operand type(s) for +: 'datetime' and 'datetime'

>>> print(hesitation * 2)
0:00:00.000020000406912

```

See the [readthedocs page](http://hightime.readthedocs.io/en/latest/) for more detailed
examples and documentation.

## License

Hightime is licensed under an MIT-style license.

See [LICENSE](https://github.com/ni/hightime/blob/master/LICENSE)
for details about how hightime is licensed.

Other incorporated projects may be licensed under different licenses. All
licenses allow for non-commercial and commercial use.
