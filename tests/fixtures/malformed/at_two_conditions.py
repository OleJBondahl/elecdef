"""Two conditions of one kind in an At are malformed."""

from elecdef import At
from elecdef.vocab import Current


def build():
    return At(Current.AC, Current.DC)
