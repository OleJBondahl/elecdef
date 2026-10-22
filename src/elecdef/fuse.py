"""The Fuse block (top level) and the FuseHolder block: a fuse and its holder, with their pins."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._product import Symbol
from elecdef._quantity import Kind
from elecdef._range import Range, Ranges
from elecdef._rating import Rating
from elecdef.pins import Link, LinkKind, Pin, PinRole
from elecdef.vocab import FuseClass, FuseSpeed, FuseSystem

__all__ = ["FuseHolder"]


def pole_pins(poles: int | None) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
    """The pins `2p-1` (LINE) and `2p` (LOAD) per pole, each pole joined by a protective link."""
    if poles is None:
        return (), ()
    if not isinstance(poles, int) or isinstance(poles, bool) or poles < 1:
        message = "poles is an int of 1 or more"
        raise TypeError(message)
    pins: tuple[Pin, ...] = ()
    links: tuple[Link, ...] = ()
    for pole in range(1, poles + 1):
        line, load = str(2 * pole - 1), str(2 * pole)
        pins += (Pin(line, PinRole.LINE), Pin(load, PinRole.LOAD))
        links += (Link((line, load), LinkKind.PROTECTIVE),)
    return pins, links


@dataclass(frozen=True)
class Fuse(Block):
    """A fuse: system, class, current, voltage and breaking capacity, and its two pins.

    The pins are `1` (LINE) and `2` (LOAD), joined by a protective link.
    """

    needs: ClassVar[tuple[str, ...]] = ("current",)

    system: FuseSystem | None = None
    fuse_class: FuseClass | None = None
    current: Range | None = figure(Kind.CURRENT)
    voltage: Ranges = figure(Kind.VOLTAGE, many=True)
    breaking_capacity: Ranges = figure(Kind.CURRENT, many=True)
    speed: FuseSpeed | None = None
    indicator: bool = False
    connection: Connection | None = None
    symbol: Symbol | None = None

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The line pin `1` and the load pin `2`."""
        return pole_pins(1)[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """The protective link between the two pins."""
        return pole_pins(1)[1]


@dataclass(frozen=True)
class FuseHolder(Block):
    """A fuse holder: pins `2p-1` and `2p` per pole, each pole joined by a protective link."""

    system: FuseSystem | None = None
    poles: int | None = None
    disconnect: bool = False
    indicator: bool = False
    rating: Rating | None = None
    connection: Connection | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Check the figures, then read the pins once so a bad pole count fails here."""
        super().__post_init__()
        _ = self.pins

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The line and load pin of each pole."""
        return pole_pins(self.poles)[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """One protective link per pole."""
        return pole_pins(self.poles)[1]
