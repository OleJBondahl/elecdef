"""The private helpers that number contacts and join their pins for the composite blocks."""

from dataclasses import replace

from elecdef._coil import Coil
from elecdef._contact import Contact
from elecdef.pins import Link, Marking, Pin


def _numbered(
    contacts: tuple[Contact, ...], scheme: Marking, first: int = 1
) -> tuple[Contact, ...]:
    """The contacts set to `scheme` from number `first`; a contact with `own_pins` is kept."""
    return tuple(
        contact if contact.own_pins else replace(contact, number=number, scheme=scheme)
        for number, contact in enumerate(contacts, first)
    )


def _joined(
    coil: Coil | None, contacts: tuple[Contact, ...]
) -> tuple[tuple[Pin, ...], tuple[Link, ...]]:
    """The coil pins, if any, then the pins and links of each contact in order."""
    pins = coil.pins if coil else ()
    links: tuple[Link, ...] = ()
    for contact in contacts:
        pins += contact.pins
        links += contact.links
    return pins, links
