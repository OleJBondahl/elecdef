"""E12 gate (SupplyInput half): a supply block draws voltage and current, and holds its pins."""

import dataclasses

import pytest

import elecdef.connections
from elecdef import Range, Role
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef.pins import Pin, PinRole
from elecdef.supply import SupplyInput


def test_default_pins_are_plus_and_minus() -> None:
    """The default pins are exactly a plus and a minus, with no side."""
    pins = SupplyInput().pins
    assert [(pin.marking, pin.role, pin.side) for pin in pins] == [
        ("+", PinRole.PLUS, None),
        ("-", PinRole.MINUS, None),
    ]


def test_defaults_are_empty() -> None:
    """Voltage and current default to an empty tuple, and the connection to None."""
    supply = SupplyInput()
    assert supply.voltage == ()
    assert supply.current == ()
    assert supply.connection is None


def test_voltage_range_is_wrapped_into_a_tuple() -> None:
    """A bare voltage Range is accepted and held as a 1-tuple."""
    rng = Range(Role.RATED, nom=U.V(24))
    supply = SupplyInput(
        voltage=rng,  # ty: ignore[invalid-argument-type] - a bare Range is wrapped on purpose
    )
    assert supply.voltage == (rng,)


def test_current_range_in_voltage_is_refused() -> None:
    """A current-kind Range in `voltage` is a TypeError (E4)."""
    current = Range(Role.RATED, nom=U.A(2))
    with pytest.raises(TypeError):
        SupplyInput(voltage=current)  # ty: ignore[invalid-argument-type] - refused on purpose


def test_replacing_connection_keeps_pins() -> None:
    """Setting the connection to the screw leaf keeps the default pins."""
    supply = dataclasses.replace(SupplyInput(), connection=elecdef.connections.SCREW)
    assert supply.connection == elecdef.connections.SCREW
    assert supply.pins == SupplyInput().pins


def test_given_pins_are_kept() -> None:
    """Pins given as L, N and PE are held as given."""
    pins = (Pin("L", PinRole.SUPPLY), Pin("N", PinRole.SUPPLY), Pin("PE", PinRole.PE))
    assert SupplyInput(pins=pins).pins == pins
