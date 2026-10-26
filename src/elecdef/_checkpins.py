"""The pin issues of `check`: marking syntax once per authored pin, uniqueness over the device."""

from dataclasses import fields

from elecdef._block import Block
from elecdef._checkwalk import join, walk
from elecdef._issue import Issue, IssueCode
from elecdef.pins import LinkKind, Pin, _is_marking


def _pin_field(block: Block) -> str | None:
    """The attribute that holds the pins the author gave, or a leaf's computed `pins`."""
    names = {item.name for item in fields(block)}
    if "own_pins" in names:
        return "own_pins"
    if "pins" in names:
        return "pins"
    leaf = all(item is block for _, item in walk(block) if isinstance(item, Block))
    return "pins" if leaf and hasattr(block, "pins") else None


def authored(path: str, block: Block) -> list[tuple[str, Pin]]:
    """Each pin the block authors, with its subject path; a composite's computed pins are not."""
    name = _pin_field(block)
    if name is None:
        return []
    return [(f"{join(path, name)}[{index}]", pin) for index, pin in enumerate(getattr(block, name))]


def marking_issues(path: str, block: Block) -> list[Issue]:
    """BAD_MARKING for each authored pin whose marking is not a run of marking characters."""
    return [
        Issue(
            IssueCode.BAD_MARKING,
            f"pin marking {pin.marking!r} is not a run of marking characters",
            subject,
        )
        for subject, pin in authored(path, block)
        if not _is_marking(pin.marking)
    ]


def link_issues(path: str, block: Block) -> list[Issue]:
    """DANGLING_LINK for each link marking that names no pin of the block."""
    names = {pin.marking for pin in getattr(block, "pins", ())}
    return [
        Issue(
            IssueCode.DANGLING_LINK,
            f"link names {marking!r}, which is no pin",
            f"{join(path, 'links')}[{index}]",
        )
        for index, link in enumerate(getattr(block, "links", ()))
        for marking in link.markings
        if marking not in names
    ]


def rest_state_issues(path: str, block: Block) -> list[Issue]:
    """STRAY_REST_STATE for each link that is not SWITCHED yet states `closed_at_rest`."""
    return [
        Issue(
            IssueCode.STRAY_REST_STATE,
            f"a {link.kind.name} link states a rest state; only a SWITCHED link has one",
            f"{join(path, 'links')}[{index}]",
        )
        for index, link in enumerate(getattr(block, "links", ()))
        if link.kind is not LinkKind.SWITCHED and link.closed_at_rest is not None
    ]


def _subjects(root: Block, pins: tuple[Pin, ...]) -> list[str]:
    """The subject of each pin in the root's full pin set: its authored path, else `pins[i]`."""
    pool = [
        pair
        for path, item in walk(root)
        if isinstance(item, Block)
        for pair in authored(path, item)
    ]
    subjects: list[str] = []
    for index, pin in enumerate(pins):
        match = next((at for at, (_, given) in enumerate(pool) if given == pin), None)
        subjects.append(pool.pop(match)[0] if match is not None else f"pins[{index}]")
    return subjects


def duplicate_issues(root: Block) -> list[Issue]:
    """DUPLICATE_MARKING for each repeat after the first over the outermost block's full pins."""
    pins = tuple(getattr(root, "pins", ()))
    found: list[Issue] = []
    seen: set[tuple[str, object]] = set()
    for pin, subject in zip(pins, _subjects(root, pins), strict=True):
        if (pin.marking, pin.side) in seen:
            side = f" on side {pin.side.name}" if pin.side else ""
            message = f"pin marking {pin.marking!r} is repeated{side}"
            found.append(Issue(IssueCode.DUPLICATE_MARKING, message, subject))
        seen.add((pin.marking, pin.side))
    return found
