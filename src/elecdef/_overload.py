"""The Overload block: a motor protection relay whose pins come from its poles and auxiliaries."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._contact import Contact
from elecdef._product import Symbol
from elecdef._quantity import Kind
from elecdef._range import Range
from elecdef._relay import _joined, _numbered
from elecdef.pins import Link, LinkKind, Marking, Pin, contact_pins
from elecdef.vocab import ContactForm, Reset, TripClass

__all__ = ["Overload"]

_MAX_POLES = 9


def _main(poles: int | None) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
    """The main pins `1/L1 2/T1 ...` of `poles` poles, each pole joined by a conductive link."""
    if poles is None:
        return (), ()
    if not isinstance(poles, int) or isinstance(poles, bool) or not 1 <= poles <= _MAX_POLES:
        message = "poles is an int from 1 to 9"
        raise TypeError(message)
    pins: tuple[Pin, ...] = ()
    links: tuple[Link, ...] = ()
    for pole in range(1, poles + 1):
        pair = contact_pins(ContactForm.MAKE, pole, Marking.MAIN)[0]
        pins += pair
        links += (Link((pair[0].marking, pair[1].marking), LinkKind.CONDUCTIVE),)
    return pins, links


@dataclass(frozen=True)
class Overload(Block):
    """A motor overload relay: main pins per pole, then auxiliaries numbered OVERLOAD.

    Pins and links are computed on every read, so `replace(overload, poles=2)` leaves none stale.
    """

    needs: ClassVar[tuple[str, ...]] = ("setting",)

    poles: int | None = None
    setting: Range | None = figure(Kind.CURRENT)
    trip_class: TripClass | None = None
    reset: Reset | None = None
    phase_failure: bool = False
    aux: tuple[Contact, ...] = ()
    connection: Connection | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Check the figures and that setting is a Range, then read the pins once."""
        super().__post_init__()
        if self.setting is not None and not isinstance(self.setting, Range):
            message = f"setting is a Range, not {type(self.setting).__name__}"
            raise TypeError(message)
        _ = self.pins

    def _joined(self) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
        """The main pins and links, then those of the auxiliaries."""
        main_pins, main_links = _main(self.poles)
        pins, links = _joined(None, _numbered(self.aux, Marking.OVERLOAD))
        return main_pins + pins, main_links + links

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The main pins, then the pins of each auxiliary contact."""
        return self._joined()[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """The conductive main links, then the links of the auxiliaries."""
        return self._joined()[1]
