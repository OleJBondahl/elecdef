"""The PlcCard block: groups of channels numbered 1..N, whose pins are read on every access."""

from dataclasses import dataclass
from typing import ClassVar

from elecdef._block import Block
from elecdef._body import Body
from elecdef.pins import Link, Pin, PinRole
from elecdef.plc import Channel, ChannelGroup
from elecdef.supply import SupplyInput
from elecdef.vocab import Bus, CardForm, CardRole, Pl, Sil

__all__ = ["PlcCard"]


def _channels(groups: tuple[ChannelGroup, ...]) -> tuple[tuple[Channel, ...], ...]:
    """The channels of each group, numbered 1..N across the groups."""
    out: list[tuple[Channel, ...]] = []
    first = 1
    for group in groups:
        channels = group.channels(first)
        out.append(channels)
        first += len(channels)
    return tuple(out)


@dataclass(frozen=True)
class PlcCard(Block):
    """A PLC card: supply, groups of channels, form, role, bus and safety levels.

    It stores no pins: `pins` are the supply pins, then each group's channel pins and common pins.
    """

    needs: ClassVar[tuple[str, ...]] = ("groups",)

    supply: SupplyInput | None = None
    groups: tuple[ChannelGroup, ...] = ()
    form: CardForm | None = None
    role: CardRole | None = None
    bus: Bus | None = None
    sil: Sil | None = None
    pl: Pl | None = None
    body: Body | None = None

    def __post_init__(self) -> None:
        """Refuse groups that are not a tuple of ChannelGroup."""
        super().__post_init__()
        if not (
            isinstance(self.groups, tuple) and all(isinstance(g, ChannelGroup) for g in self.groups)
        ):
            message = "groups is a tuple of ChannelGroup"
            raise TypeError(message)

    @property
    def channels(self) -> tuple[Channel, ...]:
        """Every channel of every group, numbered 1..N."""
        return tuple(channel for each in _channels(self.groups) for channel in each)

    @property
    def pins(self) -> tuple[Pin, ...]:
        """The supply pins, then for each group its channel pins and its common pins."""
        pins = self.supply.pins if self.supply else ()
        for group, channels in zip(self.groups, _channels(self.groups), strict=True):
            pins += tuple(pin for channel in channels for pin in channel.pins)
            pins += tuple(Pin(marking, PinRole.COMMON) for marking in group.common)
        return pins

    @property
    def links(self) -> tuple[Link, ...]:
        """No links: the card's pins are not joined inside the card."""
        return ()
