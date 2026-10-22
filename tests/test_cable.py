"""E-side gate for Conductor, Cable, Core and TypeCode (cable pins are proposed rows)."""

import dataclasses

import pytest

from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef.conductor import Conductor
from elecdef.vocab import Colour


def test_conductor_defaults_are_unfilled() -> None:
    """A bare Conductor holds nothing and needs the area."""
    c = Conductor()
    assert c.area is None
    assert c.colour == ()
    assert Conductor.needs == ("area",)


def test_conductor_takes_area_in_mm2() -> None:
    """An AREA quantity is held as given."""
    assert Conductor(area=U.MM2("1.5"), colour=(Colour.BN,)).area == U.MM2("1.5")


def test_conductor_refuses_a_length_for_area() -> None:
    """A LENGTH quantity for area raises TypeError."""
    with pytest.raises(TypeError):
        Conductor(area=U.M(2))


def test_conductor_is_frozen() -> None:
    """A Conductor cannot be changed after construction."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        Conductor().area = U.MM2(1)  # ty: ignore[invalid-assignment] - frozen on purpose
