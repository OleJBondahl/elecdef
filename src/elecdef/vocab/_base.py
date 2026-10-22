"""The base of every closed vocabulary."""

from enum import Enum
from typing import Self


class Vocab(Enum):
    """An enum whose members carry a one-line gloss; never persist `.value`, use the name."""

    gloss: str

    def __new__(cls, gloss: str = "") -> Self:
        """Number the member in order and keep its gloss (empty when none is written)."""
        member = object.__new__(cls)
        member._value_ = len(cls._member_map_) + 1
        member.gloss = gloss
        return member
