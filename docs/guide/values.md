# Values

This page shows units, quantities and kinds. A quantity is an exact figure with its unit, and it never changes unit on its own.

## Units and quantities

A unit is a member of `Unit`. Calling it with a figure builds a `Quantity`. The figure may be an int or a str.

```python
from elecdef import Quantity, Unit as U

supply = U.V(24)
wire = U.MM2("2.5")
assert isinstance(supply, Quantity)
assert supply.value == 24
assert supply.unit is U.V
assert str(wire.value) == "2.5"
assert wire.unit.symbol == "mm2"
```

## A float is refused

A float can hide an inexact decimal, so `Unit` refuses it with a `TypeError`.

```python
from elecdef import Unit as U

try:
    U.V(float("20.4"))
except TypeError:
    refused = True
assert refused
```

## Equality as written and `same`

`==` compares the figure and the unit as written. `same` compares both figures in base units, so a kilovolt equals a thousand volts only under `same`.

```python
from elecdef import Unit as U

kilovolt = U.KV(1)
assert (kilovolt == U.V(1000)) is False
assert kilovolt.same(U.V(1000)) is True
```

## Conversion with `to`

`to` gives the same figure in another unit of the same kind. The result is exact.

```python
from elecdef import Unit as U

assert U.KV(1).to(U.V) == U.V(1000)
assert U.KV(1).to(U.V).value == 1000
```

## Ordering

Quantities of one kind order by their base units.

```python
from elecdef import Unit as U

assert U.V(1) < U.KV(1)
assert U.KV(1) >= U.V(1000)
```

## Kind

Every unit has a `Kind`. Conversion and ordering stay inside one kind, and a conversion across kinds raises a `TypeError`.

```python
from elecdef import Unit as U
from elecdef.vocab import Kind

assert U.V.kind is Kind.VOLTAGE
assert U.MM2.kind is Kind.AREA
try:
    U.KV(1).to(U.A)
except TypeError:
    across_kinds = True
assert across_kinds
```
