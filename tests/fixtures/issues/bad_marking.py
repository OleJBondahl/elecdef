"""A pin whose marking holds a space reports BAD_MARKING."""

from elecdef import Device, check
from elecdef.pins import Pin, PinRole

VIA = "check"


def issues():
    return check(Device(pins=(Pin("a b", PinRole.SIGNAL),)))
