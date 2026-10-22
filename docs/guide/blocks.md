# Blocks

This page shows the leaf blocks `Connection`, `Body`, `Rating` and `Symbol`. A block holds figures checked for their kind, and a bare `Range` given to a list field becomes a one-item tuple.

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
