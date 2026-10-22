"""The Coil block: the drive of a relay or contactor, with its A1 and A2 pins."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._connection import Connection
from elecdef._product import Symbol
from elecdef._quantity import Kind
from elecdef._range import Range, Ranges
from elecdef.pins import Link, Pin, PinRole
from elecdef.vocab import CoilKind, Suppression

__all__ = ["Coil"]


@dataclass(frozen=True)
class Coil(Block):
    """One coil: kind, drive figures, suppression, and the pins computed from kind and suppression.

    `own_pins` holds only pins the author gave; with none, `pins` is A1 and A2 read on every access.
    """

    needs: ClassVar[tuple[str, ...]] = ("voltage",)

    kind: CoilKind | None = None
    voltage: Ranges = figure(Kind.VOLTAGE, many=True)
    pick_up: Range | None = figure(Kind.RATIO)
    drop_out: Range | None = figure(Kind.RATIO)
    resistance: Range | None = figure(Kind.RESISTANCE)
    power: Ranges = figure(Kind.POWER, many=True)
    apparent_power: Ranges = figure(Kind.APPARENT_POWER, many=True)
    operate_time: Range | None = figure(Kind.TIME)
    release_time: Range | None = figure(Kind.TIME)
    suppression: Suppression | None = None
    connection: Connection | None = None
    own_pins: tuple[Pin, ...] = ()
    symbol: Symbol | None = None

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The author's `own_pins`, else A1 and A2 (PLUS and MINUS for a DC coil with a diode)."""
        if self.own_pins:
            return self.own_pins
        polar = self.kind is CoilKind.DC and self.suppression is Suppression.DIODE
        first, second = (PinRole.PLUS, PinRole.MINUS) if polar else (PinRole.COIL, PinRole.COIL)
        return Pin("A1", first), Pin("A2", second)

    @property
    def links(self) -> tuple[Link, ...]:
        """A coil joins no pins."""
        return ()
