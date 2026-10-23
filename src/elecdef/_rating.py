"""The Rating block: the electrical limits of a part as a whole."""

from dataclasses import dataclass

from elecdef._block import Block, figure
from elecdef._quantity import Kind
from elecdef._range import Range, Ranges
from elecdef.vocab import OvervoltageCategory, PollutionDegree

__all__ = ["Rating"]


@dataclass(frozen=True)
class Rating(Block):
    """A part's ratings: voltages, currents, thermal current, power loss, frequency, clearances.

    Every field is unfilled by default.
    """

    voltage: Ranges = figure(Kind.VOLTAGE, many=True)
    insulation_voltage: Range | None = figure(Kind.VOLTAGE)
    impulse_voltage: Range | None = figure(Kind.VOLTAGE)
    thermal_current: Range | None = figure(Kind.CURRENT)
    frequency: Range | None = figure(Kind.FREQUENCY)
    overvoltage_category: OvervoltageCategory | None = None
    pollution_degree: PollutionDegree | None = None
    current: Ranges = figure(Kind.CURRENT, many=True)
    power_loss: Range | None = figure(Kind.POWER)
