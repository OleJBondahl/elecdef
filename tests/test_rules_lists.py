"""Gate E1: the name lists in `[tool.family]` equal the lists `RULES.md` states."""

import re

import family
from test_vocab import E1_ALLOWLIST

BACKTICKED = re.compile(r"`([^`]+)`")


def backticked(text: str) -> list[str]:
    """The backticked spans of `text`, in order."""
    return BACKTICKED.findall(text)


def rule_text(rules_text: str, rule: str) -> str:
    """The bullet `- **<rule>.**` of `rules_text`, its continuation lines joined by spaces."""
    lines = rules_text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(f"- **{rule}.**"))
    parts = [lines[start]]
    for line in lines[start + 1 :]:
        if not line.strip() or line.startswith("- **"):
            break
        parts.append(line.strip())
    return " ".join(parts)


def elecdef_names(rules_text: str, rule: str) -> list[str]:
    """The names `rule` lists for elecdef: E1 after its last " is ", F5 after "for elecdef:"."""
    body = rule_text(rules_text, rule)
    if rule == "E1":
        span = body.rsplit(" is ", 1)[1].split("GATE:")[0]
    else:
        span = body.split("for elecdef:", 1)[1].split(";", 1)[0]
    return backticked(span)


def lists_equal(rules_text: str, rule: str, names) -> bool:
    """True when the names `rule` lists for elecdef are exactly `names`, in order."""
    return elecdef_names(rules_text, rule) == list(names)


RULES_TEXT = (family.ROOT / "RULES.md").read_text(encoding="utf-8")


def test_e1_names_equal_allowlist_and_pyproject():
    assert lists_equal(RULES_TEXT, "E1", E1_ALLOWLIST)
    assert lists_equal(RULES_TEXT, "E1", family.family_config()["str_allowlist"])


def test_f5_names_equal_pyproject_boundary_names():
    assert lists_equal(RULES_TEXT, "F5", family.family_config()["boundary_names"])


def test_backticked_returns_spans_in_order():
    assert backticked("a `x`, b `yy`, `z`") == ["x", "yy", "z"]


def test_rule_text_stops_at_next_bullet():
    text = "- **A1.** one\n  GATE: `t`\n- **A2.** two\n  `u`\n"
    assert rule_text(text, "A1") == "- **A1.** one GATE: `t`"


def test_rule_text_stops_at_blank_line():
    text = "- **A1.** one\n\n  more\n"
    assert rule_text(text, "A1") == "- **A1.** one"


def test_lists_equal_can_fail_on_synthetic_text():
    text = "- **E1.** The list is `a`, `b`.\n  GATE: `x`\n"
    assert lists_equal(text, "E1", ["a", "b"])
    assert not lists_equal(text, "E1", ["a", "c"])
    assert not lists_equal(text, "E1", ["a"])


def test_lists_equal_can_fail_on_altered_real_text():
    altered = RULES_TEXT.replace("`subject`.", "`subjects`.", 1)
    assert altered != RULES_TEXT
    assert not lists_equal(altered, "E1", E1_ALLOWLIST)


def test_f5_can_fail_on_synthetic_text():
    text = "- **F5.** Fact. GATE: `t` (for elecdef: `designation`, `tag`; for refdef: `rating`).\n"
    assert lists_equal(text, "F5", ["designation", "tag"])
    assert not lists_equal(text, "F5", ["designation", "rating"])
