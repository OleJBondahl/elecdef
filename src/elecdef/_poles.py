"""The poles of a contact: the pin pairs a switched link joins, then the pins no link joins."""

from dataclasses import dataclass

from elecdef._pinorder import marking_key
from elecdef.pins import Link, LinkKind, Pin, PinRole

_NOT_POLE_PINS = frozenset({PinRole.PE, PinRole.SCREEN})


@dataclass(frozen=True)
class Pole:
    """One pole: its `ends`, and the `line` end when exactly one end has the LINE role.

    `ends` is `(line, load)` when `line` is known; a pole of one pin has that pin twice.
    """

    line: Pin | None
    ends: tuple[Pin, Pin]


def _pole(a: Pin, b: Pin) -> Pole:
    """The pole of `a` and `b`; the LINE end first when exactly one end is LINE."""
    for line, load in ((a, b), (b, a)):
        if line.role is PinRole.LINE and load.role is not PinRole.LINE:
            return Pole(line, (line, load))
    first, second = sorted((a, b), key=lambda pin: marking_key(pin.marking))
    return Pole(None, (first, second))


def _ends_key(pole: Pole) -> tuple[tuple[int, int, str], ...]:
    """The order of a pole: its lower end's marking."""
    return min(marking_key(pin.marking) for pin in pole.ends)


def _linked(pins: dict[str, Pin], links: tuple[Link, ...]) -> tuple[list[Pole], set[str]]:
    """One pole per run of switched links that share a pin, and every marking they join."""
    pairs = [
        sorted((pins[m] for m in link.markings), key=lambda pin: marking_key(pin.marking))
        for link in links
        if link.kind is LinkKind.SWITCHED and all(m in pins for m in link.markings)
    ]
    poles: list[Pole] = []
    seen: set[str] = set()
    for a, b in sorted(pairs, key=lambda pair: [marking_key(pin.marking) for pin in pair]):
        if not {a.marking, b.marking} & seen:
            poles.append(_pole(a, b))
        seen |= {a.marking, b.marking}
    return poles, seen


def poles(pins: tuple[Pin, ...], links: tuple[Link, ...]) -> tuple[Pole, ...]:
    """The poles in marking order: switched links that share a pin are one, then pins pair up.

    Pins no link joins, earth and screen left out, pair in order; an odd last pin stands alone.
    """
    by_marking: dict[str, Pin] = {}
    for pin in pins:
        by_marking.setdefault(pin.marking, pin)
    found, joined = _linked(by_marking, links)
    rest = sorted(
        (
            p
            for p in by_marking.values()
            if p.marking not in joined and p.role not in _NOT_POLE_PINS
        ),
        key=lambda pin: marking_key(pin.marking),
    )
    found += [_pole(a, b) for a, b in zip(rest[::2], rest[1::2], strict=False)]
    if len(rest) % 2:
        found.append(Pole(None, (rest[-1], rest[-1])))
    return tuple(sorted(found, key=_ends_key))
