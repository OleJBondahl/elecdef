"""The Symbol reference a drawn block holds."""

from dataclasses import dataclass

__all__ = ["Symbol"]


@dataclass(frozen=True)
class Symbol:
    """A reference to a drawn symbol by key and version.

    Nothing else of the symbol is held here.
    """

    key: str
    version: int

    def __post_init__(self) -> None:
        """Refuse a key that is not a str and a version that is not an int."""
        if not isinstance(self.key, str):
            message = f"key is a str, not {type(self.key).__name__}"
            raise TypeError(message)
        if not isinstance(self.version, int) or isinstance(self.version, bool):
            message = f"version is an int, not {type(self.version).__name__}"
            raise TypeError(message)
