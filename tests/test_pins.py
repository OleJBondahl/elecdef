"""E11 gate: contact pins and links per marking scheme, the marking test and the refusals."""

import pytest

from elecdef.pins import Link, LinkKind, Marking, Pin, PinRole, _is_marking, contact_pins
from elecdef.vocab import ContactForm

# TIMER and PLAIN rows are proposed, not sourced. Each value is the nine contacts, space separated.
_GOLDEN = {
    (Marking.AUX, ContactForm.MAKE): "13,14 23,24 33,34 43,44 53,54 63,64 73,74 83,84 93,94",
    (Marking.AUX, ContactForm.BREAK): "11,12 21,22 31,32 41,42 51,52 61,62 71,72 81,82 91,92",
    (
        Marking.AUX,
        ContactForm.CHANGEOVER,
    ): "11,12,14 21,22,24 31,32,34 41,42,44 51,52,54 61,62,64 71,72,74 81,82,84 91,92,94",
    (
        Marking.MAIN,
        ContactForm.MAKE,
    ): "1/L1,2/T1 3/L2,4/T2 5/L3,6/T3 7/L4,8/T4 9/L5,10/T5 "
    "11/L6,12/T6 13/L7,14/T7 15/L8,16/T8 17/L9,18/T9",
    (Marking.OVERLOAD, ContactForm.MAKE): "97,98 97,98 97,98 97,98 97,98 97,98 97,98 97,98 97,98",
    (Marking.OVERLOAD, ContactForm.BREAK): "95,96 95,96 95,96 95,96 95,96 95,96 95,96 95,96 95,96",
    (
        Marking.OVERLOAD,
        ContactForm.CHANGEOVER,
    ): "95,96,98 95,96,98 95,96,98 95,96,98 95,96,98 95,96,98 95,96,98 95,96,98 95,96,98",
    (Marking.TIMER, ContactForm.MAKE): "15,18 25,28 35,38 45,48 55,58 65,68 75,78 85,88 95,98",
    (Marking.TIMER, ContactForm.BREAK): "15,16 25,26 35,36 45,46 55,56 65,66 75,76 85,86 95,96",
    (
        Marking.TIMER,
        ContactForm.CHANGEOVER,
    ): "15,16,18 25,26,28 35,36,38 45,46,48 55,56,58 65,66,68 75,76,78 85,86,88 95,96,98",
    (Marking.PLAIN, ContactForm.MAKE): "1,2 3,4 5,6 7,8 9,10 11,12 13,14 15,16 17,18",
    (Marking.PLAIN, ContactForm.BREAK): "1,2 3,4 5,6 7,8 9,10 11,12 13,14 15,16 17,18",
    (
        Marking.PLAIN,
        ContactForm.CHANGEOVER,
    ): "1,2,3 4,5,6 7,8,9 10,11,12 13,14,15 16,17,18 19,20,21 22,23,24 25,26,27",
}


@pytest.mark.parametrize(("key", "text"), list(_GOLDEN.items()))
def test_golden_markings(key: tuple[Marking, ContactForm], text: str) -> None:
    """Every contact index gives the literal markings."""
    scheme, form = key
    got = tuple(tuple(p.marking for p in contact_pins(form, n, scheme)[0]) for n in range(1, 10))
    assert got == tuple(tuple(c.split(",")) for c in text.split())


_C = (PinRole.COMMON, PinRole.BREAK, PinRole.MAKE)
_MM = (PinRole.MAKE, PinRole.MAKE)
_BB = (PinRole.BREAK, PinRole.BREAK)
# Each value is (markings, roles, links as (first, second, closed_at_rest)) for contact 1.
_SHAPE = {
    (Marking.AUX, ContactForm.MAKE): (("13", "14"), _MM, (("13", "14", False),)),
    (Marking.AUX, ContactForm.BREAK): (("11", "12"), _BB, (("11", "12", True),)),
    (Marking.AUX, ContactForm.CHANGEOVER): (
        ("11", "12", "14"),
        _C,
        (("11", "12", True), ("11", "14", False)),
    ),
    (Marking.MAIN, ContactForm.MAKE): (
        ("1/L1", "2/T1"),
        (PinRole.LINE, PinRole.LOAD),
        (("1/L1", "2/T1", False),),
    ),
    (Marking.OVERLOAD, ContactForm.MAKE): (("97", "98"), _MM, (("97", "98", False),)),
    (Marking.OVERLOAD, ContactForm.BREAK): (("95", "96"), _BB, (("95", "96", True),)),
    (Marking.OVERLOAD, ContactForm.CHANGEOVER): (
        ("95", "96", "98"),
        _C,
        (("95", "96", True), ("95", "98", False)),
    ),
    (Marking.TIMER, ContactForm.MAKE): (("15", "18"), _MM, (("15", "18", False),)),
    (Marking.TIMER, ContactForm.BREAK): (("15", "16"), _BB, (("15", "16", True),)),
    (Marking.TIMER, ContactForm.CHANGEOVER): (
        ("15", "16", "18"),
        _C,
        (("15", "16", True), ("15", "18", False)),
    ),
    (Marking.PLAIN, ContactForm.MAKE): (("1", "2"), _MM, (("1", "2", False),)),
    (Marking.PLAIN, ContactForm.BREAK): (("1", "2"), _BB, (("1", "2", True),)),
    (Marking.PLAIN, ContactForm.CHANGEOVER): (
        ("1", "2", "3"),
        _C,
        (("1", "2", True), ("1", "3", False)),
    ),
}


@pytest.mark.parametrize(("key", "shape"), list(_SHAPE.items()))
def test_roles_sides_links_for_n1(key: tuple[Marking, ContactForm], shape: tuple) -> None:
    """Contact 1 has the stated roles, no side, no alternates and the stated switched links."""
    markings, roles, links = shape
    pins, got_links = contact_pins(key[1], 1, key[0])
    assert pins == tuple(Pin(m, r) for m, r in zip(markings, roles, strict=True))
    assert all(p.side is None and p.alternates == () for p in pins)
    assert got_links == tuple(Link((a, b), LinkKind.SWITCHED, closed) for a, b, closed in links)


@pytest.mark.parametrize(
    ("scheme", "form", "n"),
    [
        (Marking.MAIN, ContactForm.BREAK, 1),
        (Marking.MAIN, ContactForm.CHANGEOVER, 1),
        (Marking.AUX, ContactForm.MAKE, 0),
        (Marking.AUX, ContactForm.MAKE, 10),
        (Marking.AUX, ContactForm.MAKE, True),
        (Marking.AUX, ContactForm.MAKE, "1"),
        (Marking.OVERLOAD, ContactForm.MAKE, 0),
    ],
)
def test_contact_pins_refuses(scheme: Marking, form: ContactForm, n: object) -> None:
    """A form the scheme lacks and an n that is not an int from 1 to 9 raise TypeError."""
    with pytest.raises(TypeError):
        contact_pins(form, n, scheme)  # ty: ignore[invalid-argument-type] - the bad n is the test


@pytest.mark.parametrize("text", ["13", "A1", "1/L1", "+", "a.b-c"])
def test_is_marking_accepts(text: str) -> None:
    """Letters, digits and the six marking characters pass."""
    assert _is_marking(text)


def test_is_marking_accepts_apostrophe() -> None:
    """The apostrophe is a marking character."""
    assert _is_marking("2'")


@pytest.mark.parametrize("text", ["", " ", "1;2", "a b", "é"])
def test_is_marking_rejects(text: str) -> None:
    """Empty text, spaces, other punctuation and non-ASCII letters fail."""
    assert not _is_marking(text)


def test_link_accepts_a_pair() -> None:
    """Two str in a tuple make a link."""
    assert Link(("1", "2"), LinkKind.CONDUCTIVE).closed_at_rest is None


@pytest.mark.parametrize("markings", [("1",), ("1", "2", "3"), ["1", "2"], ("1", 2)])
def test_link_refuses(markings: object) -> None:
    """One marking, three, a list and a non-str element raise TypeError."""
    with pytest.raises(TypeError):
        Link(markings, LinkKind.CONDUCTIVE)  # ty: ignore[invalid-argument-type] - the bad pair is the test


def test_pin_defaults() -> None:
    """A pin has no side and no alternates unless given."""
    pin = Pin("1", PinRole.COIL)
    assert pin.side is None
    assert pin.alternates == ()
