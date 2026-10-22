"""The Connection block: how a conductor or a pin is attached."""

from dataclasses import dataclass

from elecdef._block import Block, figure
from elecdef._quantity import Kind, Quantity
from elecdef._range import Range, Ranges
from elecdef.vocab import ConductorMaterial, ScrewSize, Technology

__all__ = ["Connection"]


@dataclass(frozen=True)
class Connection(Block):
    """One connection point: its technology, conductor range, strip length and torque.

    Every field is unfilled by default, so a leaf states only its technology.
    """

    technology: Technology | None = None
    conductor: Ranges = figure(Kind.AREA, many=True)  # noqa: RUF009 - figure() is the field metadata
    conductor_awg: Ranges = figure(Kind.GAUGE, many=True)  # noqa: RUF009 - figure() is the field metadata
    conductors_per_clamp: int | None = None
    strip_length: Quantity | None = figure(Kind.LENGTH)  # noqa: RUF009 - figure() is the field metadata
    torque: Range | None = figure(Kind.TORQUE)  # noqa: RUF009 - figure() is the field metadata
    screw: ScrewSize | None = None
    pitch: Quantity | None = figure(Kind.LENGTH)  # noqa: RUF009 - figure() is the field metadata
    material: ConductorMaterial | None = None
