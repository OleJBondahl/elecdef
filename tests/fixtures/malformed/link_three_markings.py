"""A Link with three markings is malformed."""

from elecdef.pins import Link, LinkKind


def build():
    return Link(("11", "12", "14"), LinkKind.SWITCHED)
