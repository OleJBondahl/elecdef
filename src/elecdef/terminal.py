"""The TerminalBlock block and its Level: a terminal's levels and the pins they give."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._product import Symbol
from elecdef._quantity import Kind, Quantity
from elecdef._range import Range
from elecdef._rating import Rating
from elecdef.pins import Link, LinkKind, Pin, PinRole, Side
from elecdef.vocab import LevelKind, Potential, Rail

__all__ = ["Level"]

_TWO_SIDED = (LevelKind.FUSE, LevelKind.DISCONNECT)
_ROLE = {
    Potential.PE: PinRole.PE,
    Potential.PEN: PinRole.PE,
    Potential.SIGNAL: PinRole.SIGNAL,
}


@dataclass(frozen=True)
class Level:
    """One level of a terminal: its marking, the potential it carries and its kind."""

    marking: str
    potential: Potential
    kind: LevelKind

    def __post_init__(self) -> None:
        """Refuse a marking that is not a str."""
        if not isinstance(self.marking, str):
            message = f"marking is a str, not {type(self.marking).__name__}"
            raise TypeError(message)

    @property
    def pins(self) -> tuple[Pin, ...]:
        """One pin, or for a fuse or disconnect level the pin on side A and `marking'` on B."""
        role = _ROLE.get(self.potential, PinRole.SUPPLY)
        if self.kind not in _TWO_SIDED:
            return (Pin(self.marking, role),)
        return (Pin(self.marking, role, Side.A), Pin(f"{self.marking}'", role, Side.B))

    @property
    def links(self) -> tuple[Link, ...]:
        """The join of a two-sided level: protective for a fuse, switched and closed otherwise."""
        if self.kind not in _TWO_SIDED:
            return ()
        pair = (self.marking, f"{self.marking}'")
        if self.kind is LevelKind.FUSE:
            return (Link(pair, LinkKind.PROTECTIVE),)
        return (Link(pair, LinkKind.SWITCHED, closed_at_rest=True),)


@dataclass(frozen=True)
class TerminalBlock(Block):
    """A terminal block: its levels, the connection on each side and its mounting.

    Pins are computed from the levels on every read.
    """

    needs: ClassVar[tuple[str, ...]] = ("levels",)

    kind: LevelKind | None = None
    levels: tuple[Level, ...] = ()
    sides: tuple[Connection, ...] = ()
    cross_section: Quantity | None = figure(Kind.AREA)
    short_time_current: Range | None = figure(Kind.CURRENT)
    width: Quantity | None = figure(Kind.LENGTH)
    rail: Rail | None = None
    rating: Rating | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The pins of every level, in level order."""
        return tuple(pin for level in self.levels for pin in level.pins)

    @property
    def links(self) -> tuple[Link, ...]:
        """The links of every level, in level order."""
        return tuple(link for level in self.levels for link in level.links)
