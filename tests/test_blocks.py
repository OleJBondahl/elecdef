"""E9, E12, E15, E17 and the R14 `needs` table, read over every dataclass of the catalogue.

E15 (no supplier, price, footprint, class_letter or description field) lives here;
the Product test file does not repeat it.
"""

import importlib
import pkgutil
from collections.abc import Sequence
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, get_type_hints

import elecdef
from elecdef import Coil, Connection, IssueCode, Symbol, check
from elecdef._block import Block
from elecdef.terminal import TerminalBlock


def _dataclasses() -> list[type]:
    """Every dataclass defined in an `elecdef` module, once, ordered by name."""
    found: dict[type, None] = {}
    for info in pkgutil.walk_packages(elecdef.__path__, "elecdef."):
        if info.name.endswith("__main__"):
            continue
        module = importlib.import_module(info.name)
        for member in vars(module).values():
            if (
                isinstance(member, type)
                and is_dataclass(member)
                and member.__module__.startswith("elecdef")
            ):
                found[member] = None
    return sorted(found, key=lambda cls: cls.__name__)


def _blocks() -> list[type[Block]]:
    """The catalogue blocks: every dataclass that subclasses Block, Block itself left out."""
    return [c for c in _dataclasses() if issubclass(c, Block) and c is not Block]


def _names(cls: Any) -> set[str]:
    return {item.name for item in fields(cls)}


def _bad_mro(classes: Sequence[type]) -> list[str]:
    return [c.__name__ for c in classes if c.__mro__ != (c, Block, object)]


def test_e9_every_block_has_the_flat_mro() -> None:
    """Block is the one base: no catalogue block subclasses another."""
    assert len(_blocks()) == 26
    assert _bad_mro(_blocks()) == []


def test_e9_application_subclass_is_unknown_class() -> None:
    """A subclass of a block defined outside elecdef is reported UNKNOWN_CLASS."""

    @dataclass(frozen=True)
    class Mine(Coil):
        pass

    assert IssueCode.UNKNOWN_CLASS in {issue.code for issue in check(Mine())}


def test_e9_checker_can_fail() -> None:
    """The MRO helper rejects a subclass of a block."""

    @dataclass(frozen=True)
    class Mine(Coil):
        pass

    assert _bad_mro([Mine]) == ["Mine"]


_CONNECTION = {
    "Coil",
    "Contact",
    "SupplyInput",
    "ChannelGroup",
    "Fuse",
    "FuseHolder",
    "Breaker",
    "Overload",
    "PowerSupply",
    "Connector",
    "Device",
}


def _sides(classes: Sequence[type]) -> set[str]:
    return {c.__name__ for c in classes if "sides" in _names(c)}


def _with_connection(classes: Sequence[type]) -> set[str]:
    return {c.__name__ for c in classes if "connection" in _names(c)}


def test_e12_connection_partition() -> None:
    """Exactly the eleven blocks hold `connection`; TerminalBlock alone holds `sides`."""
    assert _with_connection(_blocks()) == _CONNECTION
    assert _sides(_blocks()) == {"TerminalBlock"}
    assert get_type_hints(TerminalBlock)["sides"] == tuple[Connection, ...]


def test_e12_checker_can_fail() -> None:
    """A fake block with `connection` or `sides` is outside the partition."""

    @dataclass(frozen=True)
    class Fake(Block):
        connection: Connection | None = None
        sides: tuple[Connection, ...] = ()

    assert _with_connection([*_blocks(), Fake]) != _CONNECTION
    assert _sides([*_blocks(), Fake]) != {"TerminalBlock"}


_E15 = {"supplier", "price", "footprint", "class_letter", "description"}
_E17 = {"geometry", "port", "outline", "glyph"}


def _named(classes: Sequence[type], names: set[str]) -> list[str]:
    return [f"{c.__name__}.{n}" for c in classes for n in sorted(_names(c) & names)]


def test_e15_no_vendor_field_anywhere() -> None:
    """No dataclass, block or plain, has a supplier, price, footprint, class or description."""
    assert len(_dataclasses()) > 30
    assert _named(_dataclasses(), _E15) == []


def test_e15_checker_can_fail() -> None:
    """The name scan flags a fake dataclass holding a price."""

    @dataclass(frozen=True)
    class Fake:
        price: int = 0

    assert _named([Fake], _E15) == ["Fake.price"]


_SYMBOL = {
    "Coil",
    "Contact",
    "Fuse",
    "FuseHolder",
    "Breaker",
    "Overload",
    "PowerSupply",
    "TerminalBlock",
    "Connector",
    "ContactBlock",
    "Channel",
    "Device",
}


def _symbol_holders(classes: Sequence[type]) -> set[str]:
    return {c.__name__ for c in classes if "symbol" in _names(c)}


def _bad_symbol_type(classes: Sequence[type]) -> list[str]:
    return [
        c.__name__
        for c in classes
        if "symbol" in _names(c) and get_type_hints(c)["symbol"] != Symbol | None
    ]


def test_e17_no_geometry_field() -> None:
    """No dataclass field is named geometry, port, outline or glyph (`Port`, `ports` are fine)."""
    assert _named(_dataclasses(), _E17) == []


def test_e17_symbol_field() -> None:
    """A `symbol` field is `Symbol | None` and sits on exactly the twelve drawn blocks."""
    assert _symbol_holders(_dataclasses()) == _SYMBOL
    assert _bad_symbol_type(_dataclasses()) == []


def test_e17_checker_can_fail() -> None:
    """The scans flag a geometry field, a stray symbol holder and a bad symbol type."""

    @dataclass(frozen=True)
    class Fake:
        geometry: int = 0
        symbol: str | None = None

    assert _named([Fake], _E17) == ["Fake.geometry"]
    assert _symbol_holders([*_dataclasses(), Fake]) != _SYMBOL
    assert _bad_symbol_type([Fake]) == ["Fake"]


_NEEDS = {
    "Contact": ("switching",),
    "Coil": ("voltage",),
    "Relay": ("contacts",),
    "Overload": ("setting",),
    "Fuse": ("current",),
    "Breaker": ("current", "curve"),
    "PowerSupply": ("output_voltage", "output_current"),
    "PlcCard": ("groups",),
    "TerminalBlock": ("levels",),
    "Conductor": ("area",),
    "Cable": ("cores",),
}


def test_needs_match_the_r14_table() -> None:
    """Each block's `needs` is the table row, or empty, and names only its own fields."""
    for cls in _blocks():
        assert cls.needs == _NEEDS.get(cls.__name__, ()), cls.__name__
        assert set(cls.needs) <= _names(cls), cls.__name__
    assert {c.__name__ for c in _blocks()} >= set(_NEEDS)
