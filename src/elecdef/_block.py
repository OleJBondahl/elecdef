"""The one base class of the blocks: it checks the kind of each figure and wraps a bare Range."""

from dataclasses import dataclass, field, fields
from typing import Any, ClassVar

from elecdef._quantity import Kind, Quantity
from elecdef._range import Range

__all__ = ["Block", "figure"]


def figure(*kinds: Kind, many: bool = False) -> Any:  # noqa: ANN401 - dataclasses types field() as Any
    """A block field that holds a figure of one of `kinds`; `many` holds a tuple of Range."""
    return field(default=() if many else None, metadata={"kinds": kinds, "many": many})


def _kind_of(value: object) -> Kind:
    """The kind of a Quantity or a Range; any other value is a TypeError."""
    if isinstance(value, Quantity):
        return value.unit.kind
    if isinstance(value, Range):
        return value.kind
    message = f"a figure is a Quantity or a Range, not {type(value).__name__}"
    raise TypeError(message)


def _check_figure(name: str, value: object, kinds: tuple[Kind, ...]) -> None:
    """Refuse a filled figure whose kind is not one of `kinds`."""
    if value is not None and _kind_of(value) not in kinds:
        message = f"{name} takes {[kind.name for kind in kinds]}, not {_kind_of(value).name}"
        raise TypeError(message)


@dataclass(frozen=True)
class Block:
    """The base of every block: it refuses a figure of the wrong kind at construction.

    A caller types a block field, or checks isinstance, against this one class for every block.
    """

    needs: ClassVar[tuple[str, ...]] = ()

    def __post_init__(self) -> None:
        """Check each filled figure and wrap a bare Range given to a `many` field."""
        for item in fields(self):
            if "kinds" not in item.metadata:
                continue
            value = getattr(self, item.name)
            if not item.metadata["many"]:
                _check_figure(item.name, value, item.metadata["kinds"])
                continue
            if isinstance(value, Range):
                value = (value,)
                object.__setattr__(self, item.name, value)
            if not isinstance(value, tuple):
                message = f"{item.name} is a tuple of Range"
                raise TypeError(message)
            for each in value:
                _check_figure(item.name, each, item.metadata["kinds"])
