import sys

from .sitimeunit import SITimeUnit

isPython3Compat = (sys.version_info.major == 3)
isPython36Compat = (isPython3Compat and (sys.version_info.minor >= 6))


def normalize_frac_seconds(a, b):
    """Returns 3-tuple containing (normalized frac_seconds for a, normalized
    frac_seconds for b, most precise (smallest) frac_seconds_exponent between
    both), where "normalized" is the frac_seconds multiplied to be equalivent
    under the more precise frac_seconds_exponent.
    Ex. a.frac_seconds = 10
        a.frac_seconds_exponent = -1
        b.frac_seconds = 12
        b.frac_seconds_exponent = -2
        returns: (100, 12, -2)
    """
    # Lots of code to handle singular "second" as used in datetime and
    # DateTime, and plural "seconds" as used in timedelta and
    # TimeDelta...

    if hasattr(a, "frac_second") and hasattr(a, "frac_second_exponent"):
        a_frac_seconds = a.frac_second
        a_frac_seconds_exponent = a.frac_second_exponent
    elif hasattr(a, "frac_seconds") and hasattr(a, "frac_seconds_exponent"):
        a_frac_seconds = a.frac_seconds
        a_frac_seconds_exponent = a.frac_seconds_exponent
    elif hasattr(a, "microsecond"):
        a_frac_seconds = a.microsecond
        a_frac_seconds_exponent = SITimeUnit.MICROSECONDS
    elif hasattr(a, "microseconds"):
        a_frac_seconds = a.microseconds
        a_frac_seconds_exponent = SITimeUnit.MICROSECONDS
    else:
        raise TypeError("invalid type for a: %s" % type(a))

    if hasattr(b, "frac_second") and hasattr(b, "frac_second_exponent"):
        b_frac_seconds = b.frac_second
        b_frac_seconds_exponent = b.frac_second_exponent
    elif hasattr(b, "frac_seconds") and hasattr(b, "frac_seconds_exponent"):
        b_frac_seconds = b.frac_seconds
        b_frac_seconds_exponent = b.frac_seconds_exponent
    elif hasattr(b, "microsecond"):
        b_frac_seconds = b.microsecond
        b_frac_seconds_exponent = SITimeUnit.MICROSECONDS
    elif hasattr(b, "microseconds"):
        b_frac_seconds = b.microseconds
        b_frac_seconds_exponent = SITimeUnit.MICROSECONDS
    else:
        raise TypeError("invalid type for b: %s" % type(b))

    if a_frac_seconds_exponent == b_frac_seconds_exponent:
        return (a_frac_seconds, b_frac_seconds,
                a_frac_seconds_exponent)

    multiplier = 10 ** (abs(a_frac_seconds_exponent -
                            b_frac_seconds_exponent))
    # a is more precise, multiply b
    if a_frac_seconds_exponent < b_frac_seconds_exponent:
        return (a_frac_seconds, b_frac_seconds * multiplier,
                a_frac_seconds_exponent)
    # b is more precise, multiply a
    else:
        return (a_frac_seconds * multiplier, b_frac_seconds,
                b_frac_seconds_exponent)


def get_subsecond_component(frac_seconds, frac_seconds_exponent,
                            subsec_component_exponent, upper_exponent_limit):
    """Return the number of subseconds from frac_seconds *
    (10**frac_seconds_exponent) corresponding to subsec_component_exponent that
    does not exceed upper_exponent_limit.

    For example:
    If frac_seconds*(10**frac_seconds_exponent) is 0.1234567,
    upper_exponent_limit is SITimeUnit.SECONDS, and subsec_component_exponent is
    SITimeUnit.MICROSECONDS, 123456 would be returned.

    If frac_seconds*(10**frac_seconds_exponent) is 0.123456789,
    upper_exponent_limit is SITimeUnit.MICROSECONDS, and
    subsec_component_exponent is SITimeUnit.NANOSECONDS, 789 would be returned.

    Same example as above, but with upper_exponent_limit = SITimeUnit.SECONDS,
    123456789 would be returned.
    """
    total_subsecs = int(frac_seconds * (10 ** (frac_seconds_exponent -
                                               subsec_component_exponent)))
    return total_subsecs % (10 ** abs(subsec_component_exponent -
                                      upper_exponent_limit))
