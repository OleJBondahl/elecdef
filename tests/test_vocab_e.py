"""E part: the elecdef allowlist of E1 and the shape of the closed vocabularies."""

import dataclasses
import enum
import importlib
import pkgutil
import typing

import family
import pytest

from elecdef import vocab
from elecdef.vocab._base import Vocab

E1_ALLOWLIST = (
    "marking",
    "alternates",
    "markings",
    "common",
    "mpn",
    "manufacturer",
    "name",
    "key",
    "text",
    "message",
    "subject",
)


def src_dataclasses() -> list[type]:
    """Every dataclass defined under src/elecdef, found by walking the package."""
    package = importlib.import_module("elecdef")
    names = [info.name for info in pkgutil.walk_packages(package.__path__, "elecdef.")]
    modules = [package, *(importlib.import_module(name) for name in names)]
    return [
        obj
        for module in modules
        for obj in vars(module).values()
        if isinstance(obj, type)
        and dataclasses.is_dataclass(obj)
        and obj.__module__.startswith("elecdef")
    ]


def is_text(hint: object) -> bool:
    """True when the hint is `str`, `tuple[str, ...]`, or a union holding either."""
    if hint is str:
        return True
    args = typing.get_args(hint)
    if typing.get_origin(hint) is tuple:
        return str in args
    return any(is_text(arg) for arg in args)


def text_fields(classes: list[type], allowed: tuple[str, ...]) -> list[str]:
    """The `Class.field` of each text field whose name is not in `allowed`."""
    found = []
    for cls in classes:
        hints = typing.get_type_hints(cls)
        found += [
            f"{cls.__qualname__}.{item.name}"
            for item in dataclasses.fields(cls)  # ty: ignore[invalid-argument-type] - cls is a dataclass type
            if item.name not in allowed and is_text(hints[item.name])
        ]
    return found


@dataclasses.dataclass(frozen=True)
class Sample:
    kind: str = ""
    marking: str = ""
    markings: tuple[str, ...] = ()
    other: tuple[str, ...] | None = None
    count: int = 0


def test_e1_list_equals_pyproject():
    assert tuple(family.family_config()["str_allowlist"]) == E1_ALLOWLIST


def test_e1_no_text_field_outside_the_list():
    assert text_fields(src_dataclasses(), E1_ALLOWLIST) == []


def test_e1_check_can_fail():
    assert text_fields([Sample], E1_ALLOWLIST) == ["Sample.kind", "Sample.other"]


def exported_enums() -> list[type[enum.Enum]]:
    return [getattr(vocab, name) for name in vocab.__all__]


def test_every_export_is_an_enum_and_all_but_kind_are_vocab():
    for item in exported_enums():
        assert issubclass(item, enum.Enum)
        assert item is vocab.Kind or issubclass(item, Vocab)


@pytest.mark.parametrize("item", [e for e in exported_enums() if issubclass(e, Vocab)])
def test_members_have_unique_names_and_a_text_gloss(item):
    names = [member.name for member in item]
    assert names
    assert len(names) == len(set(names))
    assert all(isinstance(member.gloss, str) for member in item)


def test_vocab_values_are_running_integers():
    assert [m.value for m in vocab.Current] == [1, 2]


@pytest.mark.parametrize(
    ("text", "mark"),
    [
        ("L1", "L1"), ("L2", "L2"), ("L3", "L3"), ("N", "N"), ("L+", "L_PLUS"), ("L-", "L_MINUS"),
        ("M", "M"), ("PE", "PE"), ("U", "L1"), ("V", "L2"), ("W", "L3"), ("U1", "L1"),
        ("+", "L_PLUS"), ("-", "L_MINUS"),
    ],
)  # fmt: skip
def test_conductor_mark_names_a_marking(text: str, mark: str) -> None:
    """Each printed marking and terminal letter names its conductor; the others name none."""
    assert vocab.ConductorMark.of(text) is vocab.ConductorMark[mark]


def test_conductor_mark_refuses_other_text_and_prints_back() -> None:
    """An unknown text, a case slip and the empty text name none; `marking` prints each member."""
    assert [vocab.ConductorMark.of(t) for t in ("13", "l1", "", "X")] == [None] * 4
    assert all(vocab.ConductorMark.of(m.marking) is m for m in vocab.ConductorMark)
    assert {m.marking for m in vocab.ConductorMark} == {
        "L1",
        "L2",
        "L3",
        "N",
        "L+",
        "L-",
        "M",
        "PE",
    }


def test_a_vocab_row_holds_a_gloss_only_unless_the_class_reads_more() -> None:
    """A row with extra fields in a class with no `__init__` of its own is a TypeError."""
    with pytest.raises(TypeError, match="gloss only"):

        class _Bad(Vocab):
            A = ("gloss", 1)

    assert vocab.Signal.DO.output
