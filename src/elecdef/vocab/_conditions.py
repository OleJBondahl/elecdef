"""Conditions a figure holds under: current kind, utilisation, coil state, conductor kind."""

from elecdef.vocab._base import Vocab


class Current(Vocab):
    """The current kind a figure is stated for."""

    AC = "alternating current"
    DC = "direct current"


class Utilisation(Vocab):
    """The utilisation code a contact rating is stated for."""

    AC_1 = ""
    AC_2 = ""
    AC_3 = ""
    AC_3E = ""
    AC_4 = ""
    AC_5A = ""
    AC_5B = ""
    AC_6A = ""
    AC_6B = ""
    AC_12 = ""
    AC_13 = ""
    AC_14 = ""
    AC_15 = ""
    DC_1 = ""
    DC_3 = ""
    DC_5 = ""
    DC_6 = ""
    DC_12 = ""
    DC_13 = ""
    DC_14 = ""


class CoilState(Vocab):
    """The state of a coil a figure is stated for."""

    INRUSH = "while the coil pulls in"
    HOLD = "once the coil is held"


class ConductorKind(Vocab):
    """The construction of a conductor a terminal range is stated for."""

    SOLID = "one solid wire"
    STRANDED = "many wires twisted together"
    FINE = "many fine wires"
    FINE_FERRULE = "many fine wires in a ferrule"
