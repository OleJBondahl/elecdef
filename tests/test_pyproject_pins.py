"""Exact-pin gate: every dependency in `pyproject.toml` is `name==X.Y.Z`."""

import re
from pathlib import Path

import family

PIN = re.compile(r"^[A-Za-z0-9._-]+(\[[^\]]+\])?==\d+(\.\d+)*$")


def entries(root: Path) -> list[str]:
    """Every dependency string of `[project]` and of each `[dependency-groups]` group."""
    data = family.pyproject(root)
    found = list(data["project"].get("dependencies", []))
    for group in data.get("dependency-groups", {}).values():
        found += [item for item in group if isinstance(item, str)]
    return found


def check_pins(root: Path = family.ROOT) -> None:
    """Fail naming each dependency that is not an exact pin."""
    bad = [entry for entry in entries(root) if not PIN.match(entry)]
    assert not bad, f"not exact pins: {bad}"


def test_pins():
    check_pins()
