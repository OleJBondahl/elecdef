# Vocabulary

This page shows the closed vocabularies in `elecdef.vocab`. Each member is a name with a one-line gloss, and a condition takes members in an `At`.

## Kind

`Kind` names the physical kind a unit belongs to. Members include `VOLTAGE`, `CURRENT`, `FREQUENCY` and `AREA`.

```python
from elecdef.vocab import Kind

assert Kind.VOLTAGE.name == "VOLTAGE"
assert Kind.FREQUENCY.name == "FREQUENCY"
assert Kind.AREA.name == "AREA"
```

## Current

`Current` says which current kind a figure is stated for. Each member has a gloss.

```python
from elecdef.vocab import Current

assert Current.AC.gloss == "alternating current"
assert Current.DC.gloss == "direct current"
```

## Utilisation

`Utilisation` holds the utilisation codes a contact rating is stated for, such as `AC_15` and `DC_13`.

```python
from elecdef.vocab import Utilisation

assert Utilisation.AC_15.name == "AC_15"
assert Utilisation.DC_13.name == "DC_13"
```

## CoilState

`CoilState` says in which state a coil figure holds. It takes a frequency in an `At`.

```python
from elecdef import At, Unit as U
from elecdef.vocab import CoilState

hold = At(CoilState.HOLD, U.HZ(60))
assert hold.get(CoilState) is CoilState.HOLD
assert hold.covers(CoilState.HOLD)
```

## ConductorKind

`ConductorKind` says how a terminal conductor is built. `FINE` means many fine wires.

```python
from elecdef import At
from elecdef.vocab import ConductorKind

fine = At(ConductorKind.FINE)
assert fine.get(ConductorKind) is ConductorKind.FINE
```
