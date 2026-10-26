"""The order of markings: digit runs compare as numbers, so `9` comes before `10`."""

import re

_RUNS = re.compile(r"\d+|\D+")


def marking_key(marking: str) -> tuple[tuple[int, int, str], ...]:
    """A sort key for `marking`: a digit run sorts by value, before any text run."""
    return tuple(
        (0, int(run), "") if run.isdigit() else (1, 0, run) for run in _RUNS.findall(marking)
    )
