"""The SupplyInput block: what a powered thing draws, and its supply pins."""

from dataclasses import dataclass

from elecdef._block import Block, figure
from elecdef._connection import Connection
from elecdef._quantity import Kind
from elecdef._range import Ranges
from elecdef.pins import Pin, PinRole

__all__ = ["SupplyInput"]

_SUPPLY_PINS = (Pin("+", PinRole.PLUS), Pin("-", PinRole.MINUS))


@dataclass(frozen=True)
class SupplyInput(Block):
    """What a powered thing draws: voltage and current per conditions, and its supply pins.

    The pins default to a plus and a minus; a connection is unfilled until a leaf states one.
    """

    voltage: Ranges = figure(Kind.VOLTAGE, many=True)
    current: Ranges = figure(Kind.CURRENT, many=True)
    pins: tuple[Pin, ...] = _SUPPLY_PINS
    connection: Connection | None = None
