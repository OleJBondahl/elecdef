"""The poles of a contact: each run of pins a pole link joins."""

from dataclasses import dataclass

from elecdef._pinorder import line_marking, marking_key
from elecdef.pins import Link, LinkKind, Pin, PinRole, Side

_POLE_KINDS = frozenset({LinkKind.SWITCHED, LinkKind.PROTECTIVE})
_PAIR = 2


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


_Key = tuple[str, Side | None]


def _order(pin: Pin) -> tuple[object, int]:
    """Marking order, a pin on no side first, then side A, then side B."""
    return marking_key(pin.marking), pin.side.value if pin.side else 0


def _is_pole(link: Link, by_key: dict[_Key, Pin], joined: set[_Key]) -> bool:
    """A pole link is switched, protective, or joins a LINE pin to a LOAD pin of any kind."""
    if link.kind in _POLE_KINDS:
        return True
    roles = {by_key[key].role for key in joined}
    return PinRole.LINE in roles and PinRole.LOAD in roles


def _groups(by_key: dict[_Key, Pin], links: tuple[Link, ...]) -> list[set[_Key]]:
    """The sets of (marking, side) keys that pole links join; an absent or coil pin skips a link.

    A link marking names every pin with it, so a marking on both sides joins both.
    """
    groups: list[set[_Key]] = []
    for link in links:
        named = [[key for key in by_key if key[0] == m] for m in link.markings]
        joined = {key for keys in named for key in keys}
        if not all(named) or len(joined) < _PAIR or not _is_pole(link, by_key, joined):
            continue
        if any(by_key[key].role is PinRole.COIL for key in joined):
            continue
        merged = joined.union(*(g for g in groups if g & joined))
        groups = [g for g in groups if not g & joined] + [merged]
    return groups


def poles(pins: tuple[Pin, ...], links: tuple[Link, ...]) -> tuple[Pole, ...]:
    """The poles in marking order: one per run of pole links that share a pin.

    A pole link is switched, protective, or joins a LINE pin to a LOAD pin.
    """
    by_key: dict[_Key, Pin] = {}
    for pin in pins:
        by_key.setdefault((pin.marking, pin.side), pin)
    found = []
    for group in _groups(by_key, links):
        ordered = sorted((by_key[key] for key in group), key=_order)
        found.append(Pole(_line(ordered), tuple(ordered)))
    return tuple(sorted(found, key=lambda pole: _order(pole.pins[0])))
