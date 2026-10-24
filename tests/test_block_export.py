"""Block is a public name: the base of every block, importable from elecdef."""

import elecdef
from elecdef import Block, Contact
from elecdef.vocab import ContactForm


def test_block_is_in_the_public_surface():
    assert "Block" in elecdef.__all__
    assert elecdef.Block is Block


def test_contact_is_a_block():
    assert issubclass(Contact, Block)
    assert isinstance(Contact(ContactForm.MAKE), Block)


def test_block_builds():
    assert isinstance(Block(), Block)
