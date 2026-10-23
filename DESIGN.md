# elecdef: design

`elecdef` defines what electrical and electronic things are: a coil, a contact, a terminal, a
connection, a fuse, a power supply, a PLC channel, a conductor, a cable. Each is a block with
typed, exact, kind-checked values, its pin markings and its internal links. This file is the
current truth of the model; `RULES.md` is the rule set every change follows.

## 1. Purpose

elecdef is for every electrical and electronic engineer working in Python: one typed, exact
definition of each basic thing in the electrical world, so that nobody types a coil, a contact or
a cable again. A parts library describes a real product by filling the blocks' values. An
application, a script or a notebook reads the values through one small typed surface. The
library judges nothing: it holds facts and looks them up. It has no runtime dependency and
runs with or without the rest of the family.

## 2. The family

| Library | Owns | Never holds |
|---|---|---|
| `symdef` | how a thing is drawn: symbols, frames, ports, geometry | a rating, a unit, a marking's meaning |
| `elecdef` | what a thing is: blocks, values, markings, internal links | a coordinate, a page, a designation string, a drawing key's meaning |
| `refdef` | what a thing is called: designations, levels, letter codes, numbering, sort | a device fact, a marking's meaning |
| an application | how a project connects, lays out, checks and prints | a copy of any fact above |

A fact lives in exactly one library. A block names its symbol by a `Symbol(key, version)` and
reads nothing from `symdef`. A pin marking (`13`, `A1`, `95`) is an elecdef fact; the string
`-K1:13` is a refdef fact; which wire lands on it is the application's fact.

## 3. Core model

### 3.1 Values

A `Quantity` is a `Decimal` and a `Unit`. A `Unit` is an enum member carrying a symbol, a `Kind`
(voltage, current, power, apparent power, resistance, frequency, time, length, area, gauge,
torque, ratio, temperature, temperature difference) and an exact factor to the kind's base unit.
`U.V(24)`, `U.MM2("2.5")` is the one spelling; a `float` is refused. `==` compares as written,
`same()` and ordering compare in base units, `to(unit)` converts within a kind and refuses across
kinds. Percent is a unit of kind ratio. Degrees Celsius and kelvin are different kinds.

A `Range` is written the way a datasheet states it: a role and up to three ends.

```python
Range(Role.RATED, nom=U.V(24), min=U.V("20.4"), max=U.V(30), at=At(Current.DC))
Range(Role.LIMITING, max=U.V(250))
Range(Role.REFERENCE, min=U.DEG_C(23), max=U.DEG_C(27))
```

`role` is positional and required: `RATED` is what the maker states for the stated conditions,
`LIMITING` is an extreme the thing withstands, `REFERENCE` is the band other figures are stated
for. `nom` is the marked value; an optional `typ` holds a measured typical and is never confused
with it. `tolerance` is a property returning exact fractions derived from the ends; it is never
written. Every end has one kind. `contains(quantity)` and `covers(range)` are the two tests.

`At` is the set of conditions a figure holds under, one per kind: a `Quantity` (at 400 V), a
`Range` (up to 250 V), or an enum member (`Current.DC`, `Utilisation.AC_3`, `CoilState.HOLD`,
`ConductorKind.FINE`). A condition's kind is its unit's kind or its enum class. AC and DC are
conditions, not fields, so one `Ranges` field (a tuple of `Range`) holds the 50 Hz, the 60 Hz
and the DC figures side by side.

### 3.2 Lookup

`pick(ranges, *ask) -> Pick(found, issue)` returns the single range whose conditions cover the
ask. A `Range` condition covers by inclusion, a `Quantity` by equality in base units, an enum by
identity. A row may state more kinds than the ask names; the ask may not name a kind the row
lacks. No covering row gives the issue `NO_RATING`; more than one gives `AMBIGUOUS_RATING`;
there is no silent first match. This is data access. Whether a load is acceptable against the
found range is the application's check, and elecdef stops at `found`.

### 3.3 Blocks

A block is a frozen dataclass stating what one kind of thing is. Every property may be unfilled.
A property is a `Quantity` for a dimension or a count-like figure, a `Range` for an electrical
figure, `Ranges` when it varies with conditions, an enum for a closed vocabulary, `int` or `bool`
otherwise. Every quantity field declares its kind; a value of another kind is refused at
construction. A field that holds a closed set is an enum, never a string.

Blocks compose by typed fields, by value: `Relay.coil: Coil`, `Relay.contacts: tuple[Contact,
...]`, `Coil.connection: Connection`. A leaf defined once is passed by reference into every block
that has it; equality is by value. `elecdef.connections` ships technology-only leaves (`SCREW`,
`PUSH_IN`, ...) with ranges unfilled; a parts library derives its vendor leaves from them with
`dataclasses.replace` and shares those. Family identity of a derived leaf is not tracked. A
`Connection` belongs to the pins a block owns itself: a block that owns pins directly has one
`connection` field (a terminal block has one per side in `sides`), and a block whose pins all
come from its sub-blocks has none. So `Coil`, `Contact`, `SupplyInput`, `ChannelGroup`, `Fuse`,
`FuseHolder`, `Breaker`, `Overload`, `PowerSupply` (its output pins), `Connector` and `Device`
carry one; `Relay`, `Contactor`, `ContactBlock`, `PlcCard` and `Computer` carry none.

There is one base class, `Block`, for mechanism only: it runs the kind check and normalises a
bare `Range` given to a `Ranges` field. An application never subclasses a block; `check` reports a
block whose class is not in the catalogue. A family template and a product are the same class:
the template holds ranges and gaps, the product holds values.

### 3.4 Pins, markings and links

A `Pin` is `(marking, role, side, alternates)`; a `Link` is `(markings, kind, closed_at_rest)`, `markings` a pair, with
kind `CONDUCTIVE`, `SWITCHED` or `PROTECTIVE`. Markings follow the block: `elecdef.pins` derives
them by form, index and `Marking` scheme (`AUX` n3-n4, n1-n2, n1-n2-n4; `MAIN` 1/L1-2/T1 ...;
`OVERLOAD` 95-96, 97-98; `TIMER` n5-n6-n8; `PLAIN` 1-8) with alternates as data. A composite
numbers its unnumbered sub-blocks on every read: a relay's contacts 1..n, a contactor's main
poles then its auxiliaries, a contact block from `numbered_from`, a card's channels across its
groups. A product may give pins outright; a coil or contact stores only those and computes the rest, so `replace` never leaves a stale marking. A composite's `pins` and `links` are computed over its
sub-blocks and stored nowhere else. A marking is a non-empty string of letters, digits and
`/ + - . '`, so every marking reads back unchanged in a designation string such as `-K1:13`.

### 3.5 Product

`Product(mpn, manufacturer, block, name)` is the one identity envelope: a block with its values
filled, under a maker's part number. An application wraps it in its own record (suppliers,
footprint, class letter) and never copies a block value out of it.

### 3.6 Issues

`check(block | product) -> tuple[Issue, ...]` reports content problems as values: an end below
another, a marking that repeats, a marking outside the character set, a link naming no pin, a
block kind missing a figure it needs, a class outside the catalogue. An `Issue` is `(code:
IssueCode, message, subject)`. `IssueCode` has eight members: the six that `check` reports and the
two that `pick` returns (`NO_RATING`, `AMBIGUOUS_RATING`). A malformed call (a wrong type, a wrong
kind, two conditions of one kind in an `At`) raises `TypeError`; content never does.

## 4. v1 catalogue

| Block | Reuses | States |
|---|---|---|
| `Body` | - | width, height, depth; ip; temperature (rated, storage); mounting |
| `Connection` | - | technology; conductor area per conductor kind; AWG as stated; conductors per clamp; strip length; torque; screw; pitch; material |
| `Rating` | - | operational voltage per current kind; insulation and impulse voltage; thermal current; current per current kind and conditions; power loss; frequency; overvoltage category; pollution degree |
| `SupplyInput` | Connection | what a powered thing draws: voltage and current per conditions; its supply pins |
| `Contact` | Connection | form (make, break, changeover) and features; switching current per voltage, current kind and utilisation code; limiting voltage per current kind; minimum load; material; life |
| `Coil` | Connection | kind; voltage per current kind and frequency; pick-up and drop-out as ratio; resistance; power and apparent power per coil state; times; suppression; A1-A2 |
| `Conductor` | - | material; class; area; insulation; temperature; colour; voltages |
| `Cable` | Conductor | cores (number, colour, pair, drain); screen; armour; diameter; bend radii; sheath; temperature; flags; opaque type code with scheme |
| `TerminalBlock` | Connection per side, Rating, Body | kind; levels with marking and potential; sides; cross-section; width; rail |
| `Relay` | Coil, Contact, Body | kind; contacts; latching; force-guided; timer function |
| `Contactor` | Coil, Contact, Rating, Body | main poles; auxiliaries (a mirror contact is an auxiliary with that feature) |
| `ContactBlock` | Contact, Body | a coil-less carrier: snap-on auxiliary block, button block, limit switch; actuator; first number |
| `Overload` | Contact, Connection, Body | poles; setting; trip class; reset; phase failure; auxiliaries |
| `Fuse`, `FuseHolder` | Connection, Rating, Body | system; class; current; voltage and breaking capacity per current kind; speed; indicator; poles; disconnect |
| `Breaker` | Connection, Rating, Contact, Body | poles; current; curve; breaking capacities; auxiliaries |
| `PowerSupply` | SupplyInput, Contact, Connection, Body | kind; input; output voltage and current; boost; hold-up; overload behaviour; circuit class; isolation; redundancy; efficiency; OK contact (`ok_contact`) |
| `Channel`, `ChannelGroup` | Connection | signal and number; digital input, digital output, analog or relay data; a group's markings, commons, isolation and connection, written once for many channels |
| `PlcCard` | SupplyInput, ChannelGroup, Body | form; role; bus; groups; safety levels |
| `Connector` | Rating, Connection, Body | family; coding; poles; gender; locking |
| `Computer` | SupplyInput, Connector, Body | supply; power; ports |
| `Device` | Rating, Connection, Body | pins and links given outright: the typed fallback for a thing with no block yet |

Vocabularies ship as enums in `elecdef.vocab`: industry codes are the member names
(`Utilisation.AC_3`, `FuseClass.gG`, `TripCurve.C`) with short descriptions in our own words.
Data tables ship as generated Python in `elecdef.tables`: the cross-section series, the AWG
formula, colour letter codes, the 44-core colour sequence, breaker curve bands, trip classes,
cable voltage digits, overvoltage categories, the E series. A table row ships only when its
value is confirmed; a contested row waits.

## 5. Public surface

Top level (`elecdef.__all__`): `Unit`, `Quantity`, `Range`, `Ranges`, `Role`, `At`, `pick`,
`Pick`, `Issue`, `IssueCode`, `check`, `Symbol`, `Product`, `Body`, `Rating`, `Connection`,
`Contact`, `Coil`, `Relay`, `Contactor`, `ContactBlock`, `Overload`, `TerminalBlock`, `Fuse`,
`Breaker`, `PowerSupply`, `PlcCard`, `Device`. Twelve doors, each with its own `__all__` of the
names not exported at top level: `elecdef.vocab` (`Kind` and every vocabulary enum),
`elecdef.pins` (`Pin`, `PinRole`, `Side`, `Link`, `LinkKind`, `Marking` and the marking
functions), `elecdef.connections` (`SCREW`, `SPRING_CAGE`, `PUSH_IN`, `TENSION`, `IDC`, `CRIMP`,
`SOLDER`, `PRESS_IN`, `PLUG_IN`, `BOLT`, `WIRE_WRAP`, `THT`, `SMD`), `elecdef.tables`,
`elecdef.supply` (`SupplyInput`), `elecdef.fuse` (`FuseHolder`), `elecdef.plc` (`Channel`,
`ChannelGroup`, `DigitalInput`, `DigitalOutput`, `AnalogIo`), `elecdef.terminal` (`Level`),
`elecdef.conductor` (`Conductor`), `elecdef.cable` (`Cable`, `Core`, `TypeCode`),
`elecdef.connector` (`Connector`), `elecdef.computer` (`Computer`, `Port`). The examples in this file assume `from elecdef import
Unit as U`. `python -m elecdef api` prints every surface name with its signature and docstring;
`docs/api-snapshot.txt` is that output, and a test fails when they differ.

## 0.2.0 surface (2026-10-23)

`Rating.current` is the rated current as `Ranges`, per current kind and conditions: a datasheet states the AC and the DC rating side by side, each with its own conditions. `Rating.thermal_current` stays beside it, because the thermal current is another datasheet figure and the two are never one fact. `Rating.power_loss` is the power a part dissipates, one `Range` with the load in `at`; several loads are several `Rating`s. Both new fields follow `pollution_degree`, so positional calls from 0.1.0 keep their meaning.

`Contact.voltage` is the limiting voltage as `Ranges`, per current kind, the same shape as `Rating.voltage`. A contact has one limiting voltage for alternating current and another for direct current, which one `Range` cannot say. A bare `Range` passed in is wrapped into a one-item tuple, so a 0.1.0 call that builds a `Contact` from one `Range` still builds. A 0.1.0 reader of `contact.voltage.max` breaks, and the changelog says so. The supply blocks need no change: a rated 24 V with its operating window is one `Range` (nom, min, max).

The three needs behind this section are N11 (current as `Ranges`), N12 (power loss) and N13 (`Contact.voltage` as `Ranges`, ruled in for that field only, F12-approved under `SPEC-ELECDEF`).

## 6. Out of scope

Checks and judgements (is this load acceptable, is this wire big enough), derating and
temperature factors, conductor resistance, cable type-code decoding (the `Scheme` enum and the
opaque `TypeCode` leave the slot), calculations across blocks, instances and topology, where a
pin is wired, drawing, designations and PLC tags, file reading or writing, multilingual names,
assemblies of several products. Pilot devices, sensors, motors, passives and semiconductors
arrive as blocks after v1; until then they are a `Device`.

## 7. Docs and agents

The repository publishes a GitHub Pages site built with Zensical (as `symdef` does) from the first
public release. The site holds this design, the rules, a guide with one runnable example per
surface name, and an API reference generated from the docstrings, so a name documented in code
is documented on the site by construction. The strict Zensical docs build runs in CI.

`llms.txt` at the site root lists, in plain text, what the library is, the surface names, the
guide pages and the rules, with one link each. `AGENTS.md` at the repository root tells an
agent: read `DESIGN.md` then `RULES.md`; read the surface with `python -m elecdef api` and never
the source to use the library; every public name has an example under `docs/guide/`; the tests
named in `RULES.md` are the definition of done; a change that touches the surface, the design or
the rules needs a design review before it is written.

## 8. How it changes

Semantic versioning. Every surface change carries a changelog line. A pull request that edits
`DESIGN.md` or `RULES.md`, changes `docs/api-snapshot.txt` or changes a shipped table under
`src/elecdef/tables/`, carries a `Design-review:` trailer naming an approved review; a guard
script fails it otherwise. An application's missing need is never met by a workaround in the
application or a private path into the library: it is a reviewed design change that extends the
surface. An application that adopts elecdef shrinks: it deletes its copy of the fact and reads
the surface.

Who approves is family rule F12: the maintainer approves the contract, and the design reviewer approves surface and table changes.

## 9. Licence

MIT, covering the code and the shipped tables. An open source used for a table is credited in
the README and is never share-alike or non-commercial.
