"""The Body block: the outer size, protection, temperature and mounting of a part."""

from dataclasses import dataclass

from elecdef._block import Block, figure
from elecdef._quantity import Kind, Quantity
from elecdef._range import Ranges
from elecdef.vocab import IpCode, Mounting

__all__ = ["Body"]


@dataclass(frozen=True)
class Body(Block):
    """The physical body of a part.

    Temperature rows tell operating (RATED) from storage (LIMITING) by their role.
    """

    width: Quantity | None = figure(Kind.LENGTH)
    height: Quantity | None = figure(Kind.LENGTH)
    depth: Quantity | None = figure(Kind.LENGTH)
    ip: IpCode | None = None
    temperature: Ranges = figure(Kind.TEMPERATURE, many=True)
    mounting: Mounting | None = None
