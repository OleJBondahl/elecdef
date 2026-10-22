"""Coil, relay and actuator vocabularies."""

from elecdef.vocab._base import Vocab


class CoilKind(Vocab):
    """The drive kind of a coil."""

    AC = "alternating current coil"
    DC = "direct current coil"
    AC_DC = ""
    ECONOMISER = ""
    LATCHING = ""


class Suppression(Vocab):
    """How a coil is suppressed against switch-off spikes."""

    NONE = "no suppression"
    DIODE = "flyback diode"
    RC = "resistor and capacitor"
    VARISTOR = "voltage-dependent resistor"


class RelayKind(Vocab):
    """The kind of relay."""

    ELECTROMECHANICAL = ""
    SOLID_STATE = ""
    TIMER = ""


class TimerFunction(Vocab):
    """The function of a timing relay."""

    ON_DELAY = ""
    OFF_DELAY = ""
    ON_OFF_DELAY = ""
    FLASHING = ""
    PULSE = ""


class ActuatorKind(Vocab):
    """The kind of operating head."""

    NONE = ""
    PUSH = ""
    MUSHROOM = ""
    TURN = ""
    KEY = ""
    POSITION = ""
    PULL = ""
    FOOT = ""
