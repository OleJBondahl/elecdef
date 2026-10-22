"""The Connector block: a plug or socket family, its poles and its numbered pins."""

from dataclasses import dataclass

from elecdef._block import Block
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._product import Symbol
from elecdef._rating import Rating
from elecdef.pins import Link, Pin, PinRole
from elecdef.vocab import Coding, ConnectorFamily, Gender, Locking

__all__ = ["Connector"]


@dataclass(frozen=True)
class Connector(Block):
    """A connector: family, coding, poles, gender, locking and whether it is shielded.

    Pins `1..poles` are computed on every read. Every field is unfilled by default.
    """

    family: ConnectorFamily | None = None
    coding: Coding | None = None
    poles: int | None = None
    gender: Gender | None = None
    locking: Locking | None = None
    shielded: bool = False
    rating: Rating | None = None
    connection: Connection | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Refuse poles that are not a positive int, and a shielded that is not a bool."""
        super().__post_init__()
        poles = self.poles
        if poles is not None and (
            not isinstance(poles, int) or isinstance(poles, bool) or poles < 1
        ):
            message = f"poles is a positive int, not {poles!r}"
            raise TypeError(message)
        if not isinstance(self.shielded, bool):
            message = f"shielded is a bool, not {type(self.shielded).__name__}"
            raise TypeError(message)

    @property
    def pins(self) -> tuple[Pin, ...]:
        """Pins `1..poles`, each a signal pin; none while poles is unfilled."""
        return tuple(Pin(str(n), PinRole.SIGNAL) for n in range(1, (self.poles or 0) + 1))

    @property
    def links(self) -> tuple[Link, ...]:
        """A connector joins nothing inside itself."""
        return ()
