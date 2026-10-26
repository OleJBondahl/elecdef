"""The order of markings, digit runs compared as numbers, and the line side a marking states."""

import re

_RUNS = re.compile(r"\d+|\D+")


def marking_key(marking: str) -> tuple[tuple[int, int, str], ...]:
    """A sort key for `marking`: a digit run sorts by value, before any text run."""
    return tuple(
        (0, int(run), "") if run.isdigit() else (1, 0, run) for run in _RUNS.findall(marking)
    )


_MAIN_MARKING = re.compile(r"(\d+)/")
_AUX_MARKING = re.compile(r"\d{2,}")


def line_marking(markings: tuple[str, ...]) -> str | None:
    """The line-side marking by numbering: a main's odd number, an auxiliary's lowest last digit.

    Anything else, or a tie, is None.
    """
    mains = [_MAIN_MARKING.match(m) for m in markings]
    if all(mains):
        odd = [m for m, hit in zip(markings, mains, strict=True) if hit and int(hit[1]) % 2]
        return odd[0] if len(odd) == 1 else None
    if all(_AUX_MARKING.fullmatch(m) for m in markings):
        low = min(int(m[-1]) for m in markings)
        first = [m for m in markings if int(m[-1]) == low]
        return first[0] if len(first) == 1 else None
    return None
