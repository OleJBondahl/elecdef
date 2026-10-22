"""Issues as values: what `check` and `pick` report instead of raising."""

from dataclasses import dataclass
from enum import Enum, auto


class IssueCode(Enum):
    """The closed set of issue codes; `check` reports the first six, `pick` the last two."""

    END_ORDER = auto()
    DUPLICATE_MARKING = auto()
    BAD_MARKING = auto()
    DANGLING_LINK = auto()
    MISSING_FIGURE = auto()
    UNKNOWN_CLASS = auto()
    NO_RATING = auto()
    AMBIGUOUS_RATING = auto()


@dataclass(frozen=True)
class Issue:
    """One finding: a code, a message and the subject path it concerns, such as `coil.voltage`."""

    code: IssueCode
    message: str
    subject: str
