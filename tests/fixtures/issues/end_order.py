"""A Range whose minimum is above its maximum reports END_ORDER."""

from elecdef import Coil, Range, Role, check
from elecdef import Unit as U  # noqa: N817 - the short alias the tests use

VIA = "check"


def issues():
    return check(Coil(voltage=(Range(Role.RATED, min=U.V(5), max=U.V(2)),)))
