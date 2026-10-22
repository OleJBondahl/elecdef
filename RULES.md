# elecdef: rules

Every implementation and every later change follows these rules. Each rule is one sentence and
its GATE: the mechanical check that fails a breach. "Review" is the gate only where no mechanism
can see the breach, and the reason is given. The family rules F1-F17 are shared with `refdef`
and carried verbatim; the rules E1-E19 are elecdef's own and repeat no family rule.

## Family rules

These rules bind elecdef and refdef alike, and symdef where it can (symdef has one runtime dependency, so F1 does not bind it). Both repositories carry this text verbatim in `RULES.md`,
and `tests/test_family_rules.py` in each compares it to the other's last release.

- **F1.** The library declares no runtime dependency and imports only the standard library and
  itself; libraries of the family never import each other.
  GATE: `tests/test_deps.py` asserts `dependencies = []` in `pyproject.toml` and walks every
  module's imports with `ast`, allowing only `sys.stdlib_module_names` and the package.
- **F2.** Every value is a frozen dataclass or an enum; the library performs no file, network,
  clock or random access.
  GATE: `tests/test_pure.py` fails a `@dataclass` without `frozen=True` and any import or name
  from `os`, `pathlib`, `io`, `socket`, `time`, `datetime`, `random`, `secrets`, `uuid` or a
  call to `open` under `src/`.
- **F3.** Validation returns issues as values and never raises for content; only a malformed
  call (a wrong type, a wrong kind of argument, or a shape the library's `RULES.md` names as
  malformed) raises `TypeError`.
  GATE: `tests/test_check.py` runs `check` over every malformed fixture in `tests/fixtures/`
  and asserts a non-empty issue tuple and no exception; `tests/test_malformed.py` asserts
  `TypeError` for each malformed-call fixture.
- **F4.** A closed vocabulary is an enum or a typed constant, never a string.
  GATE: `tests/test_vocab.py` fails any dataclass field annotated `str` that is not in the
  allowlist that the test names and `RULES.md` lists for that library.
- **F5.** A fact has one home across the family: `symdef` draws, `elecdef` says what a thing is,
  `refdef` says what it is called, a consumer connects and lays out.
  GATE: `tests/test_boundary.py` fails a field or function named for another home, from a list each
  library keeps in the test (for elecdef: `designation`, `tag`, `svg`, `x`, `y`, `page`; for refdef:
  `rating`, `voltage`, `svg`, `x`, `y`, `page`); the rest is review, because a
  duplicated meaning under a new name is invisible to a test.
- **F6.** A caller's convention (a padding, an ordering, a default, a project class) arrives as an
  argument or a value; no general function carries a caller's default. A fact the library itself
  defines (a block's default terminal markings, the shipped scheme's signs) is not a convention.
  GATE: the tests of every option-taking function pass the option explicitly, and
  `tests/test_boundary.py` fails a module-level default that names a consumer; what counts as a
  convention is review, because a test cannot tell a convention from a fact.
- **F7.** No paid standard is cited and no standard's wording is used; open sources are used
  only with the credit block in `README.md`.
  GATE: `tests/test_wording.py` fails a standards-body abbreviation followed by digits, an
  edition year beside a table or scheme name, or a clause reference (the pattern list lives in
  the test) anywhere under `src/`, `docs/`, `README.md` or
  `CHANGELOG.md` outside the README credit block, and asserts the credit block names every
  open source a `tables/` module header declares.
- **F8.** The public surface is the names in `__all__` of the top level and of each door, read
  by `python -m <library> api`, and it changes only with the snapshot.
  GATE: `tests/test_surface.py` compares `python -m <library> api` to `docs/api-snapshot.txt`
  byte for byte, and fails an import of a non-surface name in `docs/` and `tests/guide/`.
- **F9.** Every surface name has a docstring and a runnable example on the docs site.
  GATE: `tests/test_docs.py` asserts a non-empty docstring for every surface name, one fenced
  Python block naming it under `docs/guide/`, and runs every fenced block; the strict
  Zensical docs build runs in CI.
- **F10.** Code stays lean: a function has at most 15 statements, complexity 8 and 12 branches,
  no `def` inside a `def`; a module has at most 300 code lines; a docstring is one summary line
  plus at most two lines of why.
  GATE: ruff `PLR0915=15`, `C901=8`, `PLR0912=12` in `pyproject.toml`; `tests/test_lean.py` for
  nested defs, module lines and docstring shape; every `noqa` and `ty: ignore` names its reason
  on its line, checked by the same test.
- **F11.** Versions are semantic and every surface change carries a changelog line.
  GATE: `scripts/release_guard.py` in CI fails when `docs/api-snapshot.txt` differs from the
  last tag's copy and `CHANGELOG.md` has no line under the unreleased heading, and when a name
  disappeared without a major bump (minor before 1.0).
- **F12.** A pull request that edits `DESIGN.md` or `RULES.md`, or changes
  `docs/api-snapshot.txt`, or changes a shipped table under `src/<library>/tables/`, carries a
  `Design-review:` trailer naming an approved review. The maintainer approves a change to
  `DESIGN.md` or `RULES.md`; the design reviewer approves a surface or table change, and the
  maintainer sees it at the next review.
  GATE: `scripts/design_guard.py` in CI inspects every commit in the range touching those
  paths and fails one without the trailer; branch protection requires the job.
- **F13.** A consumer's missing need is met by a reviewed surface extension, never by a
  workaround in the consumer, a private import, a copy of the rule or a consumer-specific
  default in the library.
  GATE: `tests/test_boundary.py` fails an import or a name of another family library under `src/`, and
  `tests/test_standalone.py` (F17) fails an application's name; the consumer side is review, because the library cannot see the
  consumer's tree.
- **F14.** The library is MIT licensed, and the licence covers its code and its shipped tables.
  GATE: `tests/test_licence.py` asserts `LICENSE` holds the MIT text and `pyproject.toml`
  declares `license = "MIT"`, and fails a `tables/` module header that declares an open source
  whose licence is share-alike or non-commercial.
- **F15.** One public spelling per task: a second way to build, read or print the same value is
  not added, and no operator is overloaded to build a value; arithmetic belongs only to the
  numeric value types the library's `RULES.md` names.
  GATE: `tests/test_surface.py` fails an arithmetic or bitwise dunder (`__add__`, `__or__`,
  `__truediv__` and their kin) on a surface class that `RULES.md` does not name as numeric;
  a second spelling under a new name is review, because a test cannot see that two names do one
  task.
- **F16.** An agent finds everything from one place: `AGENTS.md` in the repository and `llms.txt`
  at the docs site root name the docs site, the surface command (`python -m <library> api`),
  the guide, `DESIGN.md` and `RULES.md`, and say that a change follows `RULES.md`.
  GATE: `tests/test_agents.py` asserts both files exist, name each of those five targets, and
  that every link in them resolves in the built site (the strict Zensical docs build).
- **F17.** The library stands alone: no file in the repository names an application that uses it.
  It is written for every electrical engineer, and its examples are general.
  GATE: `tests/test_standalone.py` lowercases every word in the tracked files and fails one whose
  SHA-256 is in the test's list of application-name hashes, so the test spells no name itself.

## elecdef rules

- **E1.** The F4 allowlist for elecdef, covering fields annotated `str` or `tuple[str, ...]`,
  is `marking`, `alternates`, `markings`, `common`, `mpn`, `manufacturer`, `name`, `key`,
  `text`, `message`, `subject`.
  GATE: `tests/test_rules_lists.py` parses this rule and asserts the list equals the one
  `tests/test_vocab.py` carries.
- **E2.** A measured figure is a `Decimal` inside a `Quantity`, a count is an `int`, a flag is a
  `bool`, a derived ratio (`tolerance`) is a `Fraction`, and `float` appears nowhere.
  GATE: `tests/test_quantity.py` asserts `TypeError` for a float value; `tests/test_pure.py`
  fails an `ast.Constant` of type `float` and a `float` annotation under `src/`.
- **E3.** A `Unit` is an enum member with one `Kind` and an exact factor; conversion and
  comparison refuse a second kind.
  GATE: `tests/test_quantity.py` parametrised over every unit pair of different kinds asserts
  `TypeError` from `to`, `same` and ordering; every factor is a `Decimal` with a finite
  representation.
- **E4.** Every quantity field of a block declares its kind, and a value of another kind is
  refused at construction.
  GATE: `tests/test_kinds.py` introspects every dataclass under `src/`, fails a `Quantity`,
  `Range` or `Ranges` field without kind metadata, and constructs each with a wrong-kind value
  asserting `TypeError`.
- **E5.** A `Range` is written as `Range(Role.X, nom=, min=, max=, at=)` with an optional `typ`;
  `role` is positional and required, tolerance is a derived property, and there is no second
  constructor or helper spelling.
  GATE: `tests/test_range.py` asserts `Range(nom=U.V(24))` raises `TypeError`, fails a
  `classmethod` or `staticmethod` on `Range` and a module-level function returning a `Range`
  outside `pick`, and asserts `tolerance` returns exact `Fraction`s.
- **E6.** Current kind, frequency, utilisation code, coil state, conductor kind and ambient are
  conditions in `At`, never fields of a block; two conditions of one kind in an `At` is the
  malformed shape F3 names.
  GATE: `tests/test_kinds.py` fails a block field annotated with a condition enum (`Current`,
  `Utilisation`, `CoilState`, `ConductorKind`) or whose name, split on `_`, contains `ac`,
  `dc` or `hz`; `tests/test_malformed.py` asserts `TypeError` for two conditions of one kind.
- **E7.** `pick` returns one covering range or an issue; it never returns the first of several.
  GATE: `tests/test_pick.py` covers zero, one and two matches, inclusion by a `Range`
  condition, equality by a `Quantity` condition, identity by an enum, and an ask naming a kind
  the rows lack.
- **E8.** The library answers which stated figure applies and never whether a figure is
  acceptable: the only surface callables that return a truth value are `Quantity.same`,
  `Quantity` ordering, `Range.contains`, `Range.covers` and `At.covers`.
  GATE: `tests/test_surface.py` asserts the set of surface callables annotated `-> bool`
  equals that list; a verdict hidden behind another return type is review, because a test
  cannot read intent.
- **E9.** Blocks compose by typed fields; an application never subclasses a block, and there is one
  base class, `Block`, for the kind check only.
  GATE: `tests/test_blocks.py` asserts every block's MRO is `(cls, Block, object)` and that
  `check` reports a subclass defined in the test.
- **E10.** A composite's `pins` and `links` are computed from its sub-blocks and stored nowhere
  else; a leaf's are stored once.
  GATE: `tests/test_pins.py` fails a composite with a stored `pins` or `links` field and
  asserts the union equals the concatenation of its sub-blocks'.
- **E11.** Pin markings, their alternates and marking schemes are data in `elecdef.pins`; a
  `Coil` or `Contact` stores only the pins its author gives (`own_pins`, may be empty) and
  computes `pins` on every read from its kind, form and position, and a composite numbers its
  unnumbered contacts on every read, so `replace` never leaves a stale marking; a marking is a
  non-empty string of letters, digits and `/ + - . '`.
  GATE: `tests/test_pins.py` golden-tests every scheme (aux, main, overload, timer, plain) for
  each form and index 1-9 and the relay, contactor, contact block, overload and card numbering,
  and asserts `check` reports `BAD_MARKING` for every generated string outside the set.
- **E12.** A `Connection` belongs to the pins a block owns itself: `Coil`, `Contact`,
  `SupplyInput`, `ChannelGroup`, `Fuse`, `FuseHolder`, `Breaker`, `Overload`, `PowerSupply`,
  `Connector` and `Device` have one `connection` field, `TerminalBlock` has `sides`, and every
  other block has neither.
  GATE: `tests/test_blocks.py` asserts that exact partition over every class under `src/`.
- **E13.** `elecdef.connections` ships technology-only leaves with every range unfilled; vendor
  figures (torque, strip length, conductor ranges) never ship.
  GATE: `tests/test_connections.py` asserts every shipped leaf has `technology` set and every
  other field at its default.
- **E14.** Data tables are generated Python modules whose rows carry no origin, and a row ships
  only when the generator's input file, which records each row's origin (an open source, a
  maker's datasheet or a measurement) and its confirmation status, marks it confirmed.
  GATE: `tests/test_tables.py` fails a `tables/` module without the generated header, a row
  string containing `http`, `source` or `verified`, and any row listed in `tables/HELD.txt`;
  the generator refuses an unconfirmed row, and the status itself is review.
- **E15.** `Product(mpn, manufacturer, block, name)` is the one identity envelope; the library
  holds no supplier, price, footprint, class letter or description field.
  GATE: `tests/test_blocks.py` fails a dataclass field named exactly `supplier`, `price`,
  `footprint`, `class_letter` or `description` anywhere under `src/`.
- **E16.** `check` reports exactly the content issues the design names: an end below another, a
  repeated marking, a marking outside the character set, a link naming no pin, a figure a block
  kind needs and lacks, a class outside the catalogue; `IssueCode` has these six codes
  (`END_ORDER`, `DUPLICATE_MARKING`, `BAD_MARKING`, `DANGLING_LINK`, `MISSING_FIGURE`,
  `UNKNOWN_CLASS`) and the two that `pick` returns (`NO_RATING`, `AMBIGUOUS_RATING`), eight in all.
  GATE: `tests/test_check.py` asserts the `IssueCode` members equal these eight, has one
  fixture per member that produces it, and asserts that `check` emits only the six.
- **E17.** A block names its symbol by `Symbol(key, version)` and holds nothing else of it.
  GATE: `tests/test_blocks.py` fails a dataclass field named `symbol` whose annotation is not
  `Symbol | None` and any dataclass field named exactly `geometry`, `port`, `outline` or `glyph`.
- **E18.** For F15, `Quantity` is the only numeric value type, and in v1 it defines comparison
  dunders only; no surface class defines an arithmetic or bitwise dunder.
  GATE: `tests/test_surface.py` asserts no arithmetic or bitwise dunder on any surface class
  and comparison dunders on `Quantity` alone.
- **E19.** Coverage never falls below 95 % per module, and `ty check` passes.
  GATE: `pytest --cov=elecdef --cov-fail-under=95` and `ty check` in CI.
