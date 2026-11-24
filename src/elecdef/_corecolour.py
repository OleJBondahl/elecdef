"""The colour text of a core, read into colours."""

from dataclasses import dataclass

from elecdef.vocab import Colour

_SCREEN = "SH"
_BASE = {c.name: c for c in Colour if c is not Colour.GNYE}


@dataclass(frozen=True)
class CoreColour:
    """What a core colour text states: its colours, its core number, or that it is a screen."""

    colours: tuple[Colour, ...] = ()
    number: int | None = None
    screen: bool = False

    @property
    def name(self) -> str:
        """The printed colour name: the names of the colours joined by `-`, or `screen`."""
        return "screen" if self.screen else "-".join(c.gloss for c in self.colours)


def _with_rest(first: Colour, rest: str) -> CoreColour | None:
    """A base colour followed by `rest`: a core number, a second base colour, or nothing."""
    if not rest:
        return CoreColour((first,))
    if rest.isascii() and rest.isdigit() and rest[0] != "0":
        return CoreColour((first,), number=int(rest))
    second = _BASE.get(rest)
    return CoreColour((first, second)) if second is not None and second is not first else None


def core_colour(text: str) -> CoreColour | None:
    """The colours of a core colour code (`BU`, `BKWH`, `GNYE`, `BK1`, the screen `SH`), else None.

    A core number has no sign and no leading zero; two joined base codes differ.
    """
    if text == _SCREEN:
        return CoreColour(screen=True)
    if text == Colour.GNYE.name:
        return CoreColour((Colour.GNYE,))
    first = _BASE.get(text[:2])
    return None if first is None else _with_rest(first, text[2:])
