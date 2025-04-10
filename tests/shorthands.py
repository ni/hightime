from typing import Any

import hightime

_UNIT_SHORTHANDS = {
    "y": "year",
    "mo": "month",
    "w": "week",
    "d": "day",
    "h": "hour",
    "m": "minute",
    "s": "second",
    "ms": "millisecond",
    "us": "microsecond",
    "ns": "nanosecond",
    "ps": "picosecond",
    "fs": "femtosecond",
    # Underscore to avoid conflict with keyword
    "as_": "attosecond",
    "zs": "zeptosecond",
    "ys": "yoctosecond",
}


def _replace(kwargs: dict[str, Any], *, plural: bool) -> dict[str, Any]:
    for shorthand, longhand in _UNIT_SHORTHANDS.items():
        if shorthand in kwargs:
            kwargs[longhand + ("s" if plural else "")] = kwargs.pop(shorthand)

    return kwargs


def datetime(*args: Any, **kwargs: Any) -> hightime.datetime:
    """Instantiate a hightime.datetime with some shorthands.

    Allows unit shorthand kwargs as well as passing year/month/day if none are provided
    """

    _replace(kwargs, plural=False)
    if len(args) < 3:
        kwargs.setdefault("day", 21)
    if len(args) < 2:
        kwargs.setdefault("month", 4)
    if len(args) < 1:
        kwargs.setdefault("year", 2020)
    return hightime.datetime(*args, **kwargs)


def timedelta(*args: Any, **kwargs: Any) -> hightime.timedelta:
    """Instantiate a hightime.timedelta, allowing unit shorthand kwargs"""

    _replace(kwargs, plural=True)
    return hightime.timedelta(*args, **kwargs)
