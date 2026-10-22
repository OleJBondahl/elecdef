"""A Link with one marking is malformed."""

from elecdef.pins import Link, LinkKind


def build():
    return Link(("11",), LinkKind.SWITCHED)
