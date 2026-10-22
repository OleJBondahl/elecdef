"""A Range with no end is malformed."""

from elecdef import Range, Role


def build():
    return Range(Role.RATED)
