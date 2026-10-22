# Pins

This page shows `elecdef.pins` and `elecdef.supply`: pins, links, the marking schemes and the supply input. A contact's markings follow its form, its index and a scheme.

## Pins and links

```python
from elecdef.pins import Link, LinkKind, Marking, Pin, PinRole, Side

pin = Pin("A1", PinRole.PLUS, Side.A)
assert pin.alternates == ()
link = Link(("11", "12"), LinkKind.SWITCHED, closed_at_rest=True)
assert link.markings == ("11", "12")
assert Marking.AUX is not Marking.MAIN
```

A link names exactly two markings; one or three raise `TypeError`.

## Markings of a contact

```python
from elecdef.pins import Marking, contact_pins
from elecdef.vocab import ContactForm

pins, links = contact_pins(ContactForm.CHANGEOVER, 1, Marking.AUX)
assert [p.marking for p in pins] == ["11", "12", "14"]
assert [(l.markings, l.closed_at_rest) for l in links] == [(("11", "12"), True), (("11", "14"), False)]
main_pins, _ = contact_pins(ContactForm.MAKE, 2, Marking.MAIN)
assert [p.marking for p in main_pins] == ["3/L2", "4/T2"]
```

## Supply input

```python
from elecdef.supply import SupplyInput

supply = SupplyInput()
assert [p.marking for p in supply.pins] == ["+", "-"]
```
