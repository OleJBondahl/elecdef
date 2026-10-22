"""Relay, Contactor and ContactBlock: golden pins and links, mirror, shared leaves, no mutation."""

from dataclasses import replace

import pytest

from elecdef import Range, Role
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef._coil import Coil
from elecdef._contact import Contact
from elecdef._relay import ContactBlock, Contactor, Relay
from elecdef.connections import SCREW
from elecdef.pins import Pin, PinRole
from elecdef.vocab import (
    CoilKind,
    ContactFeature,
    ContactForm,
    RelayKind,
    Suppression,
)

SCREW_M3 = replace(SCREW, strip_length=U.MM(7))
COIL = Coil(
    CoilKind.DC,
    connection=SCREW_M3,
    suppression=Suppression.DIODE,
    voltage=Range(Role.RATED, nom=U.V(24)),
)
CO = Contact(ContactForm.CHANGEOVER, connection=SCREW_M3)
MAIN = Contact(ContactForm.MAKE)
MIRROR_NC = Contact(ContactForm.BREAK, features=frozenset({ContactFeature.MIRROR}))
RELAY = Relay(contacts=(CO, CO), coil=COIL)


def _markings(block) -> list[str]:
    return [pin.marking for pin in block.pins]


def _pairs(block) -> list[tuple[str, ...]]:
    return [link.markings for link in block.links]


def test_relay_pins_and_links_are_golden():
    assert _markings(RELAY) == ["A1", "A2", "11", "12", "14", "21", "22", "24"]
    assert RELAY.pins[0].role is PinRole.PLUS
    assert _pairs(RELAY) == [("11", "12"), ("11", "14"), ("21", "22"), ("21", "24")]
    assert [link.closed_at_rest for link in RELAY.links] == [True, False, True, False]


def test_relay_states_that_it_needs_contacts():
    assert Relay.needs == ("contacts",)


def test_the_connection_is_shared_by_identity():
    assert COIL.connection is CO.connection
    assert RELAY.coil.connection is RELAY.contacts[0].connection


def test_reading_pins_leaves_the_library_contact_unchanged():
    _ = RELAY.pins
    assert Contact(ContactForm.CHANGEOVER, connection=SCREW_M3) == CO
    assert CO.number is None
    assert CO.scheme is None
    assert CO.own_pins == ()
    assert RELAY.contacts == (CO, CO)


def test_a_timer_relay_renumbers_to_the_timer_scheme():
    timer = replace(RELAY, kind=RelayKind.TIMER)
    assert _markings(timer) == ["A1", "A2", "15", "16", "18", "25", "26", "28"]
    assert _markings(replace(timer, kind=RelayKind.ELECTROMECHANICAL)) == _markings(RELAY)


def test_a_relay_without_a_coil_has_only_contact_pins():
    assert _markings(Relay(contacts=(Contact(ContactForm.MAKE),))) == ["13", "14"]


def test_a_contact_with_own_pins_keeps_them_in_a_relay():
    given = (Pin("X1", PinRole.MAKE), Pin("X2", PinRole.MAKE))
    relay = Relay(contacts=(Contact(ContactForm.MAKE, own_pins=given), MAIN))
    assert _markings(relay) == ["X1", "X2", "23", "24"]


def test_more_than_nine_contacts_fail_at_construction():
    with pytest.raises(TypeError):
        Relay(contacts=(MAIN,) * 10)


CONTACTOR = Contactor(COIL, (MAIN, MAIN, MAIN), (MIRROR_NC,))


def test_contactor_pins_are_golden():
    assert _markings(CONTACTOR) == [
        "A1", "A2", "1/L1", "2/T1", "3/L2", "4/T2", "5/L3", "6/T3", "11", "12",
    ]  # fmt: skip
    assert _pairs(CONTACTOR) == [
        ("1/L1", "2/T1"), ("3/L2", "4/T2"), ("5/L3", "6/T3"), ("11", "12"),
    ]  # fmt: skip
    assert CONTACTOR.links[-1].closed_at_rest is True


def test_contactor_mirror_is_a_feature_of_an_auxiliary():
    assert ContactFeature.MIRROR in CONTACTOR.aux[0].features
    assert all(ContactFeature.MIRROR not in main.features for main in CONTACTOR.main)


def test_contactor_main_is_numbered_before_aux():
    swapped = Contactor(COIL, (MAIN,), (MAIN, MIRROR_NC))
    assert _markings(swapped)[2:] == ["1/L1", "2/T1", "13", "14", "21", "22"]


def test_a_non_make_main_contact_is_refused_at_construction():
    with pytest.raises(TypeError):
        Contactor(COIL, (MAIN, MIRROR_NC))


def test_contactor_shares_the_coil_connection_by_identity():
    contactor = Contactor(COIL, (replace(MAIN, connection=COIL.connection),))
    assert contactor.coil.connection is contactor.main[0].connection


def test_contact_block_numbers_from_numbered_from():
    block = ContactBlock((Contact(ContactForm.MAKE), Contact(ContactForm.BREAK)), numbered_from=5)
    assert _markings(block) == ["53", "54", "61", "62"]
    assert _pairs(block) == [("53", "54"), ("61", "62")]
    assert _markings(replace(block, numbered_from=1)) == ["13", "14", "21", "22"]


def test_contact_block_past_nine_fails_at_construction():
    with pytest.raises(TypeError):
        ContactBlock((MAIN, MAIN), numbered_from=9)
