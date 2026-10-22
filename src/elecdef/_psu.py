"""The PowerSupply block: a composite whose pins are its input, its outputs and its OK contact."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._contact import Contact
from elecdef._product import Symbol
from elecdef._quantity import Kind
from elecdef._range import Range, Ranges
from elecdef._relay import _joined, _numbered
from elecdef.pins import Link, Marking, Pin, PinRole
from elecdef.supply import SupplyInput
from elecdef.vocab import CircuitClass, OverloadBehaviour, PsuKind

__all__ = ["PowerSupply"]


@dataclass(frozen=True)
class PowerSupply(Block):
    """A power supply: input, output figures and OK contact; the pins are read on every access.

    Outputs: the first PLUS, the second MINUS, a further one PLUS; the OK contact is AUX 1.
    """

    needs: ClassVar[tuple[str, ...]] = ("output_voltage", "output_current")

    kind: PsuKind | None = None
    input: SupplyInput | None = None
    markings: tuple[str, ...] = ("+", "-")
    output_voltage: Range | None = figure(Kind.VOLTAGE)
    output_current: Ranges = figure(Kind.CURRENT, many=True)
    boost_current: Range | None = figure(Kind.CURRENT)
    hold_up: Range | None = figure(Kind.TIME)
    overload: OverloadBehaviour | None = None
    circuit_class: CircuitClass | None = None
    isolated: bool | None = None
    redundant: bool | None = None
    efficiency: Ranges = figure(Kind.RATIO, many=True)
    ok_contact: Contact | None = None
    connection: Connection | None = None
    body: Body | None = None
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Refuse markings that are not a tuple of str."""
        super().__post_init__()
        if not (
            isinstance(self.markings, tuple) and all(isinstance(m, str) for m in self.markings)
        ):
            message = "markings is a tuple of str"
            raise TypeError(message)

    def _joined(self) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
        """The pins and links with the OK contact numbered AUX 1 when it has no pins of its own."""
        outputs = tuple(
            Pin(marking, PinRole.MINUS if index == 1 else PinRole.PLUS)
            for index, marking in enumerate(self.markings)
        )
        contacts = _numbered((self.ok_contact,), Marking.AUX) if self.ok_contact else ()
        pins, links = _joined(None, contacts)
        return (self.input.pins if self.input else ()) + outputs + pins, links

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The input pins, the output pins, then the OK contact pins."""
        return self._joined()[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """The links of the OK contact."""
        return self._joined()[1]
