"""`check`: the content issues of a block or a Product, reported as values and never raised."""

from elecdef._block import Block
from elecdef._checkwalk import join, walk
from elecdef._issue import Issue, IssueCode
from elecdef._product import Product
from elecdef._range import Range
from elecdef.pins import _is_marking

__all__ = ["check"]

_ORDER = (("min", "nom"), ("min", "typ"), ("min", "max"), ("nom", "max"), ("typ", "max"))


def _range_issues(path: str, item: Range) -> list[Issue]:
    """END_ORDER for a Range whose ends are not in order."""
    wrong = [
        f"{low} is above {high}"
        for low, high in _ORDER
        if getattr(item, low) is not None
        and getattr(item, high) is not None
        and getattr(item, low) > getattr(item, high)
    ]
    return [Issue(IssueCode.END_ORDER, "; ".join(wrong), path)] if wrong else []


def _pin_issues(path: str, block: Block) -> list[Issue]:
    """BAD_MARKING, DUPLICATE_MARKING and DANGLING_LINK from the pins and links of a block."""
    pins, links = tuple(getattr(block, "pins", ())), tuple(getattr(block, "links", ()))
    found: list[Issue] = []
    seen: set[tuple[str, object]] = set()
    for index, pin in enumerate(pins):
        subject = f"{join(path, 'pins')}[{index}]"
        if not _is_marking(pin.marking):
            message = f"pin marking {pin.marking!r} is not a run of marking characters"
            found.append(Issue(IssueCode.BAD_MARKING, message, subject))
        if (pin.marking, pin.side) in seen:
            side = f" on side {pin.side.name}" if pin.side else ""
            message = f"pin marking {pin.marking!r} is repeated{side}"
            found.append(Issue(IssueCode.DUPLICATE_MARKING, message, subject))
        seen.add((pin.marking, pin.side))
    names = {pin.marking for pin in pins}
    for index, link in enumerate(links):
        found.extend(
            Issue(
                IssueCode.DANGLING_LINK,
                f"link names {marking!r}, which is no pin",
                f"{join(path, 'links')}[{index}]",
            )
            for marking in link.markings
            if marking not in names
        )
    return found


def _block_issues(path: str, block: Block, *, product: bool) -> list[Issue]:
    """UNKNOWN_CLASS, the pin issues, and MISSING_FIGURE when the block is inside a Product."""
    found: list[Issue] = []
    module = type(block).__module__
    if module != "elecdef" and not module.startswith("elecdef."):
        message = f"{type(block).__qualname__} is not defined in the elecdef catalogue"
        found.append(Issue(IssueCode.UNKNOWN_CLASS, message, path or "block"))
    if hasattr(block, "pins"):
        found += _pin_issues(path, block)
    if product:
        found.extend(
            Issue(IssueCode.MISSING_FIGURE, f"{name} is needed and unfilled", join(path, name))
            for name in type(block).needs
            if getattr(block, name) in (None, ())
        )
    return found


def _unique(found: list[Issue]) -> tuple[Issue, ...]:
    """The issues in order, a pin issue repeated by an enclosing block kept once, outermost."""
    pin_codes = (IssueCode.BAD_MARKING, IssueCode.DUPLICATE_MARKING, IssueCode.DANGLING_LINK)
    seen: set[tuple[IssueCode, str]] = set()
    kept: list[Issue] = []
    for issue in found:
        key = (issue.code, issue.message)
        if issue.code in pin_codes and key in seen:
            continue
        seen.add(key)
        kept.append(issue)
    return tuple(kept)


def check(block: Block | Product) -> tuple[Issue, ...]:
    """Report the content issues of a block, or of the block inside a Product, as a tuple.

    A figure a block kind needs is reported only inside a Product; a bare block is a template.
    """
    if isinstance(block, Product):
        root, product = block.block, True
    elif isinstance(block, Block):
        root, product = block, False
    else:
        message = f"check takes a Block or a Product, not {type(block).__name__}"
        raise TypeError(message)
    found: list[Issue] = []
    for path, item in walk(root):
        if isinstance(item, Range):
            found += _range_issues(path, item)
        else:
            found += _block_issues(path, item, product=product)
    return _unique(found)
