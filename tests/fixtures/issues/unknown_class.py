"""A block class defined outside the catalogue reports UNKNOWN_CLASS."""

from dataclasses import dataclass

from elecdef import Coil, check

VIA = "check"


@dataclass(frozen=True)
class MyCoil(Coil):
    """A coil subclass defined outside the catalogue."""


def issues():
    return check(MyCoil())
