"""R8 member list: the PinRole members are pinned, SCREEN last (designer ruling 2026-10-22)."""

from elecdef.pins import PinRole


def test_pin_roles_are_pinned_with_screen_last() -> None:
    """A new role or a reorder fails here."""
    assert [r.name for r in PinRole] == [
        "COMMON", "MAKE", "BREAK", "LINE", "LOAD", "COIL", "PLUS", "MINUS",
        "SIGNAL", "SUPPLY", "PE", "SCREEN",
    ]  # fmt: skip
