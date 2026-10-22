# Blocks

This page shows the leaf blocks `Connection`, `Body`, `Rating` and `Symbol`, and the switching blocks `Coil`, `Contact`, `Relay`, `Contactor` and `ContactBlock`. A block holds figures checked for their kind, and a bare `Range` given to a list field becomes a one-item tuple.

## Connection

`Connection` says how a conductor attaches. Fill only what a datasheet states; the other fields stay unfilled.

```python
from dataclasses import replace

from elecdef import Connection, Range, Role, Unit as U
from elecdef.connections import SCREW
from elecdef.vocab import Technology

torque = Range(Role.RATED, min=U.N_M("0.5"), max=U.N_M("0.6"))
screw_m3 = replace(SCREW, torque=torque, strip_length=U.MM(7))
assert screw_m3.technology is Technology.SCREW
assert SCREW.torque is None
```

## Body

`Body` holds the outer shape: three lengths, a protection code, temperature ranges and the mounting.

```python
from elecdef import Body, Range, Role, Unit as U
from elecdef.vocab import IpCode, Mounting

body = Body(width=U.MM(17), ip=IpCode.IP20, mounting=Mounting.DIN_RAIL,
            temperature=Range(Role.RATED, min=U.DEG_C(-25), max=U.DEG_C(55)))
assert len(body.temperature) == 1
```

## Rating

`Rating` holds the voltage, current and frequency a thing is rated for.

```python
from elecdef import Range, Rating, Role, Unit as U
from elecdef.vocab import OvervoltageCategory

rating = Rating(voltage=Range(Role.RATED, max=U.V(400)), overvoltage_category=OvervoltageCategory.CAT_III)
assert rating.voltage[0].max == U.V(400)
```

## Symbol

`Symbol` names a drawn symbol by key and version and holds nothing else of it.

```python
from elecdef import Symbol

symbol = Symbol("relay-2co", 1)
assert symbol.version == 1
```

## Coil, Contact and Relay

`Coil` and `Contact` store only the pins their author gives. Their pins and links are read on every access, and a `Relay` numbers its contacts 1 to n each time, so `replace` never leaves a stale marking. `Contactor` numbers `main` contacts as MAIN, then `aux` as AUX; `ContactBlock` numbers AUX from `numbered_from`.

```python
from dataclasses import replace

from elecdef import Coil, Contact, ContactBlock, Contactor, Relay, Range, Role, Unit as U
from elecdef.pins import PinRole
from elecdef.vocab import CoilKind, ContactFeature, ContactForm, RelayKind, Suppression

coil = Coil(CoilKind.DC, suppression=Suppression.DIODE, voltage=Range(Role.RATED, nom=U.V(24)))
co = Contact(ContactForm.CHANGEOVER)
relay = Relay(contacts=(co, co), coil=coil)
assert [pin.marking for pin in relay.pins] == ["A1", "A2", "11", "12", "14", "21", "22", "24"]
assert relay.pins[0].role is PinRole.PLUS
assert [pin.marking for pin in replace(relay, kind=RelayKind.TIMER).pins][2] == "15"

mirror = Contact(ContactForm.BREAK, features=frozenset({ContactFeature.MIRROR}))
contactor = Contactor(coil, (Contact(ContactForm.MAKE),) * 3, (mirror,))
assert [pin.marking for pin in contactor.pins][-2:] == ["11", "12"]

block = ContactBlock((Contact(ContactForm.MAKE), Contact(ContactForm.BREAK)), numbered_from=5)
assert [pin.marking for pin in block.pins] == ["53", "54", "61", "62"]
```

## TerminalBlock and Level

`TerminalBlock` holds the levels of a terminal; each `Level` gives a pin, and a fuse or disconnect level gives a second pin `marking'` and a link.

```python
from elecdef import TerminalBlock
from elecdef.terminal import Level
from elecdef.vocab import LevelKind, Potential

block = TerminalBlock(levels=(Level("1", Potential.L, LevelKind.FUSE),))
assert [pin.marking for pin in block.pins] == ["1", "1'"]
assert len(block.links) == 1
```

## Connector

`Connector` states a connector family and its poles; its pins run from 1 to the poles.

```python
from elecdef.connector import Connector
from elecdef.vocab import ConnectorFamily

connector = Connector(family=ConnectorFamily.M12, poles=4)
assert [pin.marking for pin in connector.pins] == ["1", "2", "3", "4"]
```

## Computer and Port

`Computer` gives its supply pins, then one pin per `Port` instance.

```python
from elecdef.computer import Computer, Port
from elecdef.supply import SupplyInput
from elecdef.vocab import PortKind

computer = Computer(supply=SupplyInput(), ports=(Port(PortKind.ETHERNET, 2),))
assert [pin.marking for pin in computer.pins][-2:] == ["ETHERNET1", "ETHERNET2"]
```

## Device

`Device` holds pins and links given outright, for a thing with no block yet.

```python
from elecdef import Device
from elecdef.pins import Pin, PinRole

device = Device(pins=(Pin("1", PinRole.SIGNAL),))
assert device.pins[0].marking == "1"
```
