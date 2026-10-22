"""Terminal level, connector and port vocabularies."""

from elecdef.vocab._base import Vocab


class LevelKind(Vocab):
    """The kind of a terminal level."""

    FEED_THROUGH = ""
    PE = ""
    PEN = ""
    FUSE = ""
    DISCONNECT = ""
    BRIDGE = ""
    INSTALLATION = ""
    SENSOR_ACTUATOR = ""
    PCB = ""


class Potential(Vocab):
    """The potential a level carries."""

    L = ""
    N = ""
    PE = ""
    PEN = ""
    SIGNAL = ""
    OTHER = ""


class Rail(Vocab):
    """The mounting rail kind."""

    DIN_35 = "35 mm top-hat rail"
    DIN_15 = "15 mm rail"
    NONE = "no rail"


class ConnectorFamily(Vocab):
    """The connector family."""

    M8 = ""
    M12 = ""
    D_SUB = ""
    RJ45 = ""
    MICRO_FIT = ""


class Coding(Vocab):
    """The connector coding key."""

    A = ""
    B = ""
    C = ""
    D = ""
    X = ""
    K = ""
    M = ""


class Gender(Vocab):
    """The connector gender."""

    MALE = "pins"
    FEMALE = "sockets"
    GENDERLESS = "mates with its own kind"


class Locking(Vocab):
    """How a connector locks."""

    NONE = ""
    SCREW = ""
    SNAP = ""
    BAYONET = ""
    PUSH_PULL = ""


class PortKind(Vocab):
    """The kind of a data port."""

    ETHERNET = ""
    USB = ""
    SERIAL = ""
    DISPLAY = ""
