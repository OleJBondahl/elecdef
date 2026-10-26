"""The pin door: marking schemes and the pins and links of a contact."""

from dataclasses import dataclass
from enum import Enum, auto

from elecdef.vocab import ContactForm

__all__ = ["Link", "LinkKind", "Marking", "Pin", "PinRole", "Side", "contact_pins"]

_PAIR = 2
_MAX_N = 9
_MARKING_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/+-.'")


class PinRole(Enum):
    """What a pin does in its part."""

    COMMON = auto()
    MAKE = auto()
    BREAK = auto()
    LINE = auto()
    LOAD = auto()
    COIL = auto()
    PLUS = auto()
    MINUS = auto()
    SIGNAL = auto()
    SUPPLY = auto()
    PE = auto()
    SCREEN = auto()


class Side(Enum):
    """Which side of a part a pin is on."""

    A = auto()
    B = auto()


class LinkKind(Enum):
    """How two pins of a part are joined."""

    CONDUCTIVE = auto()
    SWITCHED = auto()
    PROTECTIVE = auto()


class Marking(Enum):
    """The marking schemes; TIMER and PLAIN are proposed, not sourced."""

    AUX = auto()
    MAIN = auto()
    OVERLOAD = auto()
    TIMER = auto()
    PLAIN = auto()


@dataclass(frozen=True)
class Pin:
    """One pin: its marking, its role, its side and the alternate markings it may carry."""

    marking: str
    role: PinRole
    side: Side | None = None
    alternates: tuple[str, ...] = ()


@dataclass(frozen=True)
class Link:
    """A join between the two pins named by `markings`; `closed_at_rest` is for a switched link."""

    markings: tuple[str, ...]
    kind: LinkKind
    closed_at_rest: bool | None = None

    def __post_init__(self) -> None:
        """Refuse markings that are not a tuple of exactly two str."""
        pair = self.markings
        if not (
            isinstance(pair, tuple) and len(pair) == _PAIR and all(isinstance(m, str) for m in pair)
        ):
            message = "markings is a tuple of exactly two str"
            raise TypeError(message)
        if self.closed_at_rest is not None and not isinstance(self.closed_at_rest, bool):
            message = "closed_at_rest is a bool or None"
            raise TypeError(message)


def _is_marking(text: str) -> bool:
    """Say whether `text` is a non-empty run of the characters a marking may use."""
    return bool(text) and all(c in _MARKING_CHARS for c in text)


_M, _B, _C = PinRole.MAKE, PinRole.BREAK, PinRole.COMMON

# Rows are (marking template, role); link rows are (pin index, pin index, closed at rest).
# Template fields: n the contact index, a = 2n-1, b = 2n, c = 3n-2, d = 3n-1, e = 3n.
_AUX = {
    ContactForm.MAKE: ((("{n}3", _M), ("{n}4", _M)), ((0, 1, False),)),
    ContactForm.BREAK: ((("{n}1", _B), ("{n}2", _B)), ((0, 1, True),)),
    ContactForm.CHANGEOVER: (
        (("{n}1", _C), ("{n}2", _B), ("{n}4", _M)),
        ((0, 1, True), (0, 2, False)),
    ),
}
_MAIN = {
    ContactForm.MAKE: ((("{a}/L{n}", PinRole.LINE), ("{b}/T{n}", PinRole.LOAD)), ((0, 1, False),)),
}
_OVERLOAD = {
    ContactForm.MAKE: ((("97", _M), ("98", _M)), ((0, 1, False),)),
    ContactForm.BREAK: ((("95", _B), ("96", _B)), ((0, 1, True),)),
    ContactForm.CHANGEOVER: ((("95", _C), ("96", _B), ("98", _M)), ((0, 1, True), (0, 2, False))),
}
# Proposed, not sourced.
_TIMER = {
    ContactForm.MAKE: ((("{n}5", _M), ("{n}8", _M)), ((0, 1, False),)),
    ContactForm.BREAK: ((("{n}5", _B), ("{n}6", _B)), ((0, 1, True),)),
    ContactForm.CHANGEOVER: (
        (("{n}5", _C), ("{n}6", _B), ("{n}8", _M)),
        ((0, 1, True), (0, 2, False)),
    ),
}
# Proposed, not sourced.
_PLAIN = {
    ContactForm.MAKE: ((("{a}", _M), ("{b}", _M)), ((0, 1, False),)),
    ContactForm.BREAK: ((("{a}", _B), ("{b}", _B)), ((0, 1, True),)),
    ContactForm.CHANGEOVER: (
        (("{c}", _C), ("{d}", _B), ("{e}", _M)),
        ((0, 1, True), (0, 2, False)),
    ),
}
_SCHEMES = {
    Marking.AUX: _AUX,
    Marking.MAIN: _MAIN,
    Marking.OVERLOAD: _OVERLOAD,
    Marking.TIMER: _TIMER,
    Marking.PLAIN: _PLAIN,
}


def contact_pins(
    form: ContactForm, n: int, scheme: Marking
) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
    """Return the pins and links of contact `n` (1 to 9) in `form` under `scheme`.

    Raises TypeError for an `n` out of range or a form the scheme does not have.
    """
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= _MAX_N:
        message = "n is an int from 1 to 9"
        raise TypeError(message)
    rows = _SCHEMES[scheme].get(form)
    if rows is None:
        message = f"the {scheme.name} scheme has no {form.name} contact"
        raise TypeError(message)
    fields = {"n": n, "a": 2 * n - 1, "b": 2 * n, "c": 3 * n - 2, "d": 3 * n - 1, "e": 3 * n}
    pin_rows, link_rows = rows
    pins = tuple(Pin(template.format(**fields), role) for template, role in pin_rows)
    links = tuple(
        Link((pins[i].marking, pins[j].marking), LinkKind.SWITCHED, closed)
        for i, j, closed in link_rows
    )
    return pins, links
