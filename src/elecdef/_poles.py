"""The poles of a contact: each run of pins a switched or protective link joins."""

from dataclasses import dataclass

from elecdef._pinorder import line_marking, marking_key
from elecdef.pins import Link, LinkKind, Pin, PinRole

_POLE_LINKS = frozenset({LinkKind.SWITCHED, LinkKind.PROTECTIVE})


@dataclass(frozen=True)
class Pole:
    """One pole: every pin its links join, in marking order, and the `line` pin."""

    line: Pin | None
    pins: tuple[Pin, ...]


def _line(group: list[Pin]) -> Pin | None:
    """The line pin of a pole: the one LINE role wins, else the numbering decides."""
    stated = [pin for pin in group if pin.role is PinRole.LINE]
    if stated:
        return stated[0] if len(stated) == 1 else None
    marking = line_marking(tuple(pin.marking for pin in group))
    return next((pin for pin in group if pin.marking == marking), None)


def _groups(by_marking: dict[str, Pin], links: tuple[Link, ...]) -> list[set[str]]:
    """The sets of markings that pole links join; a link with an absent or coil pin is skipped."""
    groups: list[set[str]] = []
    for link in links:
        joined = {m for m in link.markings if m in by_marking}
        if link.kind not in _POLE_LINKS or len(joined) != len(link.markings):
            continue
        if any(by_marking[m].role is PinRole.COIL for m in joined):
            continue
        merged = joined.union(*(g for g in groups if g & joined))
        groups = [g for g in groups if not g & joined] + [merged]
    return groups


def poles(pins: tuple[Pin, ...], links: tuple[Link, ...]) -> tuple[Pole, ...]:
    """The poles in marking order: one per run of switched or protective links that share a pin.

    A pin no such link joins is in no pole. A link that names an absent pin is skipped.
    """
    by_marking: dict[str, Pin] = {}
    for pin in pins:
        by_marking.setdefault(pin.marking, pin)
    found = []
    for group in _groups(by_marking, links):
        ordered = sorted((by_marking[m] for m in group), key=lambda pin: marking_key(pin.marking))
        found.append(Pole(_line(ordered), tuple(ordered)))
    return tuple(sorted(found, key=lambda pole: marking_key(pole.pins[0].marking)))
