"""Relay, Contactor and ContactBlock: composites whose pins come from their contacts and coil."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block
from elecdef._body import Body
from elecdef._coil import Coil
from elecdef._contact import Contact
from elecdef._numbering import _joined, _numbered
from elecdef._product import Symbol
from elecdef._rating import Rating
from elecdef.pins import Link, Marking, Pin
from elecdef.vocab import ActuatorKind, ContactForm, RelayKind, TimerFunction

__all__ = ["ContactBlock", "Contactor", "Relay"]


@dataclass(frozen=True)
class Relay(Block):
    """A relay: a coil and contacts numbered 1..n on every read (the timer scheme for a timer).

    It owns no pin and no symbol of its own, so it has no connection.
    """

    needs: ClassVar[tuple[str, ...]] = ("contacts",)

    kind: RelayKind | None = None
    coil: Coil | None = None
    contacts: tuple[Contact, ...] = ()
    latching: bool = False
    force_guided: bool = False
    timer_function: TimerFunction | None = None
    body: Body | None = None

    def __post_init__(self) -> None:
        """Check the figures, then read the pins once so a number out of range fails here."""
        super().__post_init__()
        _ = self.pins

    def _joined(self) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
        """The pins and links with the contacts numbered for the relay's kind."""
        scheme = Marking.TIMER if self.kind is RelayKind.TIMER else Marking.AUX
        return _joined(self.coil, _numbered(self.contacts, scheme))

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The coil pins, then the pins of each contact."""
        return self._joined()[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """The links of the contacts."""
        return self._joined()[1]


@dataclass(frozen=True)
class Contactor(Block):
    """A contactor: a coil, MAKE main contacts numbered MAIN 1..n, then auxiliaries AUX 1..n.

    A mirror contact is an auxiliary whose features hold `ContactFeature.MIRROR`.
    """

    coil: Coil | None = None
    main: tuple[Contact, ...] = ()
    aux: tuple[Contact, ...] = ()
    rating: Rating | None = None
    body: Body | None = None

    def __post_init__(self) -> None:
        """Refuse a main contact that is not a MAKE, then read the pins once."""
        super().__post_init__()
        if any(contact.form is not ContactForm.MAKE for contact in self.main):
            message = "a main contact is a MAKE contact"
            raise TypeError(message)
        _ = self.pins

    def _joined(self) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
        """The pins and links with main and auxiliary contacts numbered by their schemes."""
        contacts = _numbered(self.main, Marking.MAIN) + _numbered(self.aux, Marking.AUX)
        return _joined(self.coil, contacts)

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The coil pins, the main pins, then the auxiliary pins."""
        return self._joined()[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """The links of the main and auxiliary contacts."""
        return self._joined()[1]


@dataclass(frozen=True)
class ContactBlock(Block):
    """A coil-less carrier of contacts numbered AUX from `numbered_from`."""

    contacts: tuple[Contact, ...] = ()
    numbered_from: int = 1
    actuator: ActuatorKind | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Check the figures, then read the pins once so a number out of range fails here."""
        super().__post_init__()
        _ = self.pins

    def _joined(self) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
        """The pins and links of the contacts numbered from `numbered_from`."""
        return _joined(None, _numbered(self.contacts, Marking.AUX, self.numbered_from))

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The pins of each contact."""
        return self._joined()[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """The links of the contacts."""
        return self._joined()[1]
