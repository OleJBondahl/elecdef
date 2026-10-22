"""The Symbol reference a drawn block holds, and the Product envelope around a block."""

from dataclasses import dataclass

from elecdef._block import Block

__all__ = ["Product", "Symbol"]


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


@dataclass(frozen=True)
class Product:
    """A maker's product: part number, manufacturer, optional name and the block it is.

    `check` reports the figures the block's kind needs only for a block inside a Product.
    """

    mpn: str
    manufacturer: str
    block: Block
    name: str | None = None

    def __post_init__(self) -> None:
        """Refuse a text that is not a str and a block that is not a Block."""
        for field_name in ("mpn", "manufacturer"):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                message = f"{field_name} is a str, not {type(value).__name__}"
                raise TypeError(message)
        if self.name is not None and not isinstance(self.name, str):
            message = f"name is a str, not {type(self.name).__name__}"
            raise TypeError(message)
        if not isinstance(self.block, Block):
            message = f"block is a Block, not {type(self.block).__name__}"
            raise TypeError(message)
