"""A link that names a marking no pin carries reports DANGLING_LINK."""

from elecdef import Device, check
from elecdef.pins import Link, LinkKind, Pin, PinRole

VIA = "check"


def issues():
    pins = (Pin("1", PinRole.SIGNAL),)
    return check(Device(pins=pins, links=(Link(("1", "2"), LinkKind.CONDUCTIVE),)))
