"""The Rating block: the electrical limits of a part as a whole."""

from dataclasses import dataclass

from elecdef._block import Block, figure
from elecdef._quantity import Kind
from elecdef._range import Range, Ranges
from elecdef.vocab import OvervoltageCategory, PollutionDegree

__all__ = ["Rating"]


@dataclass(frozen=True)
class Rating(Block):
    """The ratings of a whole part: voltages, thermal current, frequency and clearance classes.

    Every field is unfilled by default.
    """

    voltage: Ranges = figure(Kind.VOLTAGE, many=True)  # noqa: RUF009 - figure() is the field metadata
    insulation_voltage: Range | None = figure(Kind.VOLTAGE)  # noqa: RUF009 - figure() is the field metadata
    impulse_voltage: Range | None = figure(Kind.VOLTAGE)  # noqa: RUF009 - figure() is the field metadata
    thermal_current: Range | None = figure(Kind.CURRENT)  # noqa: RUF009 - figure() is the field metadata
    frequency: Range | None = figure(Kind.FREQUENCY)  # noqa: RUF009 - figure() is the field metadata
    overvoltage_category: OvervoltageCategory | None = None
    pollution_degree: PollutionDegree | None = None
