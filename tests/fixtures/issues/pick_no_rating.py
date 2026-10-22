"""A pick with no covering row reports NO_RATING."""

from elecdef import Range, Role, Unit, pick
from elecdef.vocab import Current

U = Unit

VIA = "pick"


def issues():
    row = Range(Role.RATED, nom=U.A(6))
    return (pick((row,), U.V(24), Current.DC).issue,)
