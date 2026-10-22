# Lookup

This page shows how `pick` finds the one rating that covers a question. It returns a `Pick`, which holds either the `found` range or an `Issue`.

## pick

`pick` takes a tuple of `Range` and the conditions to ask for. Each condition is a `Quantity`, a `Range` or an enum member. The contact table below has three rows.

```python
from elecdef import At, Range, Role, Unit as U, pick
from elecdef.vocab import Current, Utilisation

rows = (
    Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_15)),
    Range(Role.RATED, nom=U.A(10), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_1)),
    Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(24)), Current.DC, Utilisation.DC_13)),
)
assert pick(rows, U.V(24), Current.DC, Utilisation.DC_13).found is rows[2]
```

## Pick

A `Pick` holds exactly one of `found` and `issue`. A found answer has no issue, and a refused answer has no range.

```python
from elecdef import At, Pick, Range, Role, Unit as U, pick
from elecdef.vocab import Current, Utilisation

rows = (
    Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_15)),
    Range(Role.RATED, nom=U.A(10), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_1)),
    Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(24)), Current.DC, Utilisation.DC_13)),
)
answer = pick(rows, U.V(24), Current.DC, Utilisation.DC_13)
assert isinstance(answer, Pick)
assert answer.issue is None
```

## Issue and IssueCode

When no row covers the ask, `pick` returns an `Issue` with the code `NO_RATING`. When two rows cover it, the code is `AMBIGUOUS_RATING`.

```python
from elecdef import At, Issue, IssueCode, Range, Role, Unit as U, pick
from elecdef.vocab import Current, Utilisation

rows = (
    Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_15)),
    Range(Role.RATED, nom=U.A(10), at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_1)),
    Range(Role.RATED, nom=U.A(6), at=At(Range(Role.LIMITING, max=U.V(24)), Current.DC, Utilisation.DC_13)),
)
no_rating = pick(rows, U.V(400), Current.AC, Utilisation.AC_15)
assert no_rating.found is None
assert isinstance(no_rating.issue, Issue)
assert no_rating.issue.code is IssueCode.NO_RATING
assert pick(rows, Current.AC).issue.code is IssueCode.AMBIGUOUS_RATING
```
