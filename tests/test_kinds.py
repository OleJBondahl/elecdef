"""Block figures are checked for kind at construction, and every src block states its kinds (E4)."""

import importlib
import pkgutil
from dataclasses import dataclass, fields, is_dataclass
from typing import get_type_hints

import pytest

from elecdef import Range, Role
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef._block import Block, figure
from elecdef._quantity import Kind, Quantity
from elecdef._range import Ranges


@dataclass(frozen=True)
class Sample(Block):
    width: Quantity | None = figure(Kind.LENGTH)  # noqa: RUF009 - figure() is the field metadata
    voltage: Ranges = figure(Kind.VOLTAGE, many=True)  # noqa: RUF009 - figure() is the field metadata
    setting: Range | None = figure(Kind.CURRENT, Kind.VOLTAGE)  # noqa: RUF009 - field metadata


@dataclass(frozen=True)
class Bare(Block):
    width: Quantity | None = None


@dataclass(frozen=True)
class Checked(Sample):
    def __post_init__(self) -> None:
        super().__post_init__()


def _rated(volts: int) -> Range:
    return Range(Role.RATED, max=U.V(volts))


def test_right_kind_is_accepted():
    sample = Sample(width=U.M(2), voltage=(_rated(24),))
    assert sample.width == U.M(2)


def test_wrong_kind_quantity_raises():
    with pytest.raises(TypeError):
        Sample(width=U.V(5))


def test_wrong_kind_range_in_many_field_raises():
    with pytest.raises(TypeError):
        Sample(voltage=(Range(Role.RATED, max=U.A(5)),))


def test_bare_range_is_wrapped_to_a_tuple():
    rated = _rated(24)
    assert Sample(voltage=rated).voltage == (rated,)  # ty: ignore[invalid-argument-type] - a bare Range is wrapped on purpose


def test_tuple_of_range_is_kept():
    ranges = (_rated(24), _rated(48))
    assert Sample(voltage=ranges).voltage == ranges


def test_defaults_are_empty():
    sample = Sample()
    assert sample.width is None
    assert sample.voltage == ()


def test_field_with_two_kinds_accepts_either():
    assert Sample(setting=Range(Role.RATED, max=U.A(5))).setting is not None
    assert Sample(setting=Range(Role.RATED, max=U.KV(1))).setting is not None
    with pytest.raises(TypeError):
        Sample(setting=Range(Role.RATED, max=U.M(1)))


def test_non_figure_value_raises():
    with pytest.raises(TypeError):
        Sample(width="2")  # ty: ignore[invalid-argument-type] - the test feeds a str on purpose


def test_non_tuple_non_range_for_many_field_raises():
    with pytest.raises(TypeError):
        Sample(voltage=[_rated(24)])  # ty: ignore[invalid-argument-type] - a list is refused on purpose


def test_subclass_post_init_still_checks():
    with pytest.raises(TypeError):
        Checked(width=U.V(5))


def src_dataclasses() -> list[type]:
    """Every dataclass defined under src/elecdef, found by walking the package."""
    package = importlib.import_module("elecdef")
    names = [info.name for info in pkgutil.walk_packages(package.__path__, "elecdef.")]
    modules = [package, *(importlib.import_module(name) for name in names)]
    return [
        obj
        for module in modules
        for obj in vars(module).values()
        if isinstance(obj, type) and is_dataclass(obj) and obj.__module__.startswith("elecdef")
    ]


def missing_kinds(classes: list[type]) -> list[str]:
    """The `Class.field` of each Block subclass whose figure field has no `kinds` metadata."""
    found = []
    for cls in classes:
        if not (isinstance(cls, type) and is_dataclass(cls) and issubclass(cls, Block)):
            continue
        hints = get_type_hints(cls)
        for item in fields(cls):
            if "kinds" in item.metadata:
                continue
            text = str(hints.get(item.name, ""))
            if "Quantity" in text or "Range" in text:
                found.append(f"{cls.__qualname__}.{item.name}")
    return found


def test_every_src_figure_states_its_kinds():
    assert missing_kinds(src_dataclasses()) == []


def test_missing_kinds_can_fail():
    assert missing_kinds([Sample]) == []
    assert missing_kinds([Bare]) == ["Bare.width"]


@dataclass(frozen=True)
class Plain(Block):
    count: int = 0


def test_a_field_without_a_figure_is_left_alone():
    assert Plain(count=3).count == 3
