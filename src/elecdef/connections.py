"""The thirteen leaf connections, each stating its technology only."""

from elecdef._connection import Connection
from elecdef.vocab import Technology

__all__ = [
    "BOLT",
    "CRIMP",
    "IDC",
    "PLUG_IN",
    "PRESS_IN",
    "PUSH_IN",
    "SCREW",
    "SMD",
    "SOLDER",
    "SPRING_CAGE",
    "TENSION",
    "THT",
    "WIRE_WRAP",
]

SCREW = Connection(technology=Technology.SCREW)
SPRING_CAGE = Connection(technology=Technology.SPRING_CAGE)
PUSH_IN = Connection(technology=Technology.PUSH_IN)
TENSION = Connection(technology=Technology.TENSION)
IDC = Connection(technology=Technology.IDC)
CRIMP = Connection(technology=Technology.CRIMP)
SOLDER = Connection(technology=Technology.SOLDER)
PRESS_IN = Connection(technology=Technology.PRESS_IN)
PLUG_IN = Connection(technology=Technology.PLUG_IN)
BOLT = Connection(technology=Technology.BOLT)
WIRE_WRAP = Connection(technology=Technology.WIRE_WRAP)
THT = Connection(technology=Technology.THT)
SMD = Connection(technology=Technology.SMD)
