"""A link that is not switched yet states a rest state reports STRAY_REST_STATE."""

from elecdef import Device, check
from elecdef.pins import Link, LinkKind, Pin, PinRole

VIA = "check"


def issues():
    pins = (Pin("1", PinRole.SIGNAL), Pin("2", PinRole.SIGNAL))
    link = Link(("1", "2"), LinkKind.CONDUCTIVE, closed_at_rest=True)
    return check(Device(pins=pins, links=(link,)))
