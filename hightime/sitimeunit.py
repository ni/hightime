from enum import IntEnum


class SITimeUnit(IntEnum):
    # prefixes from https://physics.nist.gov/cuu/Units/prefixes.html
    SECONDS = 0
    MILLISECONDS = -3
    MICROSECONDS = -6
    NANOSECONDS = -9
    PICOSECONDS = -12
    FEMTOSECONDS = -15
    ATTOSECONDS = -18
    ZEPTOSECONDS = -21
    YOCTOSECONDS = -24
