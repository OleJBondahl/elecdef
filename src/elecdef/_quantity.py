"""Measured figures: `Kind`, `Unit` and `Quantity`, exact in `Decimal`."""

import decimal
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto


class Kind(Enum):
    """The physical kind a unit belongs to; conversion and comparison stay inside one kind."""

    VOLTAGE = auto()
    CURRENT = auto()
    POWER = auto()
    APPARENT_POWER = auto()
    RESISTANCE = auto()
    FREQUENCY = auto()
    TIME = auto()
    LENGTH = auto()
    AREA = auto()
    GAUGE = auto()
    TORQUE = auto()
    RATIO = auto()
    TEMPERATURE = auto()
    TEMPERATURE_DIFFERENCE = auto()
    CHARGE = auto()


# Every Quantity calculation runs here, never in the caller's decimal context.
_CONTEXT = decimal.Context(
    prec=60,
    rounding=decimal.ROUND_HALF_EVEN,
    Emin=-999999,
    Emax=999999,
    traps=[decimal.InvalidOperation, decimal.DivisionByZero, decimal.Overflow],
)


def _decimal(value: object) -> Decimal:
    """An int, a str or a Decimal as a finite Decimal; anything else is a TypeError."""
    if isinstance(value, bool) or not isinstance(value, int | str | Decimal):
        message = f"a figure is an int, a str or a Decimal, not {type(value).__name__}"
        raise TypeError(message)
    try:
        number = Decimal(value)
    except decimal.InvalidOperation:
        message = f"not a decimal number: {value!r}"
        raise TypeError(message) from None
    if not number.is_finite():
        message = f"a figure is finite, not {value!r}"
        raise TypeError(message)
    return number


class Unit(Enum):
    """A unit of one kind with an exact factor to the base unit; `U.V(24)` builds a Quantity."""

    V = ("V", Kind.VOLTAGE, "1")
    MV = ("mV", Kind.VOLTAGE, "0.001")
    KV = ("kV", Kind.VOLTAGE, "1000")
    A = ("A", Kind.CURRENT, "1")
    UA = ("uA", Kind.CURRENT, "0.000001")
    MA = ("mA", Kind.CURRENT, "0.001")
    KA = ("kA", Kind.CURRENT, "1000")
    W = ("W", Kind.POWER, "1")
    KW = ("kW", Kind.POWER, "1000")
    VA = ("VA", Kind.APPARENT_POWER, "1")
    KVA = ("kVA", Kind.APPARENT_POWER, "1000")
    OHM = ("ohm", Kind.RESISTANCE, "1")
    KOHM = ("kohm", Kind.RESISTANCE, "1000")
    MEGOHM = ("Mohm", Kind.RESISTANCE, "1000000")
    HZ = ("Hz", Kind.FREQUENCY, "1")
    KHZ = ("kHz", Kind.FREQUENCY, "1000")
    S = ("s", Kind.TIME, "1")
    MS = ("ms", Kind.TIME, "0.001")
    US = ("us", Kind.TIME, "0.000001")
    M = ("m", Kind.LENGTH, "1")
    MM = ("mm", Kind.LENGTH, "0.001")
    UM = ("um", Kind.LENGTH, "0.000001")
    MM2 = ("mm2", Kind.AREA, "1")
    AWG = ("AWG", Kind.GAUGE, "1")
    N_M = ("N m", Kind.TORQUE, "1")
    PCT = ("%", Kind.RATIO, "0.01")
    PPM = ("ppm", Kind.RATIO, "0.000001")
    DEG_C = ("degC", Kind.TEMPERATURE, "1")
    K = ("K", Kind.TEMPERATURE_DIFFERENCE, "1")
    AH = ("Ah", Kind.CHARGE, "1")

    symbol: str
    kind: Kind
    factor: Decimal

    def __init__(self, symbol: str, kind: Kind, factor: str) -> None:
        """Hold the symbol, the kind and the factor as an exact Decimal."""
        self.symbol = symbol
        self.kind = kind
        self.factor = Decimal(factor)

    def __call__(self, value: int | str | Decimal) -> Quantity:
        """Build a Quantity from an int, a str or a Decimal; a float or a bool is a TypeError."""
        return Quantity(_decimal(value), self)


@dataclass(frozen=True, slots=True)
class Quantity:
    """A Decimal and its Unit; `==` compares as written, `same` and ordering in base units."""

    value: Decimal
    unit: Unit

    def __post_init__(self) -> None:
        """Refuse a value that is not a finite Decimal and a unit that is not a Unit."""
        if not isinstance(self.value, Decimal) or not self.value.is_finite():
            message = f"a Quantity holds a finite Decimal, not {self.value!r}"
            raise TypeError(message)
        if not isinstance(self.unit, Unit):
            message = f"a Quantity holds a Unit, not {self.unit!r}"
            raise TypeError(message)

    def base(self) -> Decimal:
        """The value in the base unit of its kind."""
        return _CONTEXT.multiply(self.value, self.unit.factor)

    def to(self, unit: Unit) -> Quantity:
        """The same figure in another unit of the same kind; another kind is a TypeError."""
        if not isinstance(unit, Unit):
            message = f"expected a Unit, not {type(unit).__name__}"
            raise TypeError(message)
        self._expect(unit.kind, unit.symbol)
        return Quantity(_CONTEXT.divide(self.base(), unit.factor), unit)

    def same(self, other: Quantity) -> bool:
        """True when both are equal in base units; another kind is a TypeError."""
        return self._base_of(other) == self.base()

    def __lt__(self, other: Quantity) -> bool:
        """Order by base units; another kind is a TypeError."""
        return self.base() < self._base_of(other)

    def __le__(self, other: Quantity) -> bool:
        """Order by base units; another kind is a TypeError."""
        return self.base() <= self._base_of(other)

    def __gt__(self, other: Quantity) -> bool:
        """Order by base units; another kind is a TypeError."""
        return self.base() > self._base_of(other)

    def __ge__(self, other: Quantity) -> bool:
        """Order by base units; another kind is a TypeError."""
        return self.base() >= self._base_of(other)

    def _expect(self, kind: Kind, symbol: str) -> None:
        if kind is not self.unit.kind:
            message = f"{self.unit.symbol} is {self.unit.kind.name}, {symbol} is {kind.name}"
            raise TypeError(message)

    def _base_of(self, other: Quantity) -> Decimal:
        if not isinstance(other, Quantity):
            message = f"expected a Quantity, not {type(other).__name__}"
            raise TypeError(message)
        self._expect(other.unit.kind, other.unit.symbol)
        return other.base()
