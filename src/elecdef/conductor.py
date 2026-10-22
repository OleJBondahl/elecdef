"""The Conductor block: the wire of a cable or of a terminal, as a datasheet states it."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block, figure
from elecdef._quantity import Kind, Quantity
from elecdef.vocab import Colour, ConductorClass, ConductorMaterial, Insulation

__all__ = ["Conductor"]


@dataclass(frozen=True)
class Conductor(Block):
    """One conductor: material, stranding class, cross-section, gauge, insulation and colour.

    It has no pins; a product must fill the area.
    """

    needs: ClassVar[tuple[str, ...]] = ("area",)

    material: ConductorMaterial | None = None
    conductor_class: ConductorClass | None = None
    area: Quantity | None = figure(Kind.AREA)
    gauge: Quantity | None = figure(Kind.GAUGE)
    insulation: Insulation | None = None
    max_temperature: Quantity | None = figure(Kind.TEMPERATURE)
    colour: tuple[Colour, ...] = ()
    voltage_u0: Quantity | None = figure(Kind.VOLTAGE)
    voltage_u: Quantity | None = figure(Kind.VOLTAGE)
