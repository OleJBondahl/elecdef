"""Connection, mounting and environment vocabularies."""

from elecdef.vocab._base import Vocab


class Technology(Vocab):
    """How a conductor or part is joined."""

    SCREW = "screw clamp"
    SPRING_CAGE = ""
    PUSH_IN = ""
    TENSION = ""
    IDC = ""
    CRIMP = ""
    SOLDER = "soldered joint"
    PRESS_IN = ""
    PLUG_IN = ""
    BOLT = ""
    WIRE_WRAP = ""
    THT = "through-hole mount"
    SMD = "surface mount"


class ScrewSize(Vocab):
    """Terminal screw thread size."""

    M2_5 = ""
    M3 = ""
    M3_5 = ""
    M4 = ""
    M5 = ""


class ConductorMaterial(Vocab):
    """The metal a conductor is made of."""

    CU = ""
    TINNED_CU = ""
    AL = ""
    AL_CU = ""


class Mounting(Vocab):
    """How a part is fixed in place."""

    DIN_RAIL = "clips onto a rail"
    PANEL = "fixed to a panel"
    PCB = "soldered to a board"
    PLUG_IN = ""


class IpCode(Vocab):
    """Ingress protection class, by name."""

    IP00 = ""
    IP20 = ""
    IP30 = ""
    IP40 = ""
    IP44 = ""
    IP54 = ""
    IP55 = ""
    IP65 = ""
    IP66 = ""
    IP67 = ""
    IP68 = ""
    IP69K = ""


class OvervoltageCategory(Vocab):
    """Overvoltage category of the installation point."""

    CAT_I = ""
    CAT_II = ""
    CAT_III = ""
    CAT_IV = ""


class PollutionDegree(Vocab):
    """Pollution degree of the environment."""

    P1 = ""
    P2 = ""
    P3 = ""
    P4 = ""
