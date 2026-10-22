"""R13: Product is the identity envelope around one block."""

import dataclasses

import pytest

from elecdef import Coil, Fuse, Product


def test_a_product_holds_its_identity_and_its_block() -> None:
    fuse = Fuse()
    product = Product("MPN-1", "Maker", fuse, name="A fuse")
    assert (product.mpn, product.manufacturer, product.block, product.name) == (
        "MPN-1",
        "Maker",
        fuse,
        "A fuse",
    )


def test_the_name_may_be_left_out() -> None:
    assert Product("MPN-1", "Maker", Coil()).name is None


def test_a_product_is_frozen() -> None:
    product = Product("MPN-1", "Maker", Coil())
    with pytest.raises(dataclasses.FrozenInstanceError):
        product.mpn = "other"  # ty: ignore[invalid-assignment] - the write is the test


@pytest.mark.parametrize(
    "args",
    [
        (1, "Maker", Coil()),
        ("MPN-1", None, Coil()),
        ("MPN-1", "Maker", "coil"),
        ("MPN-1", "Maker", None),
        ("MPN-1", "Maker", Product("MPN-2", "Maker", Coil())),
    ],
)
def test_a_wrong_type_is_a_type_error(args: tuple[object, ...]) -> None:
    with pytest.raises(TypeError):
        Product(*args)  # ty: ignore[invalid-argument-type] - the wrong type is the test


def test_a_name_that_is_not_a_str_is_a_type_error() -> None:
    with pytest.raises(TypeError):
        Product("MPN-1", "Maker", Coil(), name=3)  # ty: ignore[invalid-argument-type] - the test
