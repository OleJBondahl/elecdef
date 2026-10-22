# Ranges

This page shows how a datasheet figure becomes a `Range`. A range has a role, up to four ends and the conditions it holds under.

## Role

`Role` says what a stated figure means. `RATED` is the maker's rating, `LIMITING` is an extreme withstood, and `REFERENCE` is a reference band.

```python
from elecdef import Role

assert {role.name for role in Role} == {"RATED", "LIMITING", "REFERENCE"}
```

## Range

A `Range` holds a role, up to four ends (`min`, `nom`, `typ` and `max`) and an `At`. The ends are quantities of one kind.

```python
from fractions import Fraction

from elecdef import At, Range, Role, Unit as U
from elecdef.vocab import Current

rated = Range(Role.RATED, nom=U.V(24), min=U.V("20.4"), max=U.V(30), at=At(Current.DC))
assert rated.tolerance == (Fraction(-3, 20), Fraction(1, 4))
```

`tolerance` gives the lower and upper deviation from `nom` as exact fractions.

## contains and covers

`contains` tests one quantity. `covers` tests whether another range lies inside this one.

```python
from elecdef import At, Range, Role, Unit as U
from elecdef.vocab import Current

rated = Range(Role.RATED, nom=U.V(24), min=U.V("20.4"), max=U.V(30), at=At(Current.DC))
narrow = Range(Role.RATED, min=U.V(21), max=U.V(28), at=At(Current.DC))
assert rated.contains(U.V(22))
assert not rated.contains(U.V(31))
assert rated.covers(narrow)
assert not narrow.covers(rated)
```

## At

`At` lists the conditions a figure holds under, one per kind. It sorts them, so the order of the arguments does not matter.

```python
from elecdef import At, Unit as U
from elecdef.vocab import Current

assert At(Current.AC, U.HZ(50)) == At(U.HZ(50), Current.AC)
```

## Ranges

`Ranges` is a tuple of `Range`. Write it as a plain annotation.

```python
from fractions import Fraction

from elecdef import At, Range, Ranges, Role, Unit as U
from elecdef.vocab import Current

range1 = Range(Role.RATED, nom=U.V(24), min=U.V("20.4"), max=U.V(30), at=At(Current.DC))
range2 = Range(Role.RATED, min=U.V(21), max=U.V(28), at=At(Current.DC))
rows: Ranges = (range1, range2)
assert len(rows) == 2
assert rows[1].covers(rows[1])
```
