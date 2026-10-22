"""The E tests of `check`: its codes, its fixtures, the Product rule and the carried checks."""

from dataclasses import dataclass
from pathlib import Path

import family
import pytest

from elecdef import (
    Breaker,
    Coil,
    Contact,
    Contactor,
    Device,
    Fuse,
    Issue,
    IssueCode,
    Overload,
    PlcCard,
    PowerSupply,
    Product,
    Range,
    Relay,
    Role,
    TerminalBlock,
    check,
)
from elecdef import Unit as U  # noqa: N817 - the short alias the tests use
from elecdef.cable import Cable, Core
from elecdef.computer import Computer
from elecdef.conductor import Conductor
from elecdef.connector import Connector
from elecdef.fuse import FuseHolder
from elecdef.pins import Pin, PinRole
from elecdef.plc import Channel, ChannelGroup
from elecdef.supply import SupplyInput
from elecdef.terminal import Level
from elecdef.vocab import CoilKind, ContactForm, LevelKind, Potential

FIXTURES = Path(__file__).parent / "fixtures" / "issues"
EIGHT = {
    "END_ORDER",
    "DUPLICATE_MARKING",
    "BAD_MARKING",
    "DANGLING_LINK",
    "MISSING_FIGURE",
    "UNKNOWN_CLASS",
    "NO_RATING",
    "AMBIGUOUS_RATING",
}
PICK_CODES = {IssueCode.NO_RATING, IssueCode.AMBIGUOUS_RATING}
STEMS = {
    "end_order": IssueCode.END_ORDER,
    "duplicate_marking": IssueCode.DUPLICATE_MARKING,
    "bad_marking": IssueCode.BAD_MARKING,
    "dangling_link": IssueCode.DANGLING_LINK,
    "missing_figure": IssueCode.MISSING_FIGURE,
    "unknown_class": IssueCode.UNKNOWN_CLASS,
    "pick_no_rating": IssueCode.NO_RATING,
    "pick_ambiguous": IssueCode.AMBIGUOUS_RATING,
}
COIL = Coil(CoilKind.DC, voltage=(Range(Role.RATED, nom=U.V(24)),))
CONTACT = Contact(ContactForm.MAKE)


@dataclass(frozen=True)
class MyCoil(Coil):
    """A coil subclass defined outside the catalogue."""


def _fixtures() -> list[tuple[Path, list[Issue], str]]:
    found = []
    for path in sorted(FIXTURES.glob("*.py")):
        module = family._load_fixture(path)
        found.append((path, list(module.issues()), module.VIA))
    return found


def _supply_ac() -> SupplyInput:
    pins = (Pin("L", PinRole.LINE), Pin("N", PinRole.LINE), Pin("PE", PinRole.PE))
    return SupplyInput(pins=pins)


def _example_blocks() -> list:
    level = Level("1", Potential.L, LevelKind.FEED_THROUGH)
    group = ChannelGroup(template=Channel(), markings=("1", "2"), common=("M",))
    return [
        COIL,
        CONTACT,
        Relay(coil=COIL, contacts=(CONTACT, CONTACT)),
        Contactor(coil=COIL, main=(CONTACT,), aux=(Contact(ContactForm.BREAK),)),
        Fuse(),
        FuseHolder(poles=2),
        Breaker(),
        TerminalBlock(levels=(level,)),
        Cable(cores=(Core(number=1), Core(number=2))),
        PowerSupply(input=_supply_ac()),
        Connector(poles=3),
        Computer(supply=SupplyInput()),
        Device(pins=(Pin("1", PinRole.SIGNAL),)),
        PlcCard(supply=SupplyInput(), groups=(group,)),
    ]


def _codes(issues: tuple[Issue, ...]) -> set[IssueCode]:
    return {issue.code for issue in issues}


def test_issue_code_is_exactly_the_eight() -> None:
    """IssueCode has exactly the eight codes."""
    assert {code.name for code in IssueCode} == EIGHT


def test_every_code_has_a_fixture_named_for_it() -> None:
    """The fixtures cover all eight codes and each reports only the code its name gives."""
    seen: set[IssueCode] = set()
    for path, issues, _via in _fixtures():
        assert issues, path.name
        assert _codes(tuple(issues)) == {STEMS[path.stem]}, path.name
        seen |= _codes(tuple(issues))
    assert {code.name for code in seen} == EIGHT


def test_check_fixtures_report_no_pick_code() -> None:
    """A fixture made by `check` reports none of the pick codes."""
    for path, issues, via in _fixtures():
        if via == "check":
            assert not _codes(tuple(issues)) & PICK_CODES, path.name


@pytest.mark.parametrize("block", _example_blocks(), ids=lambda b: type(b).__name__)
def test_check_of_examples_emits_only_the_six(block) -> None:
    """`check` of an example block, bare and in a Product, never reports a pick code."""
    assert not _codes(check(block)) & PICK_CODES
    assert not _codes(check(Product("P-1", "Maker", block))) & PICK_CODES


NEEDY = [
    (Coil(), "voltage"),
    (Contact(), "switching"),
    (Fuse(), "current"),
    (Breaker(), "current"),
    (Relay(), "contacts"),
    (Overload(), "setting"),
    (PowerSupply(), "output_voltage"),
    (TerminalBlock(), "levels"),
    (Conductor(), "area"),
    (Cable(), "cores"),
    (PlcCard(), "groups"),
]


@pytest.mark.parametrize(("block", "name"), NEEDY, ids=lambda v: type(v).__name__)
def test_missing_figure_only_inside_a_product(block, name) -> None:
    """An unfilled need is clean in a bare block and MISSING_FIGURE in a Product."""
    assert IssueCode.MISSING_FIGURE not in _codes(check(block))
    issues = [
        i for i in check(Product("P-1", "Maker", block)) if i.code is IssueCode.MISSING_FIGURE
    ]
    assert name in {i.subject for i in issues}


def test_missing_figure_inside_a_relay_names_the_path() -> None:
    """An unfilled Contact inside a Relay in a Product is `contacts[0].switching`."""
    relay = Relay(coil=COIL, contacts=(Contact(ContactForm.MAKE),))
    subjects = {i.subject for i in check(Product("R-1", "Maker", relay))}
    assert "contacts[0].switching" in subjects


def test_a_clean_coil_and_its_product_report_nothing() -> None:
    """A Coil with its voltage filled, bare or in a Product, gives `()`."""
    assert check(COIL) == ()
    assert check(Product("C-1", "Maker", COIL)) == ()


@pytest.mark.parametrize("value", [3, None, Pin("1", PinRole.SIGNAL)])
def test_check_of_a_non_block_is_a_type_error(value) -> None:
    """`check` takes a Block or a Product and nothing else."""
    with pytest.raises(TypeError):
        check(value)


def _coil_with(**ends) -> Coil:
    return Coil(voltage=(Range(Role.RATED, **ends),))


@pytest.mark.parametrize(
    "ends",
    [
        {"min": U.V(5), "max": U.V(2)},
        {"min": U.V(5), "nom": U.V(2)},
        {"nom": U.V(5), "max": U.V(2)},
    ],
)
def test_end_order_reports_ends_out_of_order(ends) -> None:
    """A min above max, a min above nom and a nom above max are each END_ORDER."""
    issues = check(_coil_with(**ends))
    assert [i.code for i in issues] == [IssueCode.END_ORDER]


def test_end_order_clean_for_ends_in_order() -> None:
    """Ends in order report nothing."""
    assert check(_coil_with(min=U.V(2), nom=U.V(5), max=U.V(9))) == ()


def test_end_order_subject_is_the_path_of_a_nested_range() -> None:
    """A bad Range inside a sub-block has the path `coil.voltage[0]`."""
    relay = Relay(coil=_coil_with(min=U.V(5), max=U.V(2)), contacts=(CONTACT,))
    assert [i.subject for i in check(relay)] == ["coil.voltage[0]"]


def test_unknown_class_for_a_coil_subclass_outside_the_catalogue() -> None:
    """A Coil subclass defined here is UNKNOWN_CLASS at the root, subject `block`."""
    issues = check(MyCoil())
    assert [(i.code, i.subject) for i in issues] == [(IssueCode.UNKNOWN_CLASS, "block")]


def test_unknown_class_never_fires_for_catalogue_blocks() -> None:
    """No catalogue example is reported UNKNOWN_CLASS."""
    for block in _example_blocks():
        assert IssueCode.UNKNOWN_CLASS not in _codes(check(block))


def test_a_power_supply_with_default_input_repeats_a_marking() -> None:
    """Default input pins `+ -` against default outputs `+ -` give DUPLICATE_MARKING."""
    issues = check(PowerSupply(input=SupplyInput()))
    assert IssueCode.DUPLICATE_MARKING in _codes(issues)


def test_a_power_supply_with_ac_input_has_no_duplicate() -> None:
    """An AC input with pins `L N PE` shares no marking with the outputs."""
    issues = check(PowerSupply(input=_supply_ac()))
    assert IssueCode.DUPLICATE_MARKING not in _codes(issues)


def test_a_cable_core_with_no_number_or_colour_is_a_bad_marking() -> None:
    """A Core with no number and no colour gives an empty marking, BAD_MARKING at `pins[0]`."""
    issues = check(Cable(cores=(Core(),)))
    assert [(i.code, i.subject) for i in issues] == [(IssueCode.BAD_MARKING, "pins[0]")]


def test_a_cable_with_numbered_cores_has_no_bad_marking() -> None:
    """Numbered cores give valid markings."""
    issues = check(Cable(cores=(Core(number=1), Core(number=2))))
    assert IssueCode.BAD_MARKING not in _codes(issues)


def test_channel_group_overwrites_a_template_number_and_pins_pending_a_ruling() -> None:
    """SHOWS that `ChannelGroup.channels` replaces a template Channel's own number and pins.

    `check` does not report it. Awaiting a designer ruling: report it, refuse it, or document it.
    """
    template = Channel(number=99, pins=(Pin("X", PinRole.SIGNAL),))
    group = ChannelGroup(template=template, markings=("A", "B"))
    channels = group.channels()
    assert tuple(c.number for c in channels) == (1, 2)
    assert tuple(tuple(p.marking for p in c.pins) for c in channels) == (("A",), ("B",))
    assert check(group) == ()
