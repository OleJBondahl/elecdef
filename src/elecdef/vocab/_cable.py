"""Cable and wire vocabularies."""

from elecdef.vocab._base import Vocab


class Colour(Vocab):
    """A conductor colour code."""

    BK = ""
    BN = ""
    RD = ""
    OG = ""
    YE = ""
    GN = ""
    BU = ""
    VT = ""
    GY = ""
    WH = ""
    PK = ""
    TQ = ""
    GD = ""
    SR = ""
    GNYE = ""


class ConductorClass(Vocab):
    """The conductor stranding class."""

    CLASS_1 = ""
    CLASS_2 = ""
    CLASS_5 = ""
    CLASS_6 = ""


class Insulation(Vocab):
    """The conductor insulation material."""

    PVC = ""
    PE = ""
    XLPE = ""
    EPR = ""
    PUR = ""
    TPE = ""
    SILICONE = ""
    PTFE = ""
    FEP = ""


class Screen(Vocab):
    """The screen construction."""

    NONE = "no screen"
    FOIL = "foil screen"
    BRAID = "braided screen"
    FOIL_BRAID = ""


class Armour(Vocab):
    """The armour construction."""

    NONE = ""
    WIRE = ""
    TAPE = ""
    BRAID = ""


class SheathMaterial(Vocab):
    """The outer sheath material."""

    PVC = ""
    PUR = ""
    PE = ""
    LSZH = ""
    TPE = ""
    SILICONE = ""


class CoreRole(Vocab):
    """The role of a core in a cable."""

    CORE = ""
    DRAIN = "drain wire"


class Scheme(Vocab):
    """The wire colour scheme family."""

    HARMONISED = ""
    VDE = ""
    NORDIC = ""
    MARINE = ""
    OTHER = ""
