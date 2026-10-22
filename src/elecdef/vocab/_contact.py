"""Contact vocabularies."""

from elecdef.vocab._base import Vocab


class ContactForm(Vocab):
    """The switching form of a contact."""

    MAKE = "closes when operated"
    BREAK = "opens when operated"
    CHANGEOVER = "one common, one make, one break"


class ContactFeature(Vocab):
    """A special property of a contact."""

    MIRROR = ""
    POSITIVE_OPENING = ""
    MAKE_BEFORE_BREAK = ""
    EARLY_MAKE = ""
    LATE_BREAK = ""


class ContactMaterial(Vocab):
    """The contact surface material."""

    AG = ""
    AGNI = ""
    AGSNO2 = ""
    AU = ""
