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

    @property
    def is_output(self) -> bool:
        """Whether the channel drives a field device: DO, RELAY and the analogue outputs."""
        return _FLAGS[self][0]

    @property
    def is_analogue(self) -> bool:
        """Whether the channel carries a value, not a state: the analogue, RTD and TC kinds."""
        return _FLAGS[self][1]


# (output, analogue) per signal; a member without a row fails the table test.
_FLAGS: dict[Signal, tuple[bool, bool]] = {
    Signal.DI: (False, False),
    Signal.DO: (True, False),
    Signal.AI_CURRENT: (False, True),
    Signal.AI_VOLTAGE: (False, True),
    Signal.AO_CURRENT: (True, True),
    Signal.AO_VOLTAGE: (True, True),
    Signal.RTD: (False, True),
    Signal.TC: (False, True),
    Signal.RELAY: (True, False),
}


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
