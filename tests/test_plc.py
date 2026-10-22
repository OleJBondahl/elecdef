"""E4 and E10 gates for the PLC blocks, and the DI card golden of the spec (WO-ED-9)."""

import dataclasses

import pytest

from elecdef import At, Contact, PlcCard, Range, Role, pick
from elecdef import Unit as U  # noqa: N817 - the brief names the alias U
from elecdef.connections import PUSH_IN
from elecdef.pins import PinRole
from elecdef.plc import AnalogIo, Channel, ChannelGroup, DigitalInput, DigitalOutput
from elecdef.supply import SupplyInput
from elecdef.vocab import ContactForm, DiType, Polarity, Signal

DI = DigitalInput(input_type=DiType.T1, polarity=Polarity.SINKING)
CHANNEL = Channel(Signal.DI, electrical=DI)
GROUP = ChannelGroup(
    CHANNEL,
    markings=tuple(str(n) for n in range(1, 9)),
    common=("1M",),
    isolated=True,
    connection=PUSH_IN,
)
GROUP2 = dataclasses.replace(GROUP, markings=tuple(str(n) for n in range(9, 17)), common=("2M",))
ROW_24V = Range(Role.RATED, nom=U.MA(70), at=At(U.V(24)))
SUPPLY = SupplyInput(current=(ROW_24V, Range(Role.RATED, nom=U.MA(130), at=At(U.V(12)))))


def test_signal_blocks_default_unfilled() -> None:
    """Every field of the three signal blocks is unfilled and none has pins or a connection."""
    for block in (DigitalInput(), DigitalOutput(), AnalogIo()):
        names = {item.name for item in dataclasses.fields(block)}
        assert not names & {"pins", "connection"}
        assert all(not getattr(block, name) for name in names)


def test_digital_input_refuses_a_wrong_kind() -> None:
    """A voltage where a current is stated is a TypeError (E4)."""
    with pytest.raises(TypeError):
        DigitalInput(current=U.V(5))  # ty: ignore[invalid-argument-type] - refused on purpose


def test_analog_span_takes_voltage_and_current_not_time() -> None:
    """The span is a Range of VOLTAGE or CURRENT; TIME is refused."""
    assert AnalogIo(span=Range(Role.RATED, max=U.V(10))).span is not None
    assert AnalogIo(span=Range(Role.RATED, max=U.MA(20))).span is not None
    with pytest.raises(TypeError):
        AnalogIo(span=Range(Role.RATED, max=U.S(1)))


def test_channel_refuses_a_foreign_electrical_and_bad_pins() -> None:
    """A Channel takes one of the four electrical types, and a tuple of Pin."""
    with pytest.raises(TypeError):
        Channel(electrical=1)  # ty: ignore[invalid-argument-type] - refused on purpose
    with pytest.raises(TypeError):
        Channel(pins=("1",))  # ty: ignore[invalid-argument-type] - refused on purpose
    assert Channel(electrical=Contact(ContactForm.MAKE)).electrical is not None


def test_group_rejects_a_foreign_template_and_markings() -> None:
    """The template is a Channel; markings and common are tuples of str."""
    with pytest.raises(TypeError):
        ChannelGroup(template=1)  # ty: ignore[invalid-argument-type] - refused on purpose
    with pytest.raises(TypeError):
        ChannelGroup(markings=(1,))  # ty: ignore[invalid-argument-type] - refused on purpose
    with pytest.raises(TypeError):
        ChannelGroup(common="1M")  # ty: ignore[invalid-argument-type] - refused on purpose


def test_channels_number_from_first_and_share_electrical() -> None:
    """`channels(1)` over 8 markings gives numbers 1..8 sharing one `electrical`."""
    channels = GROUP.channels(1)
    assert [channel.number for channel in channels] == list(range(1, 9))
    assert all(channel.electrical is DI for channel in channels)
    assert [channel.pins[0].marking for channel in channels] == [str(n) for n in range(1, 9)]
    assert all(channel.pins[0].role is PinRole.SIGNAL for channel in channels)
    assert GROUP.channels(9)[0].number == 9


def test_group_without_template_has_no_channels() -> None:
    """A group with no template gives no channels."""
    assert ChannelGroup(markings=("1",)).channels() == ()


def _card() -> PlcCard:
    return PlcCard(supply=SUPPLY, groups=(GROUP, GROUP2))


def test_di_card_golden() -> None:
    """The spec DI card: 16 channels on one `electrical`, pins `+ - 1..8 1M 9..16 2M`."""
    card = _card()
    assert [channel.number for channel in card.channels] == list(range(1, 17))
    assert len({id(channel.electrical) for channel in card.channels}) == 1
    expected = ["+", "-", *map(str, range(1, 9)), "1M", *map(str, range(9, 17)), "2M"]
    assert [pin.marking for pin in card.pins] == expected
    assert card.pins[10].role is PinRole.COMMON
    assert card.links == ()


def test_pick_returns_the_70_ma_row() -> None:
    """Pick over the supply current at 24 V returns the 70 mA row."""
    supply = _card().supply
    assert supply is not None
    assert pick(supply.current, U.V(24)).found is ROW_24V


def test_card_stores_no_pins_and_replace_leaves_none_stale() -> None:
    """PlcCard has no `pins` field (E10), and a replaced card reads fresh pins."""
    assert "pins" not in {item.name for item in dataclasses.fields(PlcCard)}
    card = dataclasses.replace(_card(), groups=_card().groups[:1])
    assert len(card.channels) == 8
    assert [pin.marking for pin in card.pins][-1] == "1M"


def test_card_refuses_foreign_groups() -> None:
    """Groups are a tuple of ChannelGroup."""
    with pytest.raises(TypeError):
        PlcCard(groups=(1,))  # ty: ignore[invalid-argument-type] - refused on purpose
