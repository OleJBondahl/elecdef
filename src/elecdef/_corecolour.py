"""The colour text of a core, read into colours."""

from dataclasses import dataclass, field

from elecdef.vocab import Colour

_SCREEN = "SH"
_GNYE = Colour.GNYE.name
_BASE = {c.name: c for c in Colour if c is not Colour.GNYE}


@dataclass(frozen=True)
class CoreColour:
    """What a core colour text states: its colours, its core number, or that it is a screen.

    `protective` is true for green-yellow alone. A screen is not a core: the caller handles it.
    """

    colours: tuple[Colour, ...] = ()
    number: int | None = None
    screen: bool = False
    protective: bool = field(init=False)

    def __post_init__(self) -> None:
        """Set `protective` from the colours: green-yellow alone."""
        object.__setattr__(self, "protective", self.colours == (Colour.GNYE,))

    @property
    def name(self) -> str:
        """The printed colour name, `screen` for a screen; the core number is its own field."""
        return "screen" if self.screen else "-".join(c.gloss for c in self.colours)


def _number(rest: str) -> int | None:
    """A core number: digits with no sign and no leading zero, else None."""
    return int(rest) if rest.isascii() and rest.isdigit() and rest[0] != "0" else None


def _with_rest(first: Colour, rest: str) -> CoreColour | None:
    """A base colour followed by `rest`: a core number, a second base colour, or nothing."""
    if not rest:
        return CoreColour((first,))
    if (number := _number(rest)) is not None:
        return CoreColour((first,), number=number)
    second = _BASE.get(rest)
    return CoreColour((first, second)) if second is not None and second is not first else None


def _green_yellow(rest: str) -> CoreColour | None:
    """Green-yellow followed by `rest`: a core number or nothing."""
    if not rest:
        return CoreColour((Colour.GNYE,))
    number = _number(rest)
    return None if number is None else CoreColour((Colour.GNYE,), number=number)


def core_colour(text: str) -> CoreColour | None:
    """The colours of a core colour code (`BU`, `BKWH`, `GNYE`, `BK1`, `GNYE1`, `SH`), else None.

    A core number has no sign and no leading zero; two joined base codes differ.
    """
    if not isinstance(text, str):
        message = f"expected a str, not {type(text).__name__}"
        raise TypeError(message)
    if text == _SCREEN:
        return CoreColour(screen=True)
    if text.startswith(_GNYE):
        return _green_yellow(text[len(_GNYE) :])
    first = _BASE.get(text[:2])
    return None if first is None else _with_rest(first, text[2:])
