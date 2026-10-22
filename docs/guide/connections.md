# Connections

This page shows `elecdef.connections`: one technology-only leaf per attachment technology. Copy a leaf with `replace` to add a datasheet's figures; the shipped leaf never changes.

## The leaves

```python
from elecdef.connections import (
    BOLT, CRIMP, IDC, PLUG_IN, PRESS_IN, PUSH_IN, SCREW, SMD, SOLDER,
    SPRING_CAGE, TENSION, THT, WIRE_WRAP,
)
from elecdef.vocab import Technology

leaves = (SCREW, SPRING_CAGE, PUSH_IN, TENSION, IDC, CRIMP, SOLDER, PRESS_IN, PLUG_IN, BOLT,
          WIRE_WRAP, THT, SMD)
assert [leaf.technology for leaf in leaves] == list(Technology)
assert all(leaf.torque is None and not leaf.conductor for leaf in leaves)
```
