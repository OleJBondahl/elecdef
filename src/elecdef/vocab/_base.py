"""The base of every closed vocabulary."""

from enum import Enum
from typing import Self


class Vocab(Enum):
    """An enum whose members carry a one-line gloss; never persist `.value`, use the name."""

    gloss: str

    def __new__(cls, gloss: str = "", *_row: object) -> Self:
        """Number the member in order and keep its gloss; more fields need an `__init__`."""
        if _row and cls.__init__ is Vocab.__init__:
            message = f"{cls.__name__} rows hold a gloss only, not {len(_row)} more fields"
            raise TypeError(message)
        member = object.__new__(cls)
        member._value_ = len(cls._member_map_) + 1
        member.gloss = gloss
        return member
