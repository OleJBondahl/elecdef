"""E-side F5: no door callable takes, and no dataclass holds, a name from another home."""

import dataclasses
import importlib
import inspect
import pkgutil
from collections.abc import Callable
from typing import Any

import family

import elecdef
from elecdef import Product, check


def _banned() -> set[str]:
    return {n.lower() for n in family.family_config(family.ROOT)["boundary_names"]}


def _door_callables() -> list[tuple[str, Callable]]:
    """Every function, class constructor and public method of a class reached from a door."""
    found = []
    for door in family.family_config(family.ROOT)["doors"]:
        for name in family.door_names(door):
            obj = getattr(importlib.import_module(door), name)
            if not callable(obj):
                continue
            found.append((f"{door}.{name}", obj))
            if inspect.isclass(obj):
                found += [
                    (f"{door}.{name}.{attr}", fn)
                    for attr, fn in inspect.getmembers(obj, inspect.isfunction)
                    if not attr.startswith("_")
                ]
    return found


def _parameter_hits(callables: list[tuple[str, Callable]]) -> list[str]:
    banned = _banned()
    hits = []
    for label, fn in callables:
        try:
            parameters = inspect.signature(fn).parameters
        except ValueError, TypeError:
            continue
        hits += [f"{label}({p})" for p in parameters if p.lower() in banned]
    return hits


def _dataclass_types() -> list[Any]:
    found: dict[type, None] = {}
    for info in pkgutil.walk_packages(elecdef.__path__, "elecdef."):
        if info.name.endswith("__main__"):
            continue
        for member in vars(importlib.import_module(info.name)).values():
            if isinstance(member, type) and dataclasses.is_dataclass(member):
                found[member] = None
    return [c for c in found if c.__module__.startswith("elecdef")]


def _field_hits(classes: list[Any]) -> list[str]:
    banned = _banned()
    return [
        f"{c.__name__}.{f.name}"
        for c in classes
        for f in dataclasses.fields(c)
        if f.name.lower() in banned
    ]


def test_no_door_callable_takes_a_foreign_name() -> None:
    """No door function, constructor or public method has a parameter from boundary_names."""
    callables = _door_callables()
    assert len(callables) > 30
    assert _parameter_hits(callables) == []


def test_check_and_product_take_no_coordinate() -> None:
    """`check` and `Product` take no x, y, page, tag, svg or designation."""
    banned = _banned()
    assert banned >= {"x", "y", "page"}
    assert not banned & set(inspect.signature(check).parameters)
    assert not banned & set(inspect.signature(Product).parameters)


def test_no_dataclass_field_is_a_foreign_name() -> None:
    """No field of any Product or Block, or other dataclass, is a boundary name."""
    assert _field_hits(_dataclass_types()) == []


def test_checker_can_fail() -> None:
    """The scans flag a function with a parameter `x` and a dataclass with a field `page`."""

    def fake(x: int) -> int:
        return x

    @dataclasses.dataclass(frozen=True)
    class Fake:
        page: int = 0

    assert _parameter_hits([("fake", fake)]) == ["fake(x)"]
    assert _field_hits([Fake]) == ["Fake.page"]
