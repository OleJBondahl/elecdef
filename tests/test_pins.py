"""E11 gate: contact pins and links per marking scheme, the marking test and the refusals.

The E10 gate, composite pins as the union of the sub-blocks', is at the end.
"""

import importlib
import inspect
import pkgutil
from dataclasses import dataclass, fields, replace

import pytest

import elecdef
from elecdef import Breaker, Coil, Contact, Contactor, Overload, PowerSupply, Relay
from elecdef._block import Block
from elecdef.fuse import FuseHolder
from elecdef.pins import (
    Link,
    LinkKind,
    Marking,
    Pin,
    PinRole,
    _is_marking,
    contact_pins,
    poles,
    throws,
)
from elecdef.supply import SupplyInput
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


# E10: a leaf stores its pins once; a composite computes them from its sub-blocks.
_LEAVES = {"SupplyInput", "Channel", "Device"}
_COMPUTED = {
    "PowerSupply",
    "PlcCard",
    "Relay",
    "Contactor",
    "ContactBlock",
    "Overload",
    "Breaker",
    "Cable",
    "Connector",
    "Fuse",
    "FuseHolder",
    "TerminalBlock",
    "Computer",
    "Coil",
    "Contact",
}


def _block_classes() -> list[type]:
    """Every Block subclass defined in an `elecdef` module, once."""
    found: dict[type, None] = {}
    for info in pkgutil.walk_packages(elecdef.__path__, "elecdef."):
        if info.name.endswith("__main__"):
            continue
        for member in vars(importlib.import_module(info.name)).values():
            if isinstance(member, type) and issubclass(member, Block) and member is not Block:
                found[member] = None
    return [c for c in found if c.__module__.startswith("elecdef")]


def _field_names(cls: type) -> set[str]:
    return {item.name for item in fields(cls)}  # ty: ignore[invalid-argument-type] - a dataclass


def _is_property(cls: type, name: str) -> bool:
    return isinstance(inspect.getattr_static(cls, name, None), property)


def _has_pins(cls: type) -> bool:
    return "pins" in _field_names(cls) or _is_property(cls, "pins")


def _stored_in_composite(classes: list[type]) -> list[str]:
    """The classes that are not leaves and store `pins` or `links` as a field."""
    return [
        f"{c.__name__}.{n}"
        for c in classes
        if c.__name__ not in _LEAVES
        for n in ("pins", "links")
        if n in _field_names(c)
    ]


def _clashes(classes: list[type]) -> list[str]:
    """The classes with a field and a property of one name."""
    return [
        f"{c.__name__}.{n}" for c in classes for n in sorted(_field_names(c)) if _is_property(c, n)
    ]


def test_e10_composites_store_no_pins_or_links() -> None:
    """Only SupplyInput, Channel and Device store pins; Device alone also stores links."""
    classes = {c.__name__: c for c in _block_classes()}
    assert _stored_in_composite(list(classes.values())) == []
    assert {n for n, c in classes.items() if "pins" in _field_names(c)} == _LEAVES
    assert {n for n, c in classes.items() if "links" in _field_names(c)} == {"Device"}
    assert classes.keys() >= _COMPUTED


def test_e10_pin_bearing_blocks_are_the_leaves_and_composites() -> None:
    """The Blocks with a `pins` field or property are exactly the leaves plus the composites."""
    bearing = {c.__name__ for c in _block_classes() if _has_pins(c)}
    assert bearing == _LEAVES | _COMPUTED


def test_e10_no_field_and_property_of_one_name() -> None:
    """No block has a field and a property sharing a name."""
    assert _clashes(_block_classes()) == []


def test_e10_property_pins_leaves_keep_own_pins() -> None:
    """Coil and Contact compute `pins` from a stored `own_pins`."""
    for cls in (Coil, Contact):
        assert _is_property(cls, "pins")
        assert "own_pins" in _field_names(cls)


def test_e10_checker_can_fail() -> None:
    """The scans flag a composite that stores `pins` and a class with a field and a property."""

    @dataclass(frozen=True)
    class Fake(Block):
        pins: tuple[Pin, ...] = ()

        @property
        def links(self) -> tuple[Link, ...]:
            return ()

    @dataclass(frozen=True)
    class Both(Block):
        links: tuple[Link, ...] = ()

    Both.links = property(lambda _: ())  # ty: ignore[invalid-assignment] - the clash is the test
    assert _stored_in_composite([Fake]) == ["Fake.pins"]
    assert _has_pins(Fake)
    assert _clashes([Both]) == ["Both.links"]


def _aux(form: ContactForm = ContactForm.MAKE) -> Contact:
    return Contact(form=form)


def _numbered(contact: Contact, number: int, scheme: Marking) -> tuple[tuple[Pin, ...], tuple]:
    """The pins and links an independently numbered copy of `contact` has."""
    return contact_pins(contact.form, number, scheme)  # ty: ignore[invalid-argument-type] - form set


def test_e10_relay_pins_are_coil_then_numbered_contacts() -> None:
    """Relay pins are the coil pins, then each contact's pins as AUX 1..n; links the contacts'."""
    coil = Coil()
    contacts = (_aux(), _aux(ContactForm.BREAK), _aux(ContactForm.CHANGEOVER))
    relay = Relay(coil=coil, contacts=contacts)
    parts = [_numbered(c, i, Marking.AUX) for i, c in enumerate(contacts, 1)]
    assert relay.pins == coil.pins + sum((p for p, _ in parts), ())
    assert relay.links == sum((k for _, k in parts), ())
    assert all(c.pins == () for c in contacts)


def test_e10_contactor_pins_are_coil_main_then_aux() -> None:
    """Contactor pins are the coil, MAIN 1..n for `main`, then AUX 1..n for `aux`."""
    coil, main, aux = Coil(), (_aux(), _aux()), (_aux(ContactForm.BREAK),)
    got = Contactor(coil=coil, main=main, aux=aux)
    expected = coil.pins
    for i, c in enumerate(main, 1):
        expected += _numbered(c, i, Marking.MAIN)[0]
    for i, c in enumerate(aux, 1):
        expected += _numbered(c, i, Marking.AUX)[0]
    assert got.pins == expected


def test_e10_power_supply_pins_are_input_output_then_ok_contact() -> None:
    """PowerSupply pins are the input pins, the output pair, then the OK contact as AUX 1."""
    supply = SupplyInput(pins=(Pin("L", PinRole.LINE), Pin("N", PinRole.LOAD)))
    ok = _aux()
    got = PowerSupply(input=supply, ok_contact=ok)
    output = (Pin("+", PinRole.PLUS), Pin("-", PinRole.MINUS))
    assert got.pins == supply.pins + output + _numbered(ok, 1, Marking.AUX)[0]
    assert got.links == _numbered(ok, 1, Marking.AUX)[1]


def test_e10_overload_pins_are_main_pairs_then_numbered_aux() -> None:
    """Overload pins are 1/L1,2/T1 per pole, then each aux as OVERLOAD 1..n."""
    aux = (_aux(ContactForm.BREAK), _aux())
    got = Overload(poles=2, aux=aux)
    main = sum((contact_pins(ContactForm.MAKE, n, Marking.MAIN)[0] for n in (1, 2)), ())
    expected = main + sum((_numbered(c, i, Marking.OVERLOAD)[0] for i, c in enumerate(aux, 1)), ())
    assert got.pins == expected
    assert [p.marking for p in main] == ["1/L1", "2/T1", "3/L2", "4/T2"]


def test_e10_breaker_pins_are_pole_pairs_then_numbered_aux() -> None:
    """Breaker pins are 2p-1 and 2p per pole, then each aux as AUX 1..n."""
    aux = (_aux(), _aux())
    got = Breaker(poles=2, aux=aux)
    poles = tuple(Pin(str(n), PinRole.LINE if n % 2 else PinRole.LOAD) for n in (1, 2, 3, 4))
    expected = poles + sum((_numbered(c, i, Marking.AUX)[0] for i, c in enumerate(aux, 1)), ())
    assert got.pins == expected


def test_e10_a_replaced_sub_block_is_read_fresh() -> None:
    """`replace` on a composite leaves no stale pins: they are read on every access."""
    relay = Relay(contacts=(_aux(),))
    assert replace(relay, contacts=(_aux(), _aux())).pins != relay.pins


# Expected throws as data: (scheme, form, n) -> ((common, throw, closed at rest), ...).
_THROWS = {
    (Marking.AUX, ContactForm.CHANGEOVER, 1): (("11", "12", True), ("11", "14", False)),
    (Marking.AUX, ContactForm.CHANGEOVER, 9): (("91", "92", True), ("91", "94", False)),
    (Marking.OVERLOAD, ContactForm.CHANGEOVER, 1): (("95", "96", True), ("95", "98", False)),
    (Marking.TIMER, ContactForm.CHANGEOVER, 1): (("15", "16", True), ("15", "18", False)),
    (Marking.PLAIN, ContactForm.CHANGEOVER, 2): (("4", "5", True), ("4", "6", False)),
    (Marking.AUX, ContactForm.MAKE, 1): (),
    (Marking.AUX, ContactForm.BREAK, 1): (),
    (Marking.MAIN, ContactForm.MAKE, 1): (),
}


@pytest.mark.parametrize(("key", "expected"), _THROWS.items(), ids=str)
def test_throws_of_the_sample_contacts_equal_the_stated_values(key, expected) -> None:
    """`throws` over `contact_pins` gives the common, the throw and the rest state as stated."""
    scheme, form, n = key
    pins, links = contact_pins(form, n, scheme)
    got = tuple((t.common.marking, t.throw.marking, t.closed_at_rest) for t in throws(pins, links))
    assert got == expected


def test_throws_do_not_depend_on_the_order_of_pins_or_links() -> None:
    """Reversed pins, reversed links and swapped link ends give the same throws."""
    pins, links = contact_pins(ContactForm.CHANGEOVER, 1, Marking.AUX)
    swapped = tuple(Link(link.markings[::-1], link.kind, link.closed_at_rest) for link in links)
    assert throws(pins[::-1], swapped[::-1]) == throws(pins, links)


def test_throws_carry_the_pins_and_skip_what_is_no_throw() -> None:
    """A throw holds the two pins; an absent pin, a conductive link or two throws give none."""
    pins, links = contact_pins(ContactForm.CHANGEOVER, 1, Marking.AUX)
    first = throws(pins, links)[0]
    assert (first.common, first.throw) == (pins[0], pins[1])
    assert throws(pins[:1], links) == ()
    conductive = (Link(("11", "12"), LinkKind.CONDUCTIVE),)
    assert throws(pins, conductive) == ()
    assert throws(pins, (Link(("12", "14"), LinkKind.SWITCHED, closed_at_rest=True),)) == ()


def _shape(found) -> list[tuple[str | None, tuple[str, ...]]]:
    return [(p.line.marking if p.line else None, tuple(e.marking for e in p.pins)) for p in found]


# Expected poles as data: (scheme, form, n) -> ((line marking or None, every pin), ...).
_POLES = {
    (Marking.MAIN, ContactForm.MAKE, 2): (("3/L2", ("3/L2", "4/T2")),),
    (Marking.AUX, ContactForm.MAKE, 1): (("13", ("13", "14")),),
    (Marking.AUX, ContactForm.BREAK, 9): (("91", ("91", "92")),),
    # A changeover is ONE pole with one common and two throws; its common is the line side.
    (Marking.AUX, ContactForm.CHANGEOVER, 1): (("11", ("11", "12", "14")),),
    (Marking.OVERLOAD, ContactForm.BREAK, 1): (("95", ("95", "96")),),
    (Marking.OVERLOAD, ContactForm.CHANGEOVER, 1): (("95", ("95", "96", "98")),),
    (Marking.TIMER, ContactForm.CHANGEOVER, 1): (("15", ("15", "16", "18")),),
    (Marking.PLAIN, ContactForm.MAKE, 1): ((None, ("1", "2")),),
}


@pytest.mark.parametrize(("key", "expected"), _POLES.items(), ids=str)
def test_poles_of_the_sample_contacts_equal_the_stated_values(key, expected) -> None:
    """`poles` over `contact_pins` gives the line pin and every pin as stated."""
    scheme, form, n = key
    assert tuple(_shape(poles(*contact_pins(form, n, scheme)))) == expected


def test_a_fuse_path_is_a_pole() -> None:
    """A protective link is a pole: a fuse holder of two poles gives two, line pin first stated."""
    got = poles(*(FuseHolder(poles=2).pins, FuseHolder(poles=2).links))
    assert _shape(got) == [("1", ("1", "2")), ("3", ("3", "4"))]


def test_a_conductive_link_is_no_pole() -> None:
    """Only switched and protective links make a pole."""
    pins = (Pin("1", PinRole.LINE), Pin("2", PinRole.LOAD))
    assert poles(pins, (Link(("1", "2"), LinkKind.CONDUCTIVE),)) == ()


def test_the_changeover_is_one_pole_not_two() -> None:
    """The two throws of a changeover share the common: one pole of three pins."""
    got = poles(*contact_pins(ContactForm.CHANGEOVER, 1, Marking.AUX))
    assert len(got) == 1
    assert len(got[0].pins) == 3


def test_a_stated_line_role_wins_over_the_numbering() -> None:
    """Numbering puts 13 on the line side; a LINE role on 14 overrides it."""
    pins = (Pin("13", PinRole.LOAD), Pin("14", PinRole.LINE))
    link = (Link(("13", "14"), LinkKind.SWITCHED, closed_at_rest=False),)
    assert _shape(poles(pins, link)) == [("14", ("13", "14"))]


def test_a_main_pole_takes_its_line_side_from_the_odd_number() -> None:
    """Without roles, `1/L1` and `2/T1` give 1/L1 as the line side."""
    pins = (Pin("2/T1", PinRole.SIGNAL), Pin("1/L1", PinRole.SIGNAL))
    link = (Link(("1/L1", "2/T1"), LinkKind.SWITCHED, closed_at_rest=False),)
    assert _shape(poles(pins, link)) == [("1/L1", ("1/L1", "2/T1"))]


def test_poles_of_a_main_contactor_run_in_marking_order() -> None:
    """Three main poles of a contactor: 1/L1 2/T1, then 3/L2 4/T2, then 5/L3 6/T3."""
    got = poles(*_main_poles(3))
    assert _shape(got) == [
        ("1/L1", ("1/L1", "2/T1")),
        ("3/L2", ("3/L2", "4/T2")),
        ("5/L3", ("5/L3", "6/T3")),
    ]
    assert poles(*_main_poles(3)) == poles(_main_poles(3)[0][::-1], _main_poles(3)[1][::-1])


def _main_poles(count: int):
    contacts = [contact_pins(ContactForm.MAKE, n, Marking.MAIN) for n in range(1, count + 1)]
    return sum((c[0] for c in contacts), ()), sum((c[1] for c in contacts), ())


def test_unlinked_pins_make_no_pole() -> None:
    """No link, no pole: signal pins, earth and a screen pair with nothing."""
    names = ["10", "9", "2", "1", "11", "PE", "SH"]
    roles = {"PE": PinRole.PE, "SH": PinRole.SCREEN}
    pins = tuple(Pin(m, roles.get(m, PinRole.SIGNAL)) for m in names)
    assert poles(pins, ()) == ()


def test_a_coil_is_no_pole_and_gets_no_line_side() -> None:
    """A1 and A2 with no link give nothing; a switched link on a coil pin is skipped."""
    coil = (Pin("A2", PinRole.COIL), Pin("A1", PinRole.COIL))
    assert poles(coil, ()) == ()
    assert poles(coil, (Link(("A1", "A2"), LinkKind.SWITCHED, closed_at_rest=False),)) == ()


def test_a_link_to_an_absent_pin_is_skipped() -> None:
    """A switched link naming an absent pin joins nothing."""
    pins = (Pin("13", PinRole.MAKE),)
    assert poles(pins, (Link(("13", "X"), LinkKind.SWITCHED, closed_at_rest=False),)) == ()


def test_throws_take_the_rest_state_from_the_pin_role_not_the_link() -> None:
    """A link that states the wrong rest state does not change the throw."""
    pins = (Pin("11", PinRole.COMMON), Pin("12", PinRole.BREAK))
    got = throws(pins, (Link(("11", "12"), LinkKind.SWITCHED, closed_at_rest=False),))
    assert [t.closed_at_rest for t in got] == [True]
