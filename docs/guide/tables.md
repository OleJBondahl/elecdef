# Tables

The `elecdef.tables` door holds the data tables, generated from our own data files. A row ships only when its value is confirmed; contested rows are listed in `HELD.txt` and wait.

## Sizes and gauges

`CROSS_SECTIONS` lists the conductor cross sections in mm2. `AWG` holds `(n, diameter, area)` rows computed from the gauge formula, and `AWG_METRIC` maps each gauge to the smallest listed cross section that holds it.

```python
from elecdef import Unit
from elecdef.tables import AWG, AWG_METRIC, CROSS_SECTIONS

assert Unit.MM2("2.5") in CROSS_SECTIONS
assert AWG[0][0] == -3
number, diameter, area = AWG[13]
assert number == 10 and area == Unit.MM2("5.2612")
assert AWG_METRIC[13] == (10, Unit.MM2("6"))
```

## Core colours

`CORE_COLOURS` gives the colours of core positions 1 to 44, base colour first.

```python
from elecdef.tables import CORE_COLOURS
from elecdef.vocab import Colour

assert len(CORE_COLOURS) == 44
assert CORE_COLOURS[0] == (Colour.WH,)
assert CORE_COLOURS[10] == (Colour.GY, Colour.PK)
```

## Breakers and cables

`BREAKER_CURVES` holds the low and high trip bound of each curve as multiples of rated current. `BREAKER_CURRENTS` and `BREAKER_ICN` list rated currents and breaking capacities. `TRIP_TIMES` gives the trip time band per class at 7.2 times the setting. `CABLE_VOLTAGES` pairs a voltage digit pair with the two rated voltages, and `OVERVOLTAGE_IMPULSE` gives the impulse voltage of each overvoltage category.

```python
from elecdef import Unit
from elecdef.tables import (
    BREAKER_CURRENTS,
    BREAKER_CURVES,
    BREAKER_ICN,
    CABLE_VOLTAGES,
    OVERVOLTAGE_IMPULSE,
    TRIP_TIMES,
)
from elecdef.vocab import OvervoltageCategory, TripCurve

assert (TripCurve.B, 3, 5) in BREAKER_CURVES
assert Unit.A(16) in BREAKER_CURRENTS
assert Unit.KA("4.5") in BREAKER_ICN
assert ("05", Unit.V(300), Unit.V(500)) in CABLE_VOLTAGES
assert (OvervoltageCategory.CAT_III, Unit.V(4000)) in OVERVOLTAGE_IMPULSE
assert len(TRIP_TIMES) == 3
```

## Preferred values

`E_SERIES` holds `(series, mantissa)` pairs, the mantissa being ten times the value, so 4.7 is 47.

```python
from elecdef.tables import E_SERIES

assert ("E12", 47) in E_SERIES
assert ("E3", 15) not in E_SERIES
```
