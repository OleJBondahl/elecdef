"""Standard-agnostic electrical engineering vocabulary as strict, typed, immutable values."""

from elecdef._body import Body
from elecdef._coil import Coil
from elecdef._connection import Connection
from elecdef._contact import Contact
from elecdef._issue import Issue, IssueCode
from elecdef._product import Symbol
from elecdef._quantity import Quantity, Unit
from elecdef._range import At, Pick, Range, Ranges, Role, pick
from elecdef._rating import Rating
from elecdef._relay import ContactBlock, Contactor, Relay

__all__ = [
    "At",
    "Body",
    "Coil",
    "Connection",
    "Contact",
    "ContactBlock",
    "Contactor",
    "Issue",
    "IssueCode",
    "Pick",
    "Quantity",
    "Range",
    "Ranges",
    "Rating",
    "Relay",
    "Role",
    "Symbol",
    "Unit",
    "pick",
]
