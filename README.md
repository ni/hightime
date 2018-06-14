Hightime
========

Overview
--------
Hightime allows for virtually infinite sub-second precision by providing API-compatible replacements for datetime.datetime (hightime.DateTime) and datetime.timedelta (hightime.TimeDelta).

Installation
------------
Hightime can be installed by cloning the master branch and then in a command
line in the directory of setup.py run:

```bash
pip install --pre .
```

Or by installing from PyPI using:

```bash
pip install hightime
```

Examples
--------

```python
>>> from hightime import DateTime, TimeDelta, SITimeUnit

>>> now = DateTime.now()

>>> print(now)
2018-05-06 19:53:14.170736

>>> increment = TimeDelta(frac_seconds=135, frac_seconds_exponent=-13)

>>> print(increment)
0:00:00+135e-13

>>> later = now + increment

>>> print(later)
2018-05-06 19:53:14+1707360000135e-13

>>> later += increment

>>> print(later)
2018-05-06 19:53:14+1707360000270e-13

>>> print(later + now)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unsupported operand type(s) for +: 'DateTime' and 'DateTime'

>>> print(later - now)
0:00:00+270e-13

>>> print(increment * 2)
0:00:00+270e-13

>>> later += timedelta(microseconds=3)

>>> print(later)
2018-05-06 19:53:14+1707390000270e-13

>>> later += TimeDelta(frac_seconds=2, frac_seconds_exponent=SITimeUnit.ATTOSECONDS)

>>> print(later)
2018-05-06 19:53:14+170739000027000002e-18

>>> print(later - now)
0:00:00+3000027000002e-18
```

See the [readthedocs page](http://hightime.readthedocs.io/en/latest/) for more detailed examples and documentation.

License
-------
Hightime is licensed under an MIT-style license.

See [LICENSE](https://github.com/ni/hightime/blob/master/LICENSE)
for details about how hightime is licensed.

Other incorporated projects may be licensed under different licenses. All
licenses allow for non-commercial and commercial use.
