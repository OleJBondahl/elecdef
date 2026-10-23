# 0001 N13 Contact.voltage Ranges

This record holds the ruling that made `Contact.voltage` a `Ranges` field. It is the first elecdef decision record.

## Ruling

`Contact.voltage` becomes `Ranges`: a `many` voltage field whose items carry a current kind (`Current.AC` or `Current.DC`) in `at`, the same shape as `Rating.voltage`. The designer ruled N13 in for this field only (F12-approved, trailer `Design-review: SPEC-ELECDEF`).

## Why

A contact has one limiting voltage for alternating current and another for direct current. A single `Range` could not say both. The two supply blocks need no change: a rated 24 V and its operating window is one `Range` with nom, min and max.

## Effect

- `contact.voltage` reads as a tuple. A bare `Range` passed in is wrapped into a one-item tuple, so a 0.1.0 call that builds a Contact from one `Range` still builds. A 0.1.0 reader that used `contact.voltage.max` breaks; the changelog says so.
- Released in 0.2.0, which was never pushed, so 0.2.0 carries the change.
