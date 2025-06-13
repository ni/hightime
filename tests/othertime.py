from __future__ import annotations

import datetime
from functools import total_ordering

import hightime


@total_ordering
class OtherDateTime:
    """Another datetime class that supports comparisons with hightime.datetime."""

    def __init__(self, timestamp: float) -> None:
        """Initialize the OtherDateTime."""
        self._timestamp = timestamp

    def __eq__(self, value: object, /) -> bool:
        """Return self==value."""
        if isinstance(value, OtherDateTime):
            return self._timestamp == value._timestamp
        elif isinstance(value, (datetime.datetime, hightime.datetime)):
            return self._timestamp == value.timestamp()
        else:
            return NotImplemented

    def __lt__(self, value: OtherDateTime | datetime.datetime | hightime.datetime, /) -> bool:
        """Return self<value."""
        if isinstance(value, OtherDateTime):
            return self._timestamp < value._timestamp
        elif isinstance(value, (datetime.datetime, hightime.datetime)):
            return self._timestamp < value.timestamp()
        else:
            return NotImplemented  # type: ignore[unreachable]

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"{self.__class__.__name__}({self._timestamp})"


@total_ordering
class OtherTimeDelta:
    """Another timedelta class that supports comparisons with hightime.timedelta."""

    def __init__(self, seconds: float) -> None:
        """Initialize the OtherTimeDelta."""
        self._seconds = seconds

    def __eq__(self, value: object, /) -> bool:
        """Return self==value."""
        if isinstance(value, OtherTimeDelta):
            return self._seconds == value._seconds
        elif isinstance(value, (datetime.timedelta, hightime.timedelta)):
            return self._seconds == value.total_seconds()
        else:
            return NotImplemented

    def __lt__(self, value: OtherTimeDelta | datetime.timedelta | hightime.timedelta, /) -> bool:
        """Return self<value."""
        if isinstance(value, OtherTimeDelta):
            return self._seconds < value._seconds
        elif isinstance(value, (datetime.timedelta, hightime.timedelta)):
            return self._seconds < value.total_seconds()
        else:
            return NotImplemented  # type: ignore[unreachable]

    def __repr__(self) -> str:
        """Return repr(self)."""
        return f"{self.__class__.__name__}({self._seconds})"
