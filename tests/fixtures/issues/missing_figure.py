"""A Product around a Fuse with no current reports MISSING_FIGURE."""

from elecdef import Product, check
from elecdef.fuse import Fuse

VIA = "check"


def issues():
    return check(Product("F-1", "Maker", Fuse()))
