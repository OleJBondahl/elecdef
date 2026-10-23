"""Rating.current (rated current as Ranges) and Rating.power_loss."""

import pytest

from elecdef import At, Range, Rating, Role, Unit, pick
from elecdef.vocab import Current

U = Unit

AC = Range(Role.RATED, max=U.A(16), at=At(Current.AC))
DC = Range(Role.RATED, max=U.A(20), at=At(Current.DC))


def test_current_is_picked_per_current_kind():
    rating = Rating(current=(AC, DC))
    found = pick(rating.current, Current.DC).found
    assert found is not None
    assert found.max == U.A(20)
    assert pick(rating.current, Current.AC).found is AC


def test_a_bare_range_in_current_is_wrapped():
    assert Rating(current=AC).current == (AC,)  # ty: ignore[invalid-argument-type] - a bare Range is wrapped on purpose


def test_a_voltage_range_in_current_is_refused():
    with pytest.raises(TypeError):
        Rating(current=(Range(Role.RATED, max=U.V(24)),))


def test_a_list_in_current_is_refused():
    with pytest.raises(TypeError):
        Rating(current=[AC])  # ty: ignore[invalid-argument-type] - a list is refused on purpose


def test_current_defaults_to_empty_and_thermal_current_is_unchanged():
    assert Rating().current == ()
    assert Rating(thermal_current=AC).thermal_current is AC
