"""A link whose rest state is neither a bool nor None raises TypeError."""

from typing import Any

from elecdef.pins import Link, LinkKind


def build():
    state: Any = "closed"
    return Link(("1", "2"), LinkKind.SWITCHED, state)
