"""Two pins of one marking and no side report DUPLICATE_MARKING."""

from elecdef import Device, check
from elecdef.pins import Pin, PinRole

VIA = "check"


def issues():
    return check(Device(pins=(Pin("1", PinRole.SIGNAL), Pin("1", PinRole.SIGNAL))))
