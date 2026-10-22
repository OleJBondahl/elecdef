"""The Cable block with its Core and TypeCode: the cores of a cable and their pins (proposed)."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._quantity import Kind, Quantity
from elecdef._range import Range, Ranges
from elecdef.conductor import Conductor
from elecdef.pins import Pin, PinRole
from elecdef.vocab import Armour, Colour, CoreRole, Scheme, Screen, SheathMaterial

__all__ = ["Cable", "Core", "TypeCode"]

_SCREEN_MARKING = "SH"


@dataclass(frozen=True)
class Core:
    """One core of a cable: its number, colour code, pair, role and own conductor."""

    number: int | None = None
    colour: tuple[Colour, ...] = ()
    pair: int | None = None
    role: CoreRole | None = None
    conductor: Conductor | None = None

    def __post_init__(self) -> None:
        """Refuse a number or pair that is not an int, and a colour that is not a tuple of Colour."""
        for name in ("number", "pair"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
                message = f"{name} is an int, not {type(value).__name__}"
                raise TypeError(message)
        if not isinstance(self.colour, tuple) or not all(
            isinstance(c, Colour) for c in self.colour
        ):
            message = "colour is a tuple of Colour"
            raise TypeError(message)

    @property
    def marking(self) -> str:
        """The core number as text, else the colour names joined, else empty."""
        if self.number is not None:
            return str(self.number)
        return "".join(c.name for c in self.colour)


@dataclass(frozen=True)
class TypeCode:
    """A cable type designation: the scheme family and the text as printed."""

    scheme: Scheme
    text: str

    def __post_init__(self) -> None:
        """Refuse a scheme that is not a Scheme and a text that is not a str."""
        if not isinstance(self.scheme, Scheme):
            message = f"scheme is a Scheme, not {type(self.scheme).__name__}"
            raise TypeError(message)
        if not isinstance(self.text, str):
            message = f"text is a str, not {type(self.text).__name__}"
            raise TypeError(message)


@dataclass(frozen=True)
class Cable(Block):
    """A cable: its conductor, cores, screen, sheath and ratings.

    Pins are computed on read: one per core, plus SH (role SCREEN) when a screen is set.
    """

    needs: ClassVar[tuple[str, ...]] = ("cores",)

    conductor: Conductor | None = None
    cores: tuple[Core, ...] = ()
    screen: Screen | None = None
    armour: Armour | None = None
    outer_diameter: Quantity | None = figure(Kind.LENGTH)
    bend_radius_static: Range | None = figure(Kind.LENGTH)
    bend_radius_moving: Range | None = figure(Kind.LENGTH)
    sheath_material: SheathMaterial | None = None
    sheath_colour: Colour | None = None
    temperature: Ranges = figure(Kind.TEMPERATURE, many=True)
    halogen_free: bool | None = None
    flame_retardant: bool | None = None
    voltage_u0: Quantity | None = figure(Kind.VOLTAGE)
    voltage_u: Quantity | None = figure(Kind.VOLTAGE)
    type_code: TypeCode | None = None

    @property
    def pins(self) -> tuple[Pin, ...]:
        """One pin per core, then SH when the screen is not NONE."""
        pins = tuple(Pin(core.marking, PinRole.SIGNAL) for core in self.cores)
        if self.screen is not None and self.screen is not Screen.NONE:
            pins += (Pin(_SCREEN_MARKING, PinRole.SCREEN),)
        return pins

    @property
    def links(self) -> tuple[()]:
        """A cable joins no two pins."""
        return ()
