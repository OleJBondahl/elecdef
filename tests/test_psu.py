"""E4 and E10 gates for PowerSupply; the pin rows are proposed (no source), see the spec."""

import dataclasses

import pytest

from elecdef import Contact, PowerSupply, Range, Role
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef.pins import Pin, PinRole
from elecdef.supply import SupplyInput
from elecdef.vocab import ContactForm

AC_IN = SupplyInput(
    pins=(Pin("L", PinRole.LINE), Pin("N", PinRole.LINE), Pin("PE", PinRole.PE)),
)
OK = Contact(ContactForm.MAKE)
PSU = PowerSupply(input=AC_IN, ok_contact=OK)


def _pins(psu: PowerSupply) -> list[tuple[str, PinRole]]:
    return [(pin.marking, pin.role) for pin in psu.pins]


def test_proposed_pins_input_output_then_ok_contact() -> None:
    """Proposed row: pins `L N PE + - 13 14`, the outputs PLUS and MINUS."""
    assert [marking for marking, _ in _pins(PSU)] == ["L", "N", "PE", "+", "-", "13", "14"]
    roles = dict(_pins(PSU))
    assert roles["+"] is PinRole.PLUS
    assert roles["-"] is PinRole.MINUS
    assert len(PSU.links) == 1


def test_ok_contact_is_not_changed_by_a_read() -> None:
    """The composite numbers a copy on each read; the stored contact keeps no number."""
    _ = PSU.pins
    assert PSU.ok_contact is OK
    assert OK.number is None
    assert OK.scheme is None


def test_no_input_and_no_contact_gives_the_outputs_only() -> None:
    """A bare PowerSupply has the two default output pins and no links."""
    assert _pins(PowerSupply()) == [("+", PinRole.PLUS), ("-", PinRole.MINUS)]
    assert PowerSupply().links == ()


def test_a_third_output_marking_is_a_further_plus() -> None:
    """Choice listed in the hand-back: outputs beyond the second take PLUS; replace reads fresh."""
    psu = dataclasses.replace(PSU, markings=("+", "-", "+12"))
    assert _pins(psu)[3:6] == [("+", PinRole.PLUS), ("-", PinRole.MINUS), ("+12", PinRole.PLUS)]


def test_markings_that_collide_with_the_input_construct() -> None:
    """The clash is reported by `check` (ED-10); construction never raises."""
    psu = PowerSupply(input=SupplyInput(), markings=("+", "-"))
    assert [marking for marking, _ in _pins(psu)] == ["+", "-", "+", "-"]


def test_figures_are_kind_checked() -> None:
    """A current where a voltage is stated is a TypeError (E4); a voltage Range is accepted."""
    with pytest.raises(TypeError):
        PowerSupply(output_voltage=U.A(2))  # ty: ignore[invalid-argument-type] - refused on purpose
    assert PowerSupply(output_voltage=Range(Role.RATED, nom=U.V(24))).output_voltage is not None
    assert PowerSupply.needs == ("output_voltage", "output_current")


def test_markings_must_be_a_tuple_of_str() -> None:
    """Markings that are not a tuple of str are a TypeError."""
    with pytest.raises(TypeError):
        PowerSupply(markings=("+", 1))  # ty: ignore[invalid-argument-type] - refused on purpose


def test_has_no_pins_field() -> None:
    """E10: the pins are a property, never a stored field."""
    assert "pins" not in {item.name for item in dataclasses.fields(PowerSupply)}
