"""Family gate wrappers."""

import importlib
import shutil
from pathlib import Path

import family
import pytest

from elecdef import Coil
from elecdef._block import Block


def test_f8_snapshot_and_docs():
    family.gate_f8()


def _f8_copy(tmp_path: Path) -> Path:
    """A tmp copy of what gate_f8 reads, with an empty tests/guide."""
    for name in ("src", "docs"):
        shutil.copytree(
            family.ROOT / name, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__")
        )
    shutil.copy(family.ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    (tmp_path / "tests" / "guide" / "__pycache__").mkdir(parents=True)
    return tmp_path


def test_f8_skips_bytecode_but_still_fails_a_private_import(tmp_path):
    root = _f8_copy(tmp_path)
    (root / "tests" / "guide" / "__pycache__" / "x.pyc").write_bytes(b"\xff\xfe\x80\x00")
    family.gate_f8(root)
    lib = family.lib_name(root)
    (root / "tests" / "guide" / "test_g.py").write_text(
        f"from {lib}._private import x\n", encoding="utf-8"
    )
    with pytest.raises(AssertionError, match="private or unexported"):
        family.gate_f8(root)


def test_f15_no_arithmetic():
    family.gate_f15()


def test_doors_match_config():
    family.gate_doors()


ORDER = ("__lt__", "__le__", "__gt__", "__ge__")


def _surface() -> list[tuple[str, object]]:
    """Every name of every door, with its object."""
    return [
        (name, getattr(importlib.import_module(door), name))
        for door in family.family_config(family.ROOT)["doors"]
        for name in family.door_names(door)
    ]


def _returns_bool(obj: object) -> bool:
    """True when a function, or the getter of a property, is annotated `-> bool`."""
    func = obj.fget if isinstance(obj, property) else obj
    return getattr(func, "__annotations__", {}).get("return") in (bool, "bool")


def bool_callables(named: list[tuple[str, object]]) -> set[str]:
    """`Class.method` of each elecdef class function annotated bool, and each module one."""
    found = set()
    for name, obj in named:
        if isinstance(obj, type):
            for klass in obj.__mro__:
                if not klass.__module__.startswith("elecdef"):
                    continue
                for attr, value in vars(klass).items():
                    if attr not in ("__eq__", "__ne__") and _returns_bool(value):
                        found.add(f"{klass.__name__}.{attr}")
        elif callable(obj) and _returns_bool(obj):
            found.add(name)
    return found


def arithmetic_sites(named: list[tuple[str, object]]) -> list[str]:
    """`Class.dunder` for each arithmetic dunder in a surface class's non-builtin MRO."""
    return [
        f"{klass.__name__}.{dunder}"
        for _, obj in named
        if isinstance(obj, type)
        for klass in obj.__mro__
        if klass.__module__ != "builtins"
        for dunder in sorted(family.ARITHMETIC.intersection(vars(klass)))
    ]


def order_sites(named: list[tuple[str, object]]) -> list[str]:
    """`Class.dunder` of each ordering dunder an elecdef surface class defines in its own vars."""
    return [
        f"{obj.__name__}.{dunder}"
        for _, obj in named
        if isinstance(obj, type) and obj.__module__.startswith("elecdef")
        for dunder in ORDER
        if dunder in vars(obj)
    ]


def test_e8_bool_callables_are_the_predicates():
    assert bool_callables(_surface()) == {
        "Quantity.same",
        "Quantity.__lt__",
        "Quantity.__le__",
        "Quantity.__gt__",
        "Quantity.__ge__",
        "Range.contains",
        "Range.covers",
        "At.covers",
    }


def test_e8_checker_can_fail():
    class Fake:
        __module__ = "elecdef._fake"

        def acceptable(self) -> bool:
            return True

    assert "Fake.acceptable" in bool_callables([("Fake", Fake)])


def _verdict(_self: object) -> bool:
    return True


def _string_verdict(_self: object) -> "bool":  # noqa: UP037 - the string annotation is the test
    return True


@pytest.mark.parametrize(
    "member",
    [_verdict, _string_verdict, property(_verdict), classmethod(_verdict), staticmethod(_verdict)],
    ids=["method", "string annotation", "property", "classmethod", "staticmethod"],
)
def test_e8_sees_a_bool_member_added_to_block(member, monkeypatch):
    """A `-> bool` member added to Block shows on every surface class that inherits it."""
    monkeypatch.setattr(Block, "acceptable", member, raising=False)
    assert "Block.acceptable" in bool_callables([("Coil", Coil)])


def test_e18_no_arithmetic_on_surface_classes():
    assert arithmetic_sites(_surface()) == []


def test_e18_only_quantity_orders():
    assert set(order_sites(_surface())) == {f"Quantity.{dunder}" for dunder in ORDER}


def test_e18_checker_can_fail():
    class FakeAdd:
        __module__ = "elecdef._fake"

        def __add__(self, other: object) -> object:
            return self

    class FakeLess:
        __module__ = "elecdef._fake"

        def __lt__(self, other: object) -> bool:
            return True

    assert arithmetic_sites([("FakeAdd", FakeAdd)]) == ["FakeAdd.__add__"]
    assert order_sites([("FakeLess", FakeLess)]) == ["FakeLess.__lt__"]
