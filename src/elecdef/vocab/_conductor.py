"""The marking of a conductor by what it carries."""

from elecdef.vocab._base import Vocab


class ConductorMark(Vocab):
    """A conductor marking: a phase, the neutral, a DC pole, the mid point or protective earth."""

    L1 = "phase 1"
    L2 = "phase 2"
    L3 = "phase 3"
    N = "neutral"
    L_PLUS = "positive DC pole"
    L_MINUS = "negative DC pole"
    M = "mid point"
    PE = "protective earth"

    @property
    def marking(self) -> str:
        """The printed marking, such as `L+` for `L_PLUS`."""
        return _PRINTED.get(self, self.name)

    @classmethod
    def of(cls, text: str) -> ConductorMark | None:
        """The mark a printed marking names, terminal letters included (`U` is L1), else None."""
        if not isinstance(text, str):
            message = f"expected a str, not {type(text).__name__}"
            raise TypeError(message)
        return _BY_TEXT.get(text)


_PRINTED = {ConductorMark.L_PLUS: "L+", ConductorMark.L_MINUS: "L-"}
_LETTERS = {
    "U": "L1",
    "U1": "L1",
    "V": "L2",
    "V1": "L2",
    "W": "L3",
    "W1": "L3",
    "+": "L+",
    "-": "L-",
}
_BY_TEXT = {m.marking: m for m in ConductorMark} | {
    letter: next(m for m in ConductorMark if m.marking == mark) for letter, mark in _LETTERS.items()
}
