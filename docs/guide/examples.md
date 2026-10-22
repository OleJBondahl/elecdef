# Worked examples

This page runs three worked examples from first to last: a relay with its datasheet figures, a contactor with an overload relay, and a digital input card. The outputs they assert are the ones proven against a reference run. The terminal block and power supply rows of the last section are proposed, not proven against a source.

## A 24 V relay with two changeover contacts

The terminal connection is built once and shared by identity between the coil and the contacts. A contact holds one rated row per condition set, and `pick` returns the one row that covers an ask.

```python
from dataclasses import replace
from fractions import Fraction

from elecdef import At, Coil, Contact, IssueCode, Product, Range, Relay, Role, Unit as U, check, connections, pick
from elecdef.pins import LinkKind, PinRole
from elecdef.vocab import ConductorKind, CoilKind, ContactForm, Current, Suppression, Utilisation

SCREW_M3 = replace(
    connections.SCREW,
    conductor=Range(Role.RATED, min=U.MM2("0.5"), max=U.MM2("2.5"), at=At(ConductorKind.SOLID)),
    torque=Range(Role.RATED, min=U.N_M("0.5"), max=U.N_M("0.6")),
    strip_length=U.MM(7),
)
COIL = Coil(
    CoilKind.DC,
    connection=SCREW_M3,
    suppression=Suppression.DIODE,
    voltage=Range(Role.RATED, nom=U.V(24), min=U.V("20.4"), max=U.V(30), at=At(Current.DC)),
    pick_up=Range(Role.LIMITING, max=U.PCT(75)),
    drop_out=Range(Role.LIMITING, min=U.PCT(10)),
)
CO = Contact(
    ContactForm.CHANGEOVER,
    connection=SCREW_M3,
    switching=(
        Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_15)),
        Range(Role.RATED, nom=U.A(10), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_1)),
        Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(24)), Current.DC, Utilisation.DC_13)),
    ),
)
RELAY = Product("DEMO-RLY-2CO-24DC", "Demo", Relay(contacts=(CO, CO), coil=COIL))
block = RELAY.block

assert [pin.marking for pin in block.pins] == ["A1", "A2", "11", "12", "14", "21", "22", "24"]
assert block.pins[0].role is PinRole.PLUS
links = {link.markings: link for link in block.links}
assert links[("11", "12")].kind is LinkKind.SWITCHED and links[("11", "12")].closed_at_rest is True
assert links[("11", "14")].kind is LinkKind.SWITCHED and links[("11", "14")].closed_at_rest is False
assert COIL.connection is CO.connection

dc = pick(CO.switching, U.V(24), Current.DC, Utilisation.DC_13)
assert dc.found is CO.switching[2]
assert pick(CO.switching, U.V(400), Current.AC, Utilisation.AC_15).issue.code is IssueCode.NO_RATING
assert pick(CO.switching, Current.AC).issue.code is IssueCode.AMBIGUOUS_RATING
assert COIL.voltage[0].tolerance == (Fraction(-3, 20), Fraction(1, 4))
assert check(RELAY) == ()
```

## A contactor with a contact block and an overload relay

Main contacts take the pins `1/L1 2/T1 3/L2 ...`, a mirror contact follows as `11 12`, and a contact block continues from a number you give. Coil figures are rows under `At`, and `pick` finds the apparent power of the held state at 60 Hz.

```python
from elecdef import At, Coil, Contact, ContactBlock, Contactor, Overload, Range, Role, Unit as U, pick
from elecdef.pins import LinkKind
from elecdef.vocab import CoilKind, CoilState, ContactFeature, ContactForm, Current, Reset, TripClass

coil = Coil(
    CoilKind.AC,
    voltage=Range(Role.RATED, nom=U.V(230), at=At(Current.AC, U.HZ(50))),
    apparent_power=(
        Range(Role.RATED, nom=U.VA(70), at=At(CoilState.INRUSH, U.HZ(50))),
        Range(Role.RATED, nom=U.VA(9), at=At(CoilState.HOLD, U.HZ(60))),
    ),
)
main = Contact(ContactForm.MAKE)
mirror = Contact(ContactForm.BREAK, features=frozenset({ContactFeature.MIRROR}))
contactor = Contactor(coil, (main, main, main), (mirror,))
assert [pin.marking for pin in contactor.pins] == [
    "A1", "A2", "1/L1", "2/T1", "3/L2", "4/T2", "5/L3", "6/T3", "11", "12",
]
assert pick(coil.apparent_power, CoilState.HOLD, U.HZ(60)).found.nom == U.VA(9)

contact_block = ContactBlock((Contact(ContactForm.MAKE), Contact(ContactForm.BREAK)), numbered_from=5)
assert [pin.marking for pin in contact_block.pins] == ["53", "54", "61", "62"]

overload = Overload(
    poles=3,
    setting=Range(Role.RATED, min=U.A(7), max=U.A(10)),
    trip_class=TripClass.C10,
    reset=Reset.BOTH,
    phase_failure=True,
    aux=(Contact(ContactForm.BREAK), Contact(ContactForm.MAKE)),
)
assert [pin.marking for pin in overload.pins] == [
    "1/L1", "2/T1", "3/L2", "4/T2", "5/L3", "6/T3", "95", "96", "97", "98",
]
assert {link.markings: link.kind for link in overload.links}[("95", "96")] is LinkKind.SWITCHED
```

## A 16-channel digital input card

One `Channel` is a template; each `ChannelGroup` stamps it onto its markings. The channels of both groups are numbered 1 to 16 and share one `electrical` value by identity.

```python
from dataclasses import replace

from elecdef import At, PlcCard, Range, Role, Unit as U, pick
from elecdef.connections import PUSH_IN
from elecdef.plc import Channel, ChannelGroup, DigitalInput
from elecdef.supply import SupplyInput
from elecdef.vocab import Current, Signal

GROUP = ChannelGroup(
    Channel(Signal.DI, electrical=DigitalInput()),
    markings=tuple(str(n) for n in range(1, 9)),
    common=("1M",),
    isolated=True,
    connection=PUSH_IN,
)
supply = SupplyInput(
    voltage=Range(Role.RATED, nom=U.V(24), at=At(Current.DC)),
    current=(
        Range(Role.RATED, nom=U.A("0.07"), at=At(U.V(24))),
        Range(Role.RATED, nom=U.A("0.11"), at=At(U.V(30))),
    ),
)
card = PlcCard(
    supply=supply,
    groups=(GROUP, replace(GROUP, markings=tuple(str(n) for n in range(9, 17)), common=("2M",))),
)
assert [channel.number for channel in card.channels] == list(range(1, 17))
assert len({id(channel.electrical) for channel in card.channels}) == 1
assert [pin.marking for pin in card.pins] == (
    ["+", "-"] + [str(n) for n in range(1, 9)] + ["1M"] + [str(n) for n in range(9, 17)] + ["2M"]
)
assert pick(card.supply.current, U.V(24)).found.nom == U.A("0.07")
```

## Proposed rows

The pins of a fuse, a breaker, a power supply, a terminal block and a cable are proposed. They are not proven against a source, and the review page lists them. The pages for [blocks](blocks.md) and [cables](cables.md) run them: `Fuse` gives `1 2` with a protective link, `Breaker(poles=2)` gives four pins, `PowerSupply` with an OK contact gives `L N PE + - 13 14`, and `Cable` with a screen ends in `SH`.

```python
from elecdef import Range, Role, TerminalBlock, Unit as U
from elecdef.connections import PUSH_IN, SCREW
from elecdef.terminal import Level
from elecdef.vocab import LevelKind, Potential

terminal = TerminalBlock(
    levels=(Level("1", Potential.L, LevelKind.FEED_THROUGH),),
    sides=(PUSH_IN, SCREW),
)
assert [pin.marking for pin in terminal.pins] == ["1"]
assert len(terminal.sides) == 2
```
