"""The PLC door: the signal blocks of a channel, the Channel itself and the ChannelGroup."""

from dataclasses import dataclass, replace

from elecdef._block import Block, figure
from elecdef._connection import Connection
from elecdef._contact import Contact
from elecdef._product import Symbol
from elecdef._quantity import Kind
from elecdef._range import Range, Ranges
from elecdef.pins import Pin, PinRole
from elecdef.vocab import DiType, OutputKind, Polarity, RtdType, Signal, ThermocoupleType

__all__ = ["AnalogIo", "Channel", "ChannelGroup", "DigitalInput", "DigitalOutput"]


@dataclass(frozen=True)
class DigitalInput(Block):
    """What a digital input channel accepts: its type, polarity, voltage, thresholds and filter.

    Every field is unfilled by default; the block holds no pin and no connection.
    """

    input_type: DiType | None = None
    polarity: Polarity | None = None
    voltage: Ranges = figure(Kind.VOLTAGE, many=True)
    off_max: Range | None = figure(Kind.VOLTAGE)
    on_min: Range | None = figure(Kind.VOLTAGE)
    current: Ranges = figure(Kind.CURRENT, many=True)
    filter_time: Range | None = figure(Kind.TIME)


@dataclass(frozen=True)
class DigitalOutput(Block):
    """What a digital output channel delivers: its stage, polarity and current.

    Every field is unfilled by default; the block holds no pin and no connection.
    """

    kind: OutputKind | None = None
    polarity: Polarity | None = None
    current: Ranges = figure(Kind.CURRENT, many=True)
    short_circuit_protected: bool | None = None


@dataclass(frozen=True)
class AnalogIo(Block):
    """An analog channel: a voltage or current span, resolution, wires, sensor type and accuracy.

    Every field is unfilled by default; the block holds no pin and no connection.
    """

    span: Range | None = figure(Kind.VOLTAGE, Kind.CURRENT)
    bits: int | None = None
    wires: int | None = None
    rtd: RtdType | None = None
    thermocouple: ThermocoupleType | None = None
    accuracy: Ranges = figure(Kind.RATIO, many=True)


_ELECTRICAL = (DigitalInput, DigitalOutput, AnalogIo, Contact)


@dataclass(frozen=True)
class Channel(Block):
    """One channel: its signal, number, electrical block and the pins it is wired on.

    A leaf like Device: the pins are stored as given. A group's template carries no number or pins.
    """

    signal: Signal | None = None
    number: int | None = None
    electrical: DigitalInput | DigitalOutput | AnalogIo | Contact | None = None
    pins: tuple[Pin, ...] = ()
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Refuse an electrical block of another type, or pins that are not a tuple of Pin."""
        super().__post_init__()
        if self.electrical is not None and not isinstance(self.electrical, _ELECTRICAL):
            message = "electrical is a DigitalInput, DigitalOutput, AnalogIo or Contact"
            raise TypeError(message)
        if not (isinstance(self.pins, tuple) and all(isinstance(p, Pin) for p in self.pins)):
            message = "pins is a tuple of Pin"
            raise TypeError(message)


@dataclass(frozen=True)
class ChannelGroup(Block):
    """Channels that share a template and a common: one per marking, numbered from `first`.

    `common` holds the markings of the group's common pins; every channel shares one `electrical`.
    """

    template: Channel | None = None
    markings: tuple[str, ...] = ()
    common: tuple[str, ...] = ()
    isolated: bool | None = None
    group_current: Range | None = figure(Kind.CURRENT)
    connection: Connection | None = None

    def __post_init__(self) -> None:
        """Refuse a template that is not a Channel, or markings that are not a tuple of str."""
        super().__post_init__()
        if self.template is not None and not isinstance(self.template, Channel):
            message = "template is a Channel"
            raise TypeError(message)
        if self.template is not None and (self.template.number is not None or self.template.pins):
            message = "a template channel carries no number or pins; the group numbers them"
            raise TypeError(message)
        for name in ("markings", "common"):
            value = getattr(self, name)
            if not (isinstance(value, tuple) and all(isinstance(each, str) for each in value)):
                message = f"{name} is a tuple of str"
                raise TypeError(message)

    def channels(self, first: int = 1) -> tuple[Channel, ...]:
        """The template copied once per marking, numbered from `first`, on a SIGNAL pin each."""
        if self.template is None:
            return ()
        return tuple(
            replace(self.template, number=number, pins=(Pin(marking, PinRole.SIGNAL),))
            for number, marking in enumerate(self.markings, first)
        )
