"""A pick with two covering rows reports AMBIGUOUS_RATING."""

from elecdef import At, Range, Role, Unit, pick
from elecdef.vocab import Current, Utilisation

U = Unit

VIA = "pick"


def issues():
    first = Range(Role.RATED, nom=U.A(6), at=At(Current.AC, Utilisation.AC_15))
    second = Range(Role.RATED, nom=U.A(10), at=At(Current.AC, Utilisation.AC_1))
    return (pick((first, second), Current.AC).issue,)
