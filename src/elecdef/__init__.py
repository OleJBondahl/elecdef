"""Standard-agnostic electrical engineering vocabulary as strict, typed, immutable values."""

from elecdef._body import Body
from elecdef._connection import Connection
from elecdef._device import Device
from elecdef._issue import Issue, IssueCode
from elecdef._product import Symbol
from elecdef._quantity import Quantity, Unit
from elecdef._range import At, Pick, Range, Ranges, Role, pick
from elecdef._rating import Rating
from elecdef.terminal import TerminalBlock

__all__ = [
    "At",
    "Body",
    "Connection",
    "Device",
    "Issue",
    "IssueCode",
    "Pick",
    "Quantity",
    "Range",
    "Ranges",
    "Rating",
    "Role",
    "Symbol",
    "TerminalBlock",
    "Unit",
    "pick",
]
