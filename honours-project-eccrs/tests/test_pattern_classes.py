"""Tests for the applicable-rule-set collapse of the 2^a feature patterns.

MSW and RC only look at which rule bodies a complete pattern F satisfies.
`collapse_patterns` groups patterns by that set with a subset test (no SAT) and
evaluates each operator once per class instead of once per pattern.

`report.over_patterns` stays the reference oracle: the collapsed statistics have to
match it exactly, class for class and in total.
"""

from __future__ import annotations

import pytest

from eccrs_workbench import msw
from eccrs_workbench.base_rank import base_rank
from eccrs_workbench.parser import parse_rules
from eccrs_workbench.report import collapse_patterns, complete_patterns, over_patterns
from tests.examples import FIXTURES, REPO


def _dataset_rules(name: str):
    return parse_rules(REPO / "datasets" / name / "rules.txt")


# Full-pattern-space class counts, from an independent grouping.
# Do NOT adjust these to match the code: a mismatch is a finding.
EXPECTED_CLASSES = {"cancer": 10, "mushroom": 11, "bank": 17}


@pytest.mark.parametrize("name, expected", EXPECTED_CLASSES.items())
def test_full_pattern_space_collapses_to_the_expected_class_count(name, expected):
    ruleset = _dataset_rules(name)
    collapsed = collapse_patterns(ruleset, base_rank(ruleset.to_kb()))
    assert len(collapsed.classes) == expected


EXPECTED_OVERRIDE_PATTERNS = {
    "cancer": (24, 64),
    "mushroom": (320, 1024),
    "bank": (6656, 16384),
}


@pytest.mark.parametrize("name, expected", EXPECTED_OVERRIDE_PATTERNS.items())
def test_full_pattern_space_override_count(name, expected):
    expected_overridden, expected_total = expected
    ruleset = _dataset_rules(name)
    total = 0
    overridden = 0
    for pattern in complete_patterns(ruleset.atoms):
        total += 1
        applicable = msw.applicable(ruleset, pattern)
        if len(msw.maximal(applicable)) < len(applicable):
            overridden += 1
    assert total == expected_total
    assert overridden == expected_overridden


# The five rulesets the collapse must be exact on: the three learned datasets and both
# scholarship fixtures (one fails the alignment hypotheses, one passes them).
RULESETS = {
    "cancer": lambda: _dataset_rules("cancer"),
    "mushroom": lambda: _dataset_rules("mushroom"),
    "bank": lambda: _dataset_rules("bank"),
    "scholarship": lambda: parse_rules(FIXTURES / "scholarship.rules.txt"),
    "scholarship_closed": lambda: parse_rules(FIXTURES / "scholarship_closed.rules.txt"),
}


def _sig(ruleset, pattern):
    return frozenset(rule.id for rule in msw.applicable(ruleset, pattern))


@pytest.fixture(scope="module")
def swept(request):
    ruleset = RULESETS[request.param]()
    ranked = base_rank(ruleset.to_kb())
    return ruleset, over_patterns(ruleset, ranked), collapse_patterns(ruleset, ranked)


@pytest.mark.parametrize("swept", RULESETS, indirect=True)
def test_both_labels_are_constant_within_every_applicable_rule_set_class(swept):
    ruleset, reference, _ = swept

    by_class: dict[frozenset[str], set[tuple]] = {}
    for row in reference.rows:
        by_class.setdefault(_sig(ruleset, row.pattern), set()).add(
            (row.msw_label, row.rc_label, row.vacuous)
        )
    for signature, verdicts in by_class.items():
        assert len(verdicts) == 1, f"class {sorted(signature)} is not constant"


@pytest.mark.parametrize("swept", RULESETS, indirect=True)
def test_collapsed_statistics_are_identical_to_the_exhaustive_sweep(swept):
    ruleset, reference, collapsed = swept

    assert collapsed.total == reference.total
    assert collapsed.agreeing == reference.agreeing
    assert collapsed.rate == reference.rate
    assert collapsed.abstentions == reference.abstentions
    assert collapsed.vacuous == reference.vacuous

    diverging_patterns = sum(c.count for c in collapsed.divergences)
    assert diverging_patterns == len(reference.divergences)
    assert {c.applicable for c in collapsed.divergences} == {
        _sig(ruleset, row.pattern) for row in reference.divergences
    }


@pytest.mark.parametrize("swept", RULESETS, indirect=True)
def test_realisable_subset_survives_the_collapse(swept):
    _, reference, collapsed = swept

    assert collapsed.realisable_total == reference.realisable_total
    assert collapsed.realisable_agreeing == reference.realisable_agreeing
    assert collapsed.realisable_rate == reference.realisable_rate
    assert collapsed.realisable_divergence_patterns == len(
        reference.realisable_divergences
    )
    for c in collapsed.classes:
        assert c.realisable + c.unrealisable == c.count
