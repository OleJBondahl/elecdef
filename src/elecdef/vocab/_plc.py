"""PLC channel, card and bus vocabularies."""

from elecdef.vocab._base import Vocab


class Signal(Vocab):
    """The signal kind of a channel."""

    DI = ""
    DO = ""
    AI_CURRENT = ""
    AI_VOLTAGE = ""
    AO_CURRENT = ""
    AO_VOLTAGE = ""
    RTD = ""
    TC = ""
    RELAY = ""


class DiType(Vocab):
    """The digital input type."""

    T1 = ""
    T2 = ""
    T3 = ""


class Polarity(Vocab):
    """The digital channel polarity."""

    SINKING = "input sinks current"
    SOURCING = "input sources current"
    EITHER = ""


class OutputKind(Vocab):
    """The digital output stage."""

    TRANSISTOR = ""
    RELAY = ""
    TRIAC = ""


class RtdType(Vocab):
    """The resistance thermometer type."""

    PT100 = ""
    PT1000 = ""
    NI100 = ""


class ThermocoupleType(Vocab):
    """The thermocouple type letter."""

    J = ""
    K = ""
    N = ""
    T = ""
    E = ""


class CardForm(Vocab):
    """The build form of a card."""

    COMPACT = "fixed set of channels"
    MODULAR = "built from plug-in cards"


class CardRole(Vocab):
    """The role of a card in a station."""

    CONTROLLER = ""
    COUPLER = ""
    IO = ""


class Bus(Vocab):
    """The field or network bus."""

    ETHERCAT = ""
    PROFINET = ""
    PROFIBUS = ""
    CANOPEN = ""
    MODBUS_TCP = ""
    MODBUS_RTU = ""
    ETHERNET_IP = ""
    IO_LINK = ""


class Sil(Vocab):
    """The safety integrity level."""

    SIL_1 = ""
    SIL_2 = ""
    SIL_3 = ""


class Pl(Vocab):
    """The performance level."""

    PL_A = ""
    PL_B = ""
    PL_C = ""
    PL_D = ""
    PL_E = ""
