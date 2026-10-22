"""Overload, Fuse, FuseHolder and Breaker: golden pins and links, kind checks, no stored pins."""

from dataclasses import fields, replace

import pytest

from elecdef import Breaker, Contact, Fuse, Range, Role
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef._overload import Overload
from elecdef.fuse import FuseHolder
from elecdef.pins import LinkKind, PinRole, contact_pins
from elecdef.pins import Marking as M  # noqa: N817 - short scheme alias
from elecdef.vocab import ContactForm, FuseClass, Reset, TripClass, TripCurve

BREAK = Contact(ContactForm.BREAK)
MAKE = Contact(ContactForm.MAKE)
SETTING = Range(Role.RATED, min=U.A(7), max=U.A(10))
OVERLOAD = Overload(
    poles=3,
    setting=SETTING,
    trip_class=TripClass.C10,
    reset=Reset.BOTH,
    phase_failure=True,
    aux=(BREAK, MAKE),
)


def _markings(block) -> list[str]:
    return [pin.marking for pin in block.pins]


def test_overload_pins_are_golden():
    main = ["1/L1", "2/T1", "3/L2", "4/T2", "5/L3", "6/T3"]
    assert _markings(OVERLOAD) == [*main, "95", "96", "97", "98"]
    assert OVERLOAD.needs == ("setting",)


def test_overload_main_pins_have_line_and_load_roles():
    roles = [pin.role for pin in OVERLOAD.pins[:6]]
    assert roles == [PinRole.LINE, PinRole.LOAD] * 3


def test_overload_aux_links_are_switched_and_main_links_conductive():
    main, aux = OVERLOAD.links[:3], OVERLOAD.links[3:]
    assert [link.markings for link in main] == [
        ("1/L1", "2/T1"),
        ("3/L2", "4/T2"),
        ("5/L3", "6/T3"),
    ]
    assert {link.kind for link in main} == {LinkKind.CONDUCTIVE}
    assert [(link.markings, link.kind, link.closed_at_rest) for link in aux] == [
        (("95", "96"), LinkKind.SWITCHED, True),
        (("97", "98"), LinkKind.SWITCHED, False),
    ]


def test_overload_stores_no_pins_or_links():
    names = {item.name for item in fields(Overload)}
    assert not names & {"pins", "links"}
    assert isinstance(Overload.pins, property)


def test_overload_setting_must_be_a_current_range():
    with pytest.raises(TypeError):
        Overload(setting=U.A(7))  # ty: ignore[invalid-argument-type] - the refusal under test
    with pytest.raises(TypeError):
        Overload(setting=Range(Role.RATED, nom=U.V(7)))


def test_overload_replace_leaves_no_stale_pins():
    assert len(replace(OVERLOAD, poles=2).pins) == 4 + 4


@pytest.mark.parametrize("poles", [0, 10, True, "3"])
def test_overload_poles_out_of_range_raises(poles):
    with pytest.raises(TypeError):
        Overload(poles=poles, setting=SETTING)


# Proposed rows (no source): Fuse, FuseHolder and Breaker.
def test_fuse_pins_and_link_are_proposed_golden():
    fuse = Fuse(current=Range(Role.RATED, nom=U.A(16)), fuse_class=FuseClass.gG)
    assert _markings(fuse) == ["1", "2"]
    assert [pin.role for pin in fuse.pins] == [PinRole.LINE, PinRole.LOAD]
    assert [(link.markings, link.kind) for link in fuse.links] == [
        (("1", "2"), LinkKind.PROTECTIVE)
    ]
    assert Fuse.needs == ("current",)
    assert fuse.fuse_class is FuseClass.gG


def test_fuse_kind_check():
    with pytest.raises(TypeError):
        Fuse(current=U.V(16))  # ty: ignore[invalid-argument-type] - the refusal under test
    with pytest.raises(TypeError):
        Fuse(voltage=(Range(Role.RATED, nom=U.A(1)),))


def test_fuse_holder_pins_per_pole_are_proposed_golden():
    holder = FuseHolder(poles=3)
    assert _markings(holder) == list("123456")
    assert [link.markings for link in holder.links] == [("1", "2"), ("3", "4"), ("5", "6")]
    assert {link.kind for link in holder.links} == {LinkKind.PROTECTIVE}
    assert _markings(replace(holder, poles=1)) == ["1", "2"]


def test_fuse_and_holder_store_no_pins():
    for cls in (Fuse, FuseHolder):
        assert not {item.name for item in fields(cls)} & {"pins", "links"}


def test_fuse_holder_poles_zero_raises():
    with pytest.raises(TypeError):
        FuseHolder(poles=0)


def test_breaker_pole_pins_are_proposed_golden():
    breaker = Breaker(poles=2, curve=TripCurve.C)
    assert _markings(breaker) == list("1234")
    assert {link.kind for link in breaker.links} == {LinkKind.PROTECTIVE}
    assert _markings(replace(breaker, poles=1)) == ["1", "2"]
    assert Breaker.needs == ("current", "curve")


def test_breaker_aux_follow_the_poles_numbered_aux():
    breaker = Breaker(poles=2, aux=(BREAK, MAKE))
    first = contact_pins(ContactForm.BREAK, 1, M.AUX)
    second = contact_pins(ContactForm.MAKE, 2, M.AUX)
    assert _markings(breaker) == ["1", "2", "3", "4", *(p.marking for p in first[0] + second[0])]
    assert breaker.links[2:] == first[1] + second[1]
    assert [p.marking for p in first[0] + second[0]] == ["11", "12", "23", "24"]


def test_breaker_kind_check_and_no_stored_pins():
    with pytest.raises(TypeError):
        Breaker(icn=U.V(6))  # ty: ignore[invalid-argument-type] - the refusal under test
    assert not {item.name for item in fields(Breaker)} & {"pins", "links"}


@pytest.mark.parametrize("poles", [True, "2", 1.5])
def test_fuse_holder_poles_not_an_int_raises(poles):
    with pytest.raises(TypeError):
        FuseHolder(poles=poles)
