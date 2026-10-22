"""The thirteen leaf connections state their technology only (E13); blocks check at construction."""

from dataclasses import MISSING, fields, replace

import pytest

from elecdef import Range, Role, connections
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._product import Symbol
from elecdef._rating import Rating
from elecdef.vocab import Technology

NAMES = [
    "SCREW",
    "SPRING_CAGE",
    "PUSH_IN",
    "TENSION",
    "IDC",
    "CRIMP",
    "SOLDER",
    "PRESS_IN",
    "PLUG_IN",
    "BOLT",
    "WIRE_WRAP",
    "THT",
    "SMD",
]


def unfilled(leaf: Connection) -> list[str]:
    """Names of the fields, other than technology, whose value differs from the field default."""
    filled = []
    for item in fields(leaf):
        if item.name == "technology":
            continue
        if item.default is not MISSING:
            default = item.default
        elif item.default_factory is not MISSING:
            default = item.default_factory()
        else:
            default = MISSING
        if getattr(leaf, item.name) != default:
            filled.append(item.name)
    return filled


def test_every_leaf_states_only_its_technology():
    for name in NAMES:
        leaf = getattr(connections, name)
        assert leaf.technology is Technology[name]
        assert unfilled(leaf) == []


def test_all_is_the_thirteen_names():
    assert sorted(connections.__all__) == sorted(NAMES)
    assert len(connections.__all__) == 13


def test_leaves_are_distinct():
    leaves = [getattr(connections, name) for name in NAMES]
    assert len({id(leaf) for leaf in leaves}) == 13
    assert len({leaf.technology for leaf in leaves}) == 13


def test_unfilled_can_fail():
    torque = Range(Role.RATED, nom=U.N_M(1))
    assert unfilled(replace(connections.SCREW, torque=torque)) == ["torque"]
    assert unfilled(replace(connections.SCREW, strip_length=U.M(1))) == ["strip_length"]


def test_replace_leaves_the_constant_alone():
    replace(connections.SCREW, torque=Range(Role.RATED, nom=U.N_M(1)))
    assert unfilled(connections.SCREW) == []


def test_connection_wrong_quantity_kind_raises():
    with pytest.raises(TypeError):
        Connection(strip_length=U.V(5))


def test_connection_wrong_range_kind_raises():
    with pytest.raises(TypeError):
        Connection(torque=Range(Role.RATED, max=U.V(1)))


def test_body_wraps_a_bare_range():
    rng = Range(Role.RATED, max=U.DEG_C(40))
    assert Body(temperature=rng).temperature == (rng,)  # ty: ignore[invalid-argument-type] - a bare Range is wrapped on purpose


def test_rating_wrong_kind_raises():
    with pytest.raises(TypeError):
        Rating(frequency=Range(Role.RATED, max=U.V(1)))


def test_symbol_accepts_a_key_and_a_version():
    assert Symbol("k", 1).version == 1


@pytest.mark.parametrize(("key", "version"), [(1, 1), ("k", True), ("k", "1")])
def test_symbol_refuses_other_types(key, version):
    with pytest.raises(TypeError):
        Symbol(key, version)
