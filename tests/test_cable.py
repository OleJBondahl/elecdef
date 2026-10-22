"""E-side gate for Conductor, Cable, Core and TypeCode (cable pins are proposed rows)."""

import dataclasses
from dataclasses import replace

import pytest

from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef.cable import Cable, Core, TypeCode
from elecdef.conductor import Conductor
from elecdef.pins import PinRole
from elecdef.tables import CORE_COLOURS
from elecdef.vocab import Colour, CoreRole, Scheme, Screen


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


# Cable and Core pins are proposed rows (spec section 2 "Proposed"): no source proves them.
def test_core_is_built_and_checked() -> None:
    """A Core holds its fields and refuses a str number and a non-int pair."""
    core = Core(number=3, colour=(Colour.BN,), pair=1, role=CoreRole.CORE)
    assert (core.number, core.colour, core.pair, core.conductor) == (3, (Colour.BN,), 1, None)
    with pytest.raises(TypeError):
        Core(number="1")  # ty: ignore[invalid-argument-type] - a str number is refused on purpose
    with pytest.raises(TypeError):
        Core(pair="1")  # ty: ignore[invalid-argument-type] - a str pair is refused on purpose
    with pytest.raises(TypeError):
        Core(colour=("BN",))  # ty: ignore[invalid-argument-type] - a str colour is refused on purpose


def test_type_code_is_built_and_checked() -> None:
    """A TypeCode holds a Scheme and a str; a str scheme or a non-str text raises."""
    assert TypeCode(Scheme.HARMONISED, "H05VV-F").text == "H05VV-F"
    with pytest.raises(TypeError):
        TypeCode("VDE", "x")  # ty: ignore[invalid-argument-type] - a str scheme is refused on purpose
    with pytest.raises(TypeError):
        TypeCode(Scheme.VDE, 5)  # ty: ignore[invalid-argument-type] - an int text is refused on purpose


def test_core_pins_by_number() -> None:
    """The marking of a numbered core is its number as text."""
    cable = Cable(cores=tuple(Core(number=i) for i in (1, 2, 3)))
    assert [(p.marking, p.role) for p in cable.pins] == [
        (str(i), PinRole.SIGNAL) for i in (1, 2, 3)
    ]
    assert cable.links == ()


def test_core_pins_by_colour() -> None:
    """Without a number the marking is the colour names joined."""
    cable = Cable(cores=(Core(colour=(Colour.BN,)), Core(colour=(Colour.GY, Colour.PK))))
    assert [p.marking for p in cable.pins] == ["BN", "GYPK"]


@pytest.mark.parametrize(
    ("screen", "has_sh"),
    [
        (Screen.FOIL, True),
        (Screen.BRAID, True),
        (Screen.FOIL_BRAID, True),
        (Screen.NONE, False),
        (None, False),
    ],
)
def test_sh_pin_follows_the_screen(screen: Screen | None, has_sh: bool) -> None:
    """SH is present for a real screen, last, with the role SCREEN; absent for NONE or unset."""
    pins = Cable(cores=(Core(number=1),), screen=screen).pins
    assert [p.marking for p in pins] == (["1", "SH"] if has_sh else ["1"])
    if has_sh:
        assert pins[-1].role is PinRole.SCREEN


def test_pins_is_not_a_dataclass_field() -> None:
    """E10: pins and links are properties, never stored (the probe target)."""
    names = {f.name for f in dataclasses.fields(Cable)}
    assert "pins" not in names
    assert "links" not in names
    assert Cable(cores=(Core(number=1),)).pins == Cable(cores=(Core(number=1),)).pins


def test_replace_never_leaves_a_stale_pin() -> None:
    """Pins are computed on read, so replace on cores or screen moves them."""
    cable = Cable(cores=(Core(number=1),))
    assert len(replace(cable, screen=Screen.FOIL).pins) == 2
    assert len(replace(cable, cores=(Core(number=1), Core(number=2))).pins) == 2


_MARKINGS_44 = ["WH", "BN", "GN", "YE", "GY", "PK", "BU", "RD", "BK", "VT", "GYPK", "RDBU", "WHGN", "BNGN", "WHYE", "YEBN", "WHGY", "GYBN", "WHPK", "PKBN", "WHBU", "BNBU", "WHRD", "BNRD", "WHBK", "BNBK", "GYGN", "YEGY", "PKGN", "YEPK", "GNBU", "YEBU", "GNRD", "YERD", "GNBK", "YEBK", "GYBU", "PKBU", "GYRD", "PKRD", "GYBK", "PKBK", "BUBK", "RDBK"]


def test_44_colour_table_gives_the_44_markings() -> None:
    """A 44-core Cable built from CORE_COLOURS pins the 44 markings of SPEC R15, written out."""
    assert len(_MARKINGS_44) == 44
    cable = Cable(cores=tuple(Core(colour=c) for c in CORE_COLOURS), screen=Screen.FOIL)
    assert [p.marking for p in cable.pins] == [*_MARKINGS_44, "SH"]
