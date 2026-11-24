"""The side of a part a marking states."""

from elecdef._pinorder import line_number, marking_key
from elecdef.pins import Side

_COIL_SIDES = {"A1": Side.A, "A2": Side.B}


def pin_side(marking: str) -> Side | None:
    """The side a marking states: odd numbers and a coil's `A1` are side A, even ones and `A2` B.

    Any other marking states none.
    """
    if marking in _COIL_SIDES:
        return _COIL_SIDES[marking]
    key = marking_key(marking)
    if len(key) == 1 and key[0][0] == 0:
        return Side.A if line_number(key[0][1]) else Side.B
    return None
