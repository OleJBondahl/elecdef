"""A bool is not a figure."""

from elecdef import Unit

U = Unit


def build():
    flag = True
    return U.V(flag)
