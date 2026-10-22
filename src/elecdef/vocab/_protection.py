"""Protection and supply vocabularies."""

from elecdef.vocab._base import Vocab


class FuseSystem(Vocab):
    """The fuse construction system."""

    NH = ""
    D = ""
    D0 = ""
    CYLINDRICAL = ""
    BLADE = ""
    MINIATURE = ""


class FuseClass(Vocab):
    """The fuse operating class, as typed on the fuse."""

    gG = ""  # noqa: N815 - names as typed on the fuse
    gL = ""  # noqa: N815 - names as typed on the fuse
    aM = ""  # noqa: N815 - names as typed on the fuse
    aR = ""  # noqa: N815 - names as typed on the fuse
    gR = ""  # noqa: N815 - names as typed on the fuse
    gS = ""  # noqa: N815 - names as typed on the fuse
    gPV = ""  # noqa: N815 - names as typed on the fuse


class FuseSpeed(Vocab):
    """The fuse speed letters."""

    FF = ""
    F = ""
    M = ""
    T = ""
    TT = ""


class TripCurve(Vocab):
    """The breaker trip curve letter."""

    A = ""
    B = ""
    C = ""
    D = ""
    E = ""
    K = ""
    Z = ""


class TripClass(Vocab):
    """The motor protection trip class."""

    C10A = ""
    C10 = ""
    C20 = ""
    C30 = ""


class Reset(Vocab):
    """How a protective device is reset."""

    MANUAL = "reset by hand"
    AUTO = "resets by itself"
    BOTH = ""


class PsuKind(Vocab):
    """The kind of power supply."""

    AC_DC = ""
    DC_DC = ""
    RECTIFIER = ""
    TRANSFORMER = ""
    UPS = ""


class OverloadBehaviour(Vocab):
    """How a supply behaves on overload."""

    CONSTANT = ""
    LATCHING = ""
    HICCUP = ""


class CircuitClass(Vocab):
    """The protective class of a circuit."""

    SELV = ""
    PELV = ""
    ELV = ""
    CLASS_2 = ""
    LPS = ""
