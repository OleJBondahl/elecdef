"""The Breaker block: pole pins as a fuse holder has them, then auxiliaries numbered AUX."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._contact import Contact
from elecdef._product import Symbol
from elecdef._quantity import Kind
from elecdef._range import Range
from elecdef._rating import Rating
from elecdef._relay import _joined, _numbered
from elecdef.fuse import pole_pins
from elecdef.pins import Link, Marking, Pin
from elecdef.vocab import TripCurve

__all__ = ["Breaker"]


@dataclass(frozen=True)
class Breaker(Block):
    """A circuit breaker: current, trip curve and breaking capacities, pole pins, auxiliaries.

    Pins and links are computed on every read, so `replace(breaker, poles=1)` leaves none stale.
    """

    needs: ClassVar[tuple[str, ...]] = ("current", "curve")

    poles: int | None = None
    current: Range | None = figure(Kind.CURRENT)
    curve: TripCurve | None = None
    icn: Range | None = figure(Kind.CURRENT)
    icu: Range | None = figure(Kind.CURRENT)
    ics: Range | None = figure(Kind.CURRENT)
    rating: Rating | None = None
    aux: tuple[Contact, ...] = ()
    connection: Connection | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Check the figures, then read the pins once so a bad pole count fails here."""
        super().__post_init__()
        _ = self.pins

    def _joined(self) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
        """The pole pins and links, then those of the auxiliaries."""
        pole_p, pole_l = pole_pins(self.poles)
        pins, links = _joined(None, _numbered(self.aux, Marking.AUX))
        return pole_p + pins, pole_l + links

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The pole pins, then the pins of each auxiliary contact."""
        return self._joined()[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """One protective link per pole, then the links of the auxiliaries."""
        return self._joined()[1]
