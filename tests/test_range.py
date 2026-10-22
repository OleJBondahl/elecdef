"""RULE E5: a Range is built from one role and keyword ends, with no second constructor."""

import ast
import pathlib
from fractions import Fraction

import pytest

from elecdef import At, Range, Role
from elecdef import Unit as U  # noqa: N817  # the brief fixes the U alias for Unit
from elecdef.vocab import Current, Kind

RANGE_SRC = pathlib.Path(__file__).resolve().parent.parent / "src" / "elecdef" / "_range.py"


def _class_decorators(source: str) -> list[str]:
    """The decorator names on the methods of `class Range` in a source string."""
    tree = ast.parse(source)
    names = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Range":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    names.extend(ast.unparse(deco) for deco in item.decorator_list)
    return names


def test_role_and_end_are_required() -> None:
    with pytest.raises(TypeError):
        Range(nom=U.V(24))  # ty: ignore[missing-argument]  # role missing on purpose
    with pytest.raises(TypeError):
        Range(Role.RATED)


def test_ends_share_one_kind() -> None:
    with pytest.raises(TypeError):
        Range(Role.RATED, min=U.V(1), max=U.A(2))


def test_ends_are_keyword_only() -> None:
    with pytest.raises(TypeError):
        Range(Role.RATED, U.V(1))  # ty: ignore[too-many-positional-arguments]  # positional end on purpose


def test_tolerance_is_exact_fractions() -> None:
    rng = Range(Role.RATED, nom=U.V(24), min=U.V("20.4"), max=U.V(30))
    assert rng.tolerance == (Fraction(-3, 20), Fraction(1, 4))
    low, high = rng.tolerance
    assert isinstance(low, Fraction)
    assert isinstance(high, Fraction)


def test_tolerance_is_none_without_all_three_or_zero_nom() -> None:
    assert Range(Role.RATED, nom=U.V(24), max=U.V(30)).tolerance is None
    assert Range(Role.RATED, min=U.V(20), max=U.V(30)).tolerance is None
    assert Range(Role.RATED, min=U.V(20), nom=U.V(24)).tolerance is None
    assert Range(Role.RATED, nom=U.V(0), min=U.V(1), max=U.V(2)).tolerance is None


def test_no_classmethod_staticmethod_or_second_constructor() -> None:
    source = RANGE_SRC.read_text(encoding="utf-8")
    decorators = _class_decorators(source)
    assert not {"classmethod", "staticmethod"} & set(decorators)
    tree = ast.parse(source)
    returns = [
        ast.unparse(node.returns)
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.returns is not None
    ]
    assert "Range" not in returns


def test_class_decorators_finds_classmethod_in_literal() -> None:
    literal = "class Range:\n    @classmethod\n    def build(cls):\n        pass\n"
    assert _class_decorators(literal) == ["classmethod"]


def test_contains_within_and_at_ends() -> None:
    rng = Range(Role.RATED, min=U.V(10), max=U.V(30))
    assert rng.contains(U.V(24))
    assert rng.contains(U.MV(24000))
    assert rng.contains(U.V(10))
    assert rng.contains(U.V(30))
    assert not rng.contains(U.V(31))


def test_contains_with_only_max_and_only_nom() -> None:
    assert Range(Role.LIMITING, max=U.V(250)).contains(U.V(12))
    assert not Range(Role.LIMITING, max=U.V(250)).contains(U.V(251))
    point = Range(Role.REFERENCE, nom=U.V(24))
    assert point.contains(U.V(24))
    assert not point.contains(U.V(23))


def test_contains_another_kind_is_type_error() -> None:
    with pytest.raises(TypeError):
        Range(Role.RATED, min=U.V(10), max=U.V(30)).contains(U.A(1))


def test_covers() -> None:
    wide = Range(Role.RATED, min=U.V(10), max=U.V(30))
    assert wide.covers(Range(Role.RATED, min=U.V(12), max=U.V(20)))
    assert wide.covers(wide)
    assert not wide.covers(Range(Role.RATED, min=U.V(5), max=U.V(20)))


def test_open_ended_covers() -> None:
    high = Range(Role.LIMITING, max=U.V(250))
    low = Range(Role.LIMITING, max=U.V(24))
    assert high.covers(low)
    assert not low.covers(high)


def test_covers_another_kind_is_type_error() -> None:
    with pytest.raises(TypeError):
        Range(Role.RATED, min=U.V(10), max=U.V(30)).covers(Range(Role.RATED, max=U.A(1)))


def test_reversed_ends_construct() -> None:
    rng = Range(Role.RATED, min=U.V(30), max=U.V(10))
    assert rng.min == U.V(30)


def test_default_at_and_kind() -> None:
    rng = Range(Role.RATED, nom=U.V(24))
    assert rng.at == At()
    assert rng.kind is Kind.VOLTAGE
    conditioned = Range(Role.RATED, nom=U.A(1), at=At(Current.DC))
    assert conditioned.at == At(Current.DC)
