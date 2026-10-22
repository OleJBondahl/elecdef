# Cables

This page shows `elecdef.conductor` and `elecdef.cable`: a conductor, and a cable whose pins follow its cores and its screen. Cable pins are a proposed row, not proven against a source.

## A conductor

```python
from elecdef import Unit
from elecdef.conductor import Conductor
from elecdef.vocab import Colour, ConductorMaterial

wire = Conductor(material=ConductorMaterial.CU, area=Unit.MM2("1.5"), colour=(Colour.BN,))
assert wire.area == Unit.MM2("1.5")
assert Conductor.needs == ("area",)
```

## A cable from the 44-colour table

Each core takes its colours from `CORE_COLOURS`; a core with no number is marked by its colour letters, and a screen adds the pin `SH`.

```python
from elecdef.cable import Cable, Core, TypeCode
from elecdef.pins import PinRole
from elecdef.tables import CORE_COLOURS
from elecdef.vocab import Scheme, Screen

cable = Cable(
    cores=tuple(Core(colour=colours) for colours in CORE_COLOURS),
    screen=Screen.FOIL,
    type_code=TypeCode(Scheme.OTHER, "44-core control cable"),
)
markings = [pin.marking for pin in cable.pins]
assert markings[:3] == ["WH", "BN", "GN"]
assert markings[10] == "GYPK"
assert markings[-2:] == ["RDBK", "SH"]
assert cable.pins[-1].role is PinRole.SCREEN
assert cable.links == ()
```

With numbers the markings are the numbers: `Core(number=1)` gives the pin `1`.
