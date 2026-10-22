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

## The other vocabularies

Each enum below is a closed list of names; a figure or a block names its choice from it, never a string.

### ActuatorKind

```python
from elecdef.vocab import ActuatorKind

assert ActuatorKind.NONE.name == "NONE"
assert isinstance(ActuatorKind.NONE.gloss, str)
```

### Armour

```python
from elecdef.vocab import Armour

assert Armour.NONE.name == "NONE"
assert isinstance(Armour.NONE.gloss, str)
```

### Bus

```python
from elecdef.vocab import Bus

assert Bus.ETHERCAT.name == "ETHERCAT"
assert isinstance(Bus.ETHERCAT.gloss, str)
```

### CardForm

```python
from elecdef.vocab import CardForm

assert CardForm.COMPACT.name == "COMPACT"
assert isinstance(CardForm.COMPACT.gloss, str)
```

### CardRole

```python
from elecdef.vocab import CardRole

assert CardRole.CONTROLLER.name == "CONTROLLER"
assert isinstance(CardRole.CONTROLLER.gloss, str)
```

### CircuitClass

```python
from elecdef.vocab import CircuitClass

assert CircuitClass.SELV.name == "SELV"
assert isinstance(CircuitClass.SELV.gloss, str)
```

### Coding

```python
from elecdef.vocab import Coding

assert Coding.A.name == "A"
assert isinstance(Coding.A.gloss, str)
```

### CoilKind

```python
from elecdef.vocab import CoilKind

assert CoilKind.AC.name == "AC"
assert isinstance(CoilKind.AC.gloss, str)
```

### Colour

```python
from elecdef.vocab import Colour

assert Colour.BK.name == "BK"
assert isinstance(Colour.BK.gloss, str)
```

### ConductorClass

```python
from elecdef.vocab import ConductorClass

assert ConductorClass.CLASS_1.name == "CLASS_1"
assert isinstance(ConductorClass.CLASS_1.gloss, str)
```

### ConductorMaterial

```python
from elecdef.vocab import ConductorMaterial

assert ConductorMaterial.CU.name == "CU"
assert isinstance(ConductorMaterial.CU.gloss, str)
```

### ConnectorFamily

```python
from elecdef.vocab import ConnectorFamily

assert ConnectorFamily.M8.name == "M8"
assert isinstance(ConnectorFamily.M8.gloss, str)
```

### ContactFeature

```python
from elecdef.vocab import ContactFeature

assert ContactFeature.MIRROR.name == "MIRROR"
assert isinstance(ContactFeature.MIRROR.gloss, str)
```

### ContactForm

```python
from elecdef.vocab import ContactForm

assert ContactForm.MAKE.name == "MAKE"
assert isinstance(ContactForm.MAKE.gloss, str)
```

### ContactMaterial

```python
from elecdef.vocab import ContactMaterial

assert ContactMaterial.AG.name == "AG"
assert isinstance(ContactMaterial.AG.gloss, str)
```

### CoreRole

```python
from elecdef.vocab import CoreRole

assert CoreRole.CORE.name == "CORE"
assert isinstance(CoreRole.CORE.gloss, str)
```

### DiType

```python
from elecdef.vocab import DiType

assert DiType.T1.name == "T1"
assert isinstance(DiType.T1.gloss, str)
```

### FuseClass

```python
from elecdef.vocab import FuseClass

assert FuseClass.gG.name == "gG"
assert isinstance(FuseClass.gG.gloss, str)
```

### FuseSpeed

```python
from elecdef.vocab import FuseSpeed

assert FuseSpeed.FF.name == "FF"
assert isinstance(FuseSpeed.FF.gloss, str)
```

### FuseSystem

```python
from elecdef.vocab import FuseSystem

assert FuseSystem.NH.name == "NH"
assert isinstance(FuseSystem.NH.gloss, str)
```

### Gender

```python
from elecdef.vocab import Gender

assert Gender.MALE.name == "MALE"
assert isinstance(Gender.MALE.gloss, str)
```

### Insulation

```python
from elecdef.vocab import Insulation

assert Insulation.PVC.name == "PVC"
assert isinstance(Insulation.PVC.gloss, str)
```

### IpCode

```python
from elecdef.vocab import IpCode

assert IpCode.IP00.name == "IP00"
assert isinstance(IpCode.IP00.gloss, str)
```

### LevelKind

```python
from elecdef.vocab import LevelKind

assert LevelKind.FEED_THROUGH.name == "FEED_THROUGH"
assert isinstance(LevelKind.FEED_THROUGH.gloss, str)
```

### Locking

```python
from elecdef.vocab import Locking

assert Locking.NONE.name == "NONE"
assert isinstance(Locking.NONE.gloss, str)
```

### Mounting

```python
from elecdef.vocab import Mounting

assert Mounting.DIN_RAIL.name == "DIN_RAIL"
assert isinstance(Mounting.DIN_RAIL.gloss, str)
```

### OutputKind

```python
from elecdef.vocab import OutputKind

assert OutputKind.TRANSISTOR.name == "TRANSISTOR"
assert isinstance(OutputKind.TRANSISTOR.gloss, str)
```

### OverloadBehaviour

```python
from elecdef.vocab import OverloadBehaviour

assert OverloadBehaviour.CONSTANT.name == "CONSTANT"
assert isinstance(OverloadBehaviour.CONSTANT.gloss, str)
```

### OvervoltageCategory

```python
from elecdef.vocab import OvervoltageCategory

assert OvervoltageCategory.CAT_I.name == "CAT_I"
assert isinstance(OvervoltageCategory.CAT_I.gloss, str)
```

### Pl

```python
from elecdef.vocab import Pl

assert Pl.PL_A.name == "PL_A"
assert isinstance(Pl.PL_A.gloss, str)
```

### Polarity

```python
from elecdef.vocab import Polarity

assert Polarity.SINKING.name == "SINKING"
assert isinstance(Polarity.SINKING.gloss, str)
```

### PollutionDegree

```python
from elecdef.vocab import PollutionDegree

assert PollutionDegree.P1.name == "P1"
assert isinstance(PollutionDegree.P1.gloss, str)
```

### PortKind

```python
from elecdef.vocab import PortKind

assert PortKind.ETHERNET.name == "ETHERNET"
assert isinstance(PortKind.ETHERNET.gloss, str)
```

### Potential

```python
from elecdef.vocab import Potential

assert Potential.L.name == "L"
assert isinstance(Potential.L.gloss, str)
```

### PsuKind

```python
from elecdef.vocab import PsuKind

assert PsuKind.AC_DC.name == "AC_DC"
assert isinstance(PsuKind.AC_DC.gloss, str)
```

### Rail

```python
from elecdef.vocab import Rail

assert Rail.DIN_35.name == "DIN_35"
assert isinstance(Rail.DIN_35.gloss, str)
```

### RelayKind

```python
from elecdef.vocab import RelayKind

assert RelayKind.ELECTROMECHANICAL.name == "ELECTROMECHANICAL"
assert isinstance(RelayKind.ELECTROMECHANICAL.gloss, str)
```

### Reset

```python
from elecdef.vocab import Reset

assert Reset.MANUAL.name == "MANUAL"
assert isinstance(Reset.MANUAL.gloss, str)
```

### RtdType

```python
from elecdef.vocab import RtdType

assert RtdType.PT100.name == "PT100"
assert isinstance(RtdType.PT100.gloss, str)
```

### Scheme

```python
from elecdef.vocab import Scheme

assert Scheme.HARMONISED.name == "HARMONISED"
assert isinstance(Scheme.HARMONISED.gloss, str)
```

### Screen

```python
from elecdef.vocab import Screen

assert Screen.NONE.name == "NONE"
assert isinstance(Screen.NONE.gloss, str)
```

### ScrewSize

```python
from elecdef.vocab import ScrewSize

assert ScrewSize.M2_5.name == "M2_5"
assert isinstance(ScrewSize.M2_5.gloss, str)
```

### SheathMaterial

```python
from elecdef.vocab import SheathMaterial

assert SheathMaterial.PVC.name == "PVC"
assert isinstance(SheathMaterial.PVC.gloss, str)
```

### Signal

```python
from elecdef.vocab import Signal

assert Signal.DI.name == "DI"
assert isinstance(Signal.DI.gloss, str)
```

### Sil

```python
from elecdef.vocab import Sil

assert Sil.SIL_1.name == "SIL_1"
assert isinstance(Sil.SIL_1.gloss, str)
```

### Suppression

```python
from elecdef.vocab import Suppression

assert Suppression.NONE.name == "NONE"
assert isinstance(Suppression.NONE.gloss, str)
```

### Technology

```python
from elecdef.vocab import Technology

assert Technology.SCREW.name == "SCREW"
assert isinstance(Technology.SCREW.gloss, str)
```

### ThermocoupleType

```python
from elecdef.vocab import ThermocoupleType

assert ThermocoupleType.J.name == "J"
assert isinstance(ThermocoupleType.J.gloss, str)
```

### TimerFunction

```python
from elecdef.vocab import TimerFunction

assert TimerFunction.ON_DELAY.name == "ON_DELAY"
assert isinstance(TimerFunction.ON_DELAY.gloss, str)
```

### TripClass

```python
from elecdef.vocab import TripClass

assert TripClass.C10A.name == "C10A"
assert isinstance(TripClass.C10A.gloss, str)
```

### TripCurve

```python
from elecdef.vocab import TripCurve

assert TripCurve.A.name == "A"
assert isinstance(TripCurve.A.gloss, str)
```
