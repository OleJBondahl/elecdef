"""A switched link that states a rest state its break pin denies reports CONFLICTING_REST_STATE."""

from elecdef import Device, check
from elecdef.pins import Link, LinkKind, Pin, PinRole

VIA = "check"


def issues():
    pins = (Pin("11", PinRole.COMMON), Pin("12", PinRole.BREAK))
    link = Link(("11", "12"), LinkKind.SWITCHED, closed_at_rest=False)
    return check(Device(pins=pins, links=(link,)))
