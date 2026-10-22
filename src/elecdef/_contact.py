"""The Contact block: one switching element, with the pins its number and scheme give."""

from dataclasses import dataclass, field
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._connection import Connection
from elecdef._product import Symbol
from elecdef._quantity import Kind
from elecdef._range import Range, Ranges
from elecdef.pins import Link, Marking, Pin, contact_pins
from elecdef.vocab import ContactFeature, ContactForm, ContactMaterial

__all__ = ["Contact"]

_MAX_N = 9


@dataclass(frozen=True)
class Contact(Block):
    """One contact: form, ratings per condition, and the pins computed from number and scheme.

    `own_pins` holds only what the author gave; `pins` is read from `number` and `scheme` each time.
    """

    needs: ClassVar[tuple[str, ...]] = ("switching",)

    form: ContactForm | None = None
    features: frozenset[ContactFeature] = field(default_factory=frozenset)
    switching: Ranges = figure(Kind.CURRENT, many=True)
    voltage: Range | None = figure(Kind.VOLTAGE)
    min_load_voltage: Range | None = figure(Kind.VOLTAGE)
    min_load_current: Range | None = figure(Kind.CURRENT)
    material: ContactMaterial | None = None
    mechanical_life: int | None = None
    electrical_life: int | None = None
    connection: Connection | None = None
    number: int | None = None
    scheme: Marking | None = None
    own_pins: tuple[Pin, ...] = ()
    symbol: Symbol | None = None

    def __post_init__(self) -> None:
        """Check the figures, then refuse a number or form the scheme cannot mark."""
        super().__post_init__()
        number = self.number
        if number is not None and (
            not isinstance(number, int) or isinstance(number, bool) or not 1 <= number <= _MAX_N
        ):
            message = "number is an int from 1 to 9"
            raise TypeError(message)
        self._computed()

    def _computed(self) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
        """The pins and links read from form, number and scheme; empty when any is unset."""
        form, number, scheme = self.form, self.number, self.scheme
        if self.own_pins or form is None or number is None or scheme is None:
            return (), ()
        return contact_pins(form, number, scheme)

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The author's `own_pins`, else the pins of the contact's form, number and scheme."""
        return self.own_pins or self._computed()[0]

    @property
    def links(self) -> tuple[Link, ...]:
        """The links of the computed pins; none with `own_pins`."""
        return self._computed()[1]
