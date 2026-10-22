"""E12 gate (terminal, connector, computer, device): the pins each block gives (proposed rows)."""

import dataclasses

import pytest

from elecdef import Device, TerminalBlock
from elecdef.computer import Computer, Port
from elecdef.connector import Connector
from elecdef.pins import Link, LinkKind, Pin, PinRole, Side
from elecdef.supply import SupplyInput
from elecdef.terminal import Level
from elecdef.vocab import ConnectorFamily, LevelKind, PortKind, Potential


def _level(marking: str, kind: LevelKind, potential: Potential = Potential.L) -> Level:
    return Level(marking, potential, kind)


def test_device_stores_pins_and_links_as_given() -> None:
    """Pins and links are held and returned as given (the typed fallback)."""
    pins = (Pin("1", PinRole.LINE), Pin("2", PinRole.LOAD))
    links = (Link(("1", "2"), LinkKind.CONDUCTIVE),)
    device = Device(pins=pins, links=links)
    assert device.pins == pins
    assert device.links == links


def test_device_defaults_are_empty() -> None:
    """A bare Device has no pins, no links and nothing else filled."""
    device = Device()
    assert (device.pins, device.links) == ((), ())
    assert device.rating is device.connection is device.body is device.symbol is None


@pytest.mark.parametrize("field", ["pins", "links"])
def test_device_wrong_types_raise(field: str) -> None:
    """A non-tuple, or a tuple of the wrong item, is a TypeError."""
    with pytest.raises(TypeError):
        Device(**{field: ["x"]})  # ty: ignore[invalid-argument-type] - refused on purpose
    with pytest.raises(TypeError):
        Device(**{field: ("x",)})  # ty: ignore[invalid-argument-type] - refused on purpose


def test_feed_through_level_gives_one_pin() -> None:
    """Proposed row: a FEED_THROUGH level on two sides gives one pin and no link."""
    block = TerminalBlock(levels=(_level("1", LevelKind.FEED_THROUGH),))
    assert block.pins == (Pin("1", PinRole.SUPPLY),)
    assert block.links == ()


def test_fuse_level_gives_a_primed_pin_and_a_link() -> None:
    """Proposed row (D7): a FUSE level gives `1` on side A, `1'` on side B and a protective link."""
    block = TerminalBlock(levels=(_level("1", LevelKind.FUSE),))
    assert block.pins == (
        Pin("1", PinRole.SUPPLY, Side.A),
        Pin("1'", PinRole.SUPPLY, Side.B),
    )
    assert block.links == (Link(("1", "1'"), LinkKind.PROTECTIVE),)


def test_disconnect_level_gives_a_switched_link() -> None:
    """Proposed row (D7): a DISCONNECT level gives two pins and a link closed at rest."""
    block = TerminalBlock(levels=(_level("2", LevelKind.DISCONNECT),))
    assert [pin.marking for pin in block.pins] == ["2", "2'"]
    assert block.links == (Link(("2", "2'"), LinkKind.SWITCHED, closed_at_rest=True),)


def test_pe_level_has_the_pe_role() -> None:
    """Proposed row: a PE level carries the PE role; a signal potential the SIGNAL role."""
    block = TerminalBlock(
        levels=(
            _level("PE", LevelKind.PE, Potential.PE),
            _level("3", LevelKind.SENSOR_ACTUATOR, Potential.SIGNAL),
        )
    )
    assert [pin.role for pin in block.pins] == [PinRole.PE, PinRole.SIGNAL]


def test_levels_are_needed_and_pins_follow_replace() -> None:
    """`needs` names levels; pins are computed on every read, so replace never leaves them stale."""
    assert TerminalBlock.needs == ("levels",)
    block = TerminalBlock(levels=(_level("1", LevelKind.FEED_THROUGH),))
    changed = dataclasses.replace(block, levels=(_level("7", LevelKind.FEED_THROUGH),))
    assert changed.pins[0].marking == "7"
    assert TerminalBlock().pins == ()


def test_level_marking_must_be_a_str() -> None:
    """A Level marking that is not a str is a TypeError."""
    with pytest.raises(TypeError):
        Level(1, Potential.L, LevelKind.FEED_THROUGH)  # ty: ignore[invalid-argument-type] - refused on purpose


def test_connector_pins_run_one_to_poles() -> None:
    """Proposed row: poles=4 gives pins 1 to 4, in order."""
    connector = Connector(family=ConnectorFamily.M12, poles=4)
    assert [pin.marking for pin in connector.pins] == ["1", "2", "3", "4"]
    assert connector.links == ()
    assert Connector().pins == ()


@pytest.mark.parametrize("poles", [0, -1, True, "4"])
def test_connector_bad_poles_raise(poles: object) -> None:
    """Zero, a negative, a bool and a str are not poles."""
    with pytest.raises(TypeError):
        Connector(poles=poles)  # ty: ignore[invalid-argument-type] - refused on purpose


def test_connector_shielded_must_be_a_bool() -> None:
    """A shielded flag that is not a bool is a TypeError."""
    with pytest.raises(TypeError):
        Connector(shielded=1)  # ty: ignore[invalid-argument-type] - refused on purpose


def test_computer_pins_are_supply_then_ports() -> None:
    """Proposed row: supply pins first, then ETHERNET1, ETHERNET2 for count 2."""
    computer = Computer(supply=SupplyInput(), ports=(Port(PortKind.ETHERNET, 2),))
    assert [pin.marking for pin in computer.pins] == ["+", "-", "ETHERNET1", "ETHERNET2"]
    assert computer.links == ()
    assert Computer().pins == ()


def test_port_instances_are_numbered_per_kind() -> None:
    """Two Port entries of one kind never repeat a marking; another kind restarts at 1."""
    computer = Computer(
        ports=(Port(PortKind.USB), Port(PortKind.ETHERNET), Port(PortKind.USB, 2)),
    )
    assert [pin.marking for pin in computer.pins] == ["USB1", "ETHERNET1", "USB2", "USB3"]


@pytest.mark.parametrize("count", [0, -1, True, 1.5])
def test_port_bad_count_raises(count: object) -> None:
    """A count that is not a positive int is a TypeError."""
    with pytest.raises(TypeError):
        Port(PortKind.USB, count)  # ty: ignore[invalid-argument-type] - refused on purpose
