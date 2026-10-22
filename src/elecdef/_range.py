"""Datasheet figures: `Role`, `At`, `Range`, `Ranges` and the lookup `pick`."""

from dataclasses import KW_ONLY, dataclass
from decimal import Decimal
from enum import Enum, auto
from fractions import Fraction

from elecdef._issue import Issue, IssueCode
from elecdef._quantity import Kind, Quantity

__all__ = ["At", "Pick", "Range", "Ranges", "Role", "pick"]


class Role(Enum):
    """What a stated figure means: the maker's rating, an extreme withstood, or a reference band."""

    RATED = auto()
    LIMITING = auto()
    REFERENCE = auto()


def _key(condition: object) -> Kind | type[Enum]:
    """The kind a condition is stated for: a Kind for a Quantity or Range, else its enum class."""
    if isinstance(condition, Quantity):
        return condition.unit.kind
    if isinstance(condition, Range):
        return condition.kind
    if isinstance(condition, Enum):
        return type(condition)
    message = (
        f"a condition is a Quantity, a Range or an enum member, not {type(condition).__name__}"
    )
    raise TypeError(message)


def _order(key: Kind | type[Enum]) -> tuple[int, int | str]:
    """Kinds first in Kind order, then enum classes by name."""
    return (0, key.value) if isinstance(key, Kind) else (1, key.__qualname__)


@dataclass(frozen=True, init=False)
class At:
    """The conditions a figure holds under, one per kind, in a canonical order."""

    items: tuple[Quantity | Range | Enum, ...]

    def __init__(self, *conds: Quantity | Range | Enum) -> None:
        """Sort the conditions; two of one kind are a TypeError."""
        keys = [_key(cond) for cond in conds]
        if len(set(keys)) != len(keys):
            message = "two conditions of one kind in an At"
            raise TypeError(message)
        ordered = sorted(zip(keys, conds, strict=True), key=lambda pair: _order(pair[0]))
        object.__setattr__(self, "items", tuple(cond for _, cond in ordered))

    def get(self, kind: Kind | type[Enum]) -> Quantity | Range | Enum | None:
        """The condition of a Kind or of an enum class, or None."""
        return next((cond for cond in self.items if _key(cond) == kind), None)

    def covers(self, ask: Quantity | Range | Enum) -> bool:
        """True when the condition of the ask's kind holds the ask; no such condition is False."""
        cond = self.get(_key(ask))
        if isinstance(cond, Range):
            if isinstance(ask, Quantity):
                return cond.contains(ask)
            return isinstance(ask, Range) and cond.covers(ask)
        if isinstance(cond, Quantity):
            return isinstance(ask, Quantity) and cond.same(ask)
        return cond is not None and cond is ask


@dataclass(frozen=True, slots=True)
class Range:
    """A figure as a datasheet states it: a role, up to four ends, and its conditions."""

    role: Role
    _: KW_ONLY
    min: Quantity | None = None
    nom: Quantity | None = None
    typ: Quantity | None = None
    max: Quantity | None = None
    at: At = At()

    def __post_init__(self) -> None:
        """Refuse a missing end, ends of two kinds, and a wrong type."""
        if not isinstance(self.role, Role) or not isinstance(self.at, At):
            message = "a Range takes a Role and an At"
            raise TypeError(message)
        ends = self._ends()
        if not ends:
            message = "a Range needs at least one end"
            raise TypeError(message)
        if not all(isinstance(end, Quantity) for end in ends):
            message = "the ends of a Range are Quantities"
            raise TypeError(message)
        if len({end.unit.kind for end in ends}) != 1:
            message = "the ends of a Range share one kind"
            raise TypeError(message)

    def _ends(self) -> list[Quantity]:
        return [end for end in (self.min, self.nom, self.typ, self.max) if end is not None]

    @property
    def kind(self) -> Kind:
        """The kind of the ends."""
        return self._ends()[0].unit.kind

    @property
    def tolerance(self) -> tuple[Fraction, Fraction] | None:
        """The lower and upper deviation from `nom` as exact fractions, or None."""
        if self.min is None or self.nom is None or self.max is None:
            return None
        nom = Fraction(self.nom.base())
        if nom == 0:
            return None
        return (Fraction(self.min.base()) / nom - 1, Fraction(self.max.base()) / nom - 1)

    def _bounds(self) -> tuple[Decimal | None, Decimal | None]:
        """The lower and upper end in base units; a Range with only nom or typ is a point."""
        if self.min is None and self.max is None:
            point = (self.nom or self.typ or self._ends()[0]).base()
            return (point, point)
        return (
            None if self.min is None else self.min.base(),
            None if self.max is None else self.max.base(),
        )

    def contains(self, quantity: Quantity) -> bool:
        """True when the quantity lies between the ends; another kind is a TypeError."""
        if not isinstance(quantity, Quantity) or quantity.unit.kind is not self.kind:
            message = f"a {self.kind.name} Range holds a {self.kind.name} Quantity"
            raise TypeError(message)
        low, high = self._bounds()
        base = quantity.base()
        return (low is None or low <= base) and (high is None or base <= high)

    def covers(self, other: Range) -> bool:
        """True when the other Range lies inside this one; another kind is a TypeError."""
        if not isinstance(other, Range) or other.kind is not self.kind:
            message = f"a {self.kind.name} Range covers a {self.kind.name} Range"
            raise TypeError(message)
        low, high = self._bounds()
        other_low, other_high = other._bounds()
        low_ok = low is None or (other_low is not None and low <= other_low)
        high_ok = high is None or (other_high is not None and other_high <= high)
        return low_ok and high_ok


Ranges = tuple[Range, ...]


@dataclass(frozen=True)
class Pick:
    """The answer of `pick`: exactly one of the range found or the issue."""

    found: Range | None = None
    issue: Issue | None = None

    def __post_init__(self) -> None:
        """Hold exactly one of `found` and `issue`."""
        if (self.found is None) == (self.issue is None):
            message = "a Pick holds exactly one of found and issue"
            raise TypeError(message)


def pick(ranges: tuple[Range, ...], *ask: Quantity | Range | Enum) -> Pick:
    """The one range whose conditions cover every ask, else NO_RATING or AMBIGUOUS_RATING."""
    if not isinstance(ranges, tuple) or not all(isinstance(row, Range) for row in ranges):
        message = "pick takes a tuple of Range"
        raise TypeError(message)
    wanted = At(*ask).items
    hits = [row for row in ranges if all(row.at.covers(cond) for cond in wanted)]
    if len(hits) == 1:
        return Pick(found=hits[0])
    code = IssueCode.NO_RATING if not hits else IssueCode.AMBIGUOUS_RATING
    return Pick(issue=Issue(code, f"{len(hits)} rows cover the ask", "ranges"))
