"""The Device block: pins and links given outright, the typed fallback for a thing with no block."""

from dataclasses import dataclass

from elecdef._block import Block
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._product import Symbol
from elecdef._rating import Rating
from elecdef.pins import Link, Pin

__all__ = ["Device"]


@dataclass(frozen=True)
class Device(Block):
    """A thing with no block of its own yet: its pins and links are stored as given.

    Every field is unfilled by default.
    """

    pins: tuple[Pin, ...] = ()
    links: tuple[Link, ...] = ()
    rating: Rating | None = None
    connection: Connection | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Refuse pins or links that are not a tuple of Pin or Link."""
        super().__post_init__()
        for name, kind in (("pins", Pin), ("links", Link)):
            value = getattr(self, name)
            if not (isinstance(value, tuple) and all(isinstance(each, kind) for each in value)):
                message = f"{name} is a tuple of {kind.__name__}"
                raise TypeError(message)
