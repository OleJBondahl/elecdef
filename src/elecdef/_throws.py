"""The throws of a contact: which switched links join a common pin to a break or make pin."""

from dataclasses import dataclass

from elecdef._pinorder import marking_key
from elecdef.pins import Link, LinkKind, Pin, PinRole

_THROWS = frozenset({PinRole.BREAK, PinRole.MAKE})


@dataclass(frozen=True)
class Throw:
    """One throw: the `common` pin, the `throw` pin it closes to, and the state at rest.

    `closed_at_rest` is True when the throw is a break pin and False when it is a make pin.
    """

    common: Pin
    throw: Pin
    closed_at_rest: bool


def _throw(link: Link, by_marking: dict[str, Pin]) -> Throw | None:
    """The throw `link` makes, or None when it is not switched or joins no common to a throw."""
    first, second = (by_marking.get(marking) for marking in link.markings)
    if link.kind is not LinkKind.SWITCHED or first is None or second is None:
        return None
    for common, throw in ((first, second), (second, first)):
        if common.role is PinRole.COMMON and throw.role in _THROWS:
            return Throw(common, throw, throw.role is PinRole.BREAK)
    return None


def throws(pins: tuple[Pin, ...], links: tuple[Link, ...]) -> tuple[Throw, ...]:
    """The switched links that join a COMMON pin to a BREAK or MAKE pin, in marking order.

    A link that names an absent pin is skipped; `check` reports it.
    """
    by_marking: dict[str, Pin] = {}
    for pin in pins:
        by_marking.setdefault(pin.marking, pin)
    found = (_throw(link, by_marking) for link in links)
    return tuple(
        sorted(
            (t for t in found if t is not None),
            key=lambda t: (marking_key(t.common.marking), marking_key(t.throw.marking)),
        )
    )
