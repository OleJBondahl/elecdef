"""E7: pick returns one covering range or an issue, never the first of several."""

import pytest

from elecdef import At, IssueCode, Pick, Range, Role, Unit, pick
from elecdef.vocab import CoilState, Current, Utilisation

U = Unit

AC15 = Range(
    Role.RATED,
    nom=U.A(6),
    at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_15),
)
AC1 = Range(
    Role.RATED,
    nom=U.A(10),
    at=At(Range(Role.LIMITING, max=U.V(250)), Current.AC, Utilisation.AC_1),
)
DC13 = Range(
    Role.RATED,
    nom=U.A(6),
    at=At(Range(Role.LIMITING, max=U.V(24)), Current.DC, Utilisation.DC_13),
)
ROWS = (AC15, AC1, DC13)


def test_one_match_is_found_by_inclusion_and_identity():
    assert pick(ROWS, U.V(24), Current.DC, Utilisation.DC_13) == Pick(found=DC13)
    assert pick(ROWS, U.V(230), Current.AC, Utilisation.AC_15).found is AC15


def test_no_match_is_no_rating():
    result = pick(ROWS, U.V(400), Current.AC, Utilisation.AC_15)
    assert result.found is None
    assert result.issue is not None
    assert result.issue.code is IssueCode.NO_RATING


def test_two_matches_are_ambiguous_not_the_first():
    result = pick(ROWS, Current.AC)
    assert result.found is None
    assert result.issue is not None
    assert result.issue.code is IssueCode.AMBIGUOUS_RATING


def test_a_quantity_condition_is_equality_in_base_units():
    row = Range(Role.RATED, nom=U.VA(9), at=At(CoilState.HOLD, U.HZ(60)))
    other = Range(Role.RATED, nom=U.VA(12), at=At(CoilState.HOLD, U.HZ(50)))
    assert pick((row, other), CoilState.HOLD, U.KHZ("0.06")).found is row
    assert pick((row, other), CoilState.HOLD, U.HZ(55)).issue is not None


def test_a_range_ask_is_covered_by_inclusion():
    assert pick(ROWS, Range(Role.LIMITING, max=U.V(24)), Current.DC).found is DC13
    assert pick(ROWS, Range(Role.LIMITING, max=U.V(300)), Current.DC).issue is not None


def test_an_ask_naming_a_kind_the_rows_lack_matches_no_row():
    result = pick(ROWS, U.HZ(50), Current.AC, Utilisation.AC_1)
    assert result.issue is not None
    assert result.issue.code is IssueCode.NO_RATING


def test_a_row_may_state_more_kinds_than_the_ask():
    assert pick((DC13,), Current.DC).found is DC13


def test_no_rows_is_no_rating():
    result = pick((), Current.DC)
    assert result.issue is not None
    assert result.issue.code is IssueCode.NO_RATING


def test_malformed_calls_raise():
    with pytest.raises(TypeError):
        pick(ROWS, 24)  # ty: ignore[invalid-argument-type] - the refusal under test
    with pytest.raises(TypeError):
        pick(ROWS, Current.AC, Current.DC)
    with pytest.raises(TypeError):
        pick([AC1], Current.AC)  # ty: ignore[invalid-argument-type] - the refusal under test
    with pytest.raises(TypeError):
        pick((1,), Current.AC)  # ty: ignore[invalid-argument-type] - the refusal under test


def test_a_pick_holds_exactly_one():
    with pytest.raises(TypeError):
        Pick()
    with pytest.raises(TypeError):
        Pick(found=AC1, issue=pick((), Current.AC).issue)
