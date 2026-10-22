"""Contact and Coil: kind checks, pins computed on every read, and no stale default pins."""

from dataclasses import replace

import pytest

from elecdef import Range, Role
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef._coil import Coil
from elecdef._contact import Contact
from elecdef.pins import LinkKind, Marking, Pin, PinRole
from elecdef.vocab import CoilKind, ContactForm, Suppression

CO = Contact(ContactForm.CHANGEOVER)


def _markings(block) -> list[str]:
    return [pin.marking for pin in block.pins]


def test_contact_figures_are_checked_for_kind():
    assert Contact(switching=(Range(Role.RATED, nom=U.A(6)),)).switching[0].nom == U.A(6)
    with pytest.raises(TypeError):
        Contact(switching=(Range(Role.RATED, nom=U.V(6)),))
    with pytest.raises(TypeError):
        Contact(voltage=Range(Role.LIMITING, max=U.A(1)))
    with pytest.raises(TypeError):
        Contact(min_load_current=Range(Role.RATED, min=U.V(1)))


def test_contact_states_that_it_needs_switching():
    assert Contact.needs == ("switching",)


def test_an_unnumbered_contact_has_no_pins_and_no_links():
    assert CO.pins == ()
    assert CO.links == ()


def test_a_numbered_contact_computes_its_pins_and_links():
    contact = replace(CO, number=1, scheme=Marking.AUX)
    assert _markings(contact) == ["11", "12", "14"]
    assert [link.markings for link in contact.links] == [("11", "12"), ("11", "14")]
    assert all(link.kind is LinkKind.SWITCHED for link in contact.links)


def test_replace_of_form_renumbers_with_no_stale_pins():
    fresh = Contact(ContactForm.MAKE, number=1, scheme=Marking.AUX)
    changed = replace(CO, number=1, scheme=Marking.AUX, form=ContactForm.MAKE)
    assert _markings(changed) == ["13", "14"]
    assert changed.pins == fresh.pins
    assert changed.links == fresh.links


def test_a_numbered_contact_writes_nothing_into_own_pins():
    contact = replace(CO, number=2, scheme=Marking.AUX)
    assert contact.pins
    assert contact.own_pins == ()


def test_own_pins_win_and_leave_no_links():
    given = (Pin("X1", PinRole.MAKE), Pin("X2", PinRole.MAKE))
    contact = Contact(ContactForm.MAKE, number=1, scheme=Marking.AUX, own_pins=given)
    assert contact.pins == given
    assert contact.links == ()


@pytest.mark.parametrize("number", [0, 10, -1, True, "1"])
def test_a_number_outside_1_to_9_is_refused_at_construction(number):
    with pytest.raises(TypeError):
        Contact(ContactForm.MAKE, number=number)
    with pytest.raises(TypeError):
        Contact(ContactForm.MAKE, number=number, scheme=Marking.AUX)


def test_a_form_the_scheme_refuses_is_refused_at_construction():
    with pytest.raises(TypeError):
        Contact(ContactForm.BREAK, number=1, scheme=Marking.MAIN)


def test_coil_figures_are_checked_for_kind():
    assert Coil(power=Range(Role.RATED, nom=U.W(2))).power[0].nom == U.W(2)
    with pytest.raises(TypeError):
        Coil(power=Range(Role.RATED, nom=U.VA(8)))
    with pytest.raises(TypeError):
        Coil(apparent_power=Range(Role.RATED, nom=U.W(2)))
    with pytest.raises(TypeError):
        Coil(pick_up=Range(Role.LIMITING, max=U.V(5)))
    with pytest.raises(TypeError):
        Coil(power=U.VA(8))


def test_coil_states_that_it_needs_voltage():
    assert Coil.needs == ("voltage",)


def test_a_coil_has_a1_a2_and_no_links():
    coil = Coil(CoilKind.AC)
    assert _markings(coil) == ["A1", "A2"]
    assert [pin.role for pin in coil.pins] == [PinRole.COIL, PinRole.COIL]
    assert coil.links == ()


def test_replace_of_kind_and_suppression_leaves_no_stale_default_pins():
    coil = Coil(CoilKind.AC)
    polar = replace(coil, kind=CoilKind.DC, suppression=Suppression.DIODE)
    assert [pin.role for pin in polar.pins] == [PinRole.PLUS, PinRole.MINUS]
    back = replace(polar, kind=CoilKind.AC)
    assert [pin.role for pin in back.pins] == [PinRole.COIL, PinRole.COIL]
    assert [pin.role for pin in replace(polar, suppression=Suppression.RC).pins] == [
        PinRole.COIL,
        PinRole.COIL,
    ]


def test_the_coil_default_is_not_stored_in_own_pins():
    assert Coil(CoilKind.DC, suppression=Suppression.DIODE).own_pins == ()


def test_coil_own_pins_win():
    given = (Pin("1", PinRole.COIL), Pin("2", PinRole.COIL))
    assert Coil(CoilKind.DC, suppression=Suppression.DIODE, own_pins=given).pins == given
