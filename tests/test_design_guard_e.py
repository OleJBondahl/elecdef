"""The design-review exemption list holds exactly the two ED-4 commits whose trailer slipped."""

import tomllib

import family

# ED-4 trailer slip 2026-10-22: the Design-review line sat behind a blank line, so git parsed none.
SLIPPED = {
    "4eea0fda95b85b12fc30e69aa56fb440172df11b",
    "54639f10ed62916d1750ad8d042456d7cf393e39",
}


def test_the_exempt_list_is_exactly_the_two_slipped_commits():
    config = tomllib.loads((family.ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert set(config["tool"]["family"]["design_review_exempt"]) == SLIPPED
    assert len(config["tool"]["family"]["design_review_exempt"]) == 2
