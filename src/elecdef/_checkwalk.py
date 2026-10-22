"""The generic walk `check` makes: every Block and Range under a value, with its path."""

from collections.abc import Iterator
from dataclasses import fields, is_dataclass

from elecdef._block import Block
from elecdef._range import Range


def join(path: str, name: str) -> str:
    """The path of `name` under `path`."""
    return f"{path}.{name}" if path else name


def walk(value: object, path: str = "") -> Iterator[tuple[str, Block | Range]]:
    """Each Block and Range under `value`, parents first, through dataclass fields and tuples."""
    if isinstance(value, Range):
        yield path, value
    elif isinstance(value, tuple):
        for index, each in enumerate(value):
            yield from walk(each, f"{path}[{index}]")
    elif is_dataclass(value) and not isinstance(value, type):
        if isinstance(value, Block):
            yield path, value
        for item in fields(value):
            yield from walk(getattr(value, item.name), join(path, item.name))
