"""The Computer block and its Port: a supply plus one pin per data-port instance."""

from collections import Counter
from dataclasses import dataclass

from elecdef._block import Block, figure
from elecdef._body import Body
from elecdef._quantity import Kind
from elecdef._range import Range
from elecdef.connector import Connector
from elecdef.pins import Link, Pin, PinRole
from elecdef.supply import SupplyInput
from elecdef.vocab import PortKind

__all__ = ["Computer", "Port"]


@dataclass(frozen=True)
class Port:
    """A data port: its kind, how many there are and the connector it takes, if stated."""

    kind: PortKind
    count: int = 1
    connector: Connector | None = None

    def __post_init__(self) -> None:
        """Refuse a count that is not a positive int."""
        count = self.count
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            message = f"count is a positive int, not {count!r}"
            raise TypeError(message)


@dataclass(frozen=True)
class Computer(Block):
    """A computer: the supply it draws, its power and its data ports.

    Pins are the supply pins, then one `<KIND><n>` pin per port instance, numbered per kind.
    """

    supply: SupplyInput | None = None
    power: Range | None = figure(Kind.POWER)
    ports: tuple[Port, ...] = ()
    body: Body | None = None

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The supply pins first, then each port instance in port order."""
        supply = self.supply.pins if self.supply is not None else ()
        seen: Counter[PortKind] = Counter()
        ports: list[Pin] = []
        for port in self.ports:
            for _ in range(port.count):
                seen[port.kind] += 1
                ports.append(Pin(f"{port.kind.name}{seen[port.kind]}", PinRole.SIGNAL))
        return (*supply, *ports)

    @property
    def links(self) -> tuple[Link, ...]:
        """A computer joins nothing inside itself."""
        return ()
