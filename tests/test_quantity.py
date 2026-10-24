"""E2 and E3: exact figures, units of one kind, no float."""

import decimal
import itertools
from decimal import Decimal

import pytest

from elecdef import Quantity, Unit
from elecdef.vocab import Kind

U = Unit

PAIRS = [(a, b) for a, b in itertools.permutations(U, 2) if a.kind is not b.kind]
SAME_KIND = [(a, b) for a, b in itertools.permutations(U, 2) if a.kind is b.kind]


def test_a_float_is_refused():
    with pytest.raises(TypeError):
        U.V(1.5)  # ty: ignore[invalid-argument-type] - the refusal under test
    with pytest.raises(TypeError):
        Quantity(1.5, U.V)  # ty: ignore[invalid-argument-type] - the refusal under test


def test_a_bool_and_junk_are_refused():
    for bad in (True, None, "abc", "NaN", Decimal("Infinity"), [1]):
        with pytest.raises(TypeError):
            U.V(bad)  # ty: ignore[invalid-argument-type] - the refusal under test


def test_int_str_and_decimal_are_accepted():
    assert U.V(24) == U.V("24") == U.V(Decimal(24))
    assert U.MM2("2.5").value == Decimal("2.5")


def test_equality_is_as_written_and_same_is_in_base_units():
    assert U.V(24) != U.MV(24000)
    assert U.V(24).same(U.MV(24000))
    assert U.V(24) == U.V("24.0")


def test_to_converts_within_a_kind():
    assert U.KV(1).to(U.V).value == 1000
    assert U.MV(1500).to(U.V).value == Decimal("1.5")
    assert U.PCT(75).to(U.PPM).value == 750000
    assert U.V(24).to(U.V) == U.V(24)


def test_ordering_is_in_base_units():
    assert U.V(1) < U.KV(1)
    assert U.KV(1) > U.V(999)
    assert U.V(1) <= U.MV(1000)
    assert U.V(1) >= U.MV(1000)
    assert not U.V(1) < U.MV(1000)


def test_every_factor_is_finite_and_positive():
    for unit in U:
        assert isinstance(unit.factor, Decimal)
        assert unit.factor.is_finite()
        assert unit.factor > 0


def test_every_cross_kind_pair_is_refused():
    assert len(PAIRS) > 400
    for a, b in PAIRS:
        with pytest.raises(TypeError):
            a(1).to(b)
        with pytest.raises(TypeError):
            a(1).same(b(1))
        with pytest.raises(TypeError):
            _ = a(1) < b(1)


def test_every_same_kind_pair_converts_back_exactly():
    for a, b in SAME_KIND:
        assert a(7).to(b).to(a).same(a(7))
        assert a(7).to(b).same(a(7))


def test_the_callers_decimal_context_is_not_used():
    with decimal.localcontext() as ctx:
        ctx.prec = 3
        assert U.KV("1.2345").base() == Decimal("1234.5")
        assert U.KV("1.2345").to(U.V).value == Decimal("1234.5")


def test_a_non_quantity_is_refused_by_same_and_ordering():
    with pytest.raises(TypeError):
        U.V(1).same(1)  # ty: ignore[invalid-argument-type] - the refusal under test
    with pytest.raises(TypeError):
        _ = U.V(1) < 1  # ty: ignore[unsupported-operator] - the refusal under test
    with pytest.raises(TypeError):
        U.V(1).to("V")  # ty: ignore[invalid-argument-type] - the refusal under test


def test_a_quantity_needs_a_decimal_and_a_unit():
    with pytest.raises(TypeError):
        Quantity(1, U.V)  # ty: ignore[invalid-argument-type] - the refusal under test
    with pytest.raises(TypeError):
        Quantity(Decimal(1), "V")  # ty: ignore[invalid-argument-type] - the refusal under test


def test_ampere_hour_is_charge_and_prints_as_ah():
    capacity = U.AH("2.5")
    assert U.AH.symbol == "Ah"
    assert U.AH.kind is Kind.CHARGE
    assert capacity == Quantity(Decimal("2.5"), U.AH)
    assert capacity.unit.symbol == "Ah"
    with pytest.raises(TypeError):
        capacity.to(U.A)
