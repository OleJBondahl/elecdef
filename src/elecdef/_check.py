"""`check`: the content issues of a block or a Product, reported as values and never raised."""

from elecdef._block import Block
from elecdef._checkpins import duplicate_issues, link_issues, marking_issues
from elecdef._checkwalk import join, walk
from elecdef._issue import Issue, IssueCode
from elecdef._product import Product
from elecdef._range import Range

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


def _block_issues(path: str, block: Block, *, product: bool) -> list[Issue]:
    """UNKNOWN_CLASS, the marking and link issues, and MISSING_FIGURE inside a Product."""
    found: list[Issue] = []
    module = type(block).__module__
    if module != "elecdef" and not module.startswith("elecdef."):
        message = f"{type(block).__qualname__} is not defined in the elecdef catalogue"
        found.append(Issue(IssueCode.UNKNOWN_CLASS, message, path or "block"))
    found += marking_issues(path, block) + link_issues(path, block)
    if product:
        found.extend(
            Issue(IssueCode.MISSING_FIGURE, f"{name} is needed and unfilled", join(path, name))
            for name in type(block).needs
            if getattr(block, name) in (None, ())
        )
    return found


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
    return tuple(found + duplicate_issues(root))
