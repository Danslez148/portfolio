"""Tests for baseline.py. Its numbers go straight into the paper's optimisation
result, so it gets the same scrutiny as everything else.

Cancer and mushroom only, since both run well under a second. Bank's `measure()`
takes about 55s (5 repeats of a ~5.3s naive pass), so it stays out of the suite like
`data-bank.lp` does elsewhere. We check it by running
`python -m eccrs_workbench.evaluate --full` and comparing the numbers with
tests/fixtures/evaluation.json.
"""

from __future__ import annotations

from eccrs_workbench import baseline
from eccrs_workbench.base_rank import base_rank
from eccrs_workbench.parser import parse_instances, parse_rules, safe_label_atom
from eccrs_workbench.sat import count_calls
from tests.examples import REPO


def test_measure_matches_the_documented_cancer_figures():
    """The committed figures (tests/fixtures/evaluation.json): cancer naive 360, shipped
    400, collapsed 64, base_rank 23, peak clause size 19. Pinned so a silent regression
    in any of the three query paths is caught before it reaches the paper."""
    m = baseline.measure(
        "cancer", "datasets/cancer/rules.txt", "datasets/cancer/data-cancer.lp"
    )
    assert m.rules == 12
    assert m.rule_atoms == 6
    assert m.distinct_ranks == 4
    assert m.patterns == 64
    assert m.applicable_rule_set_classes == 10
    assert m.base_rank_calls == 23
    assert m.naive_total_calls == 360
    assert m.shipped_total_calls == 400
    assert m.collapsed_total_calls == 64
    assert m.peak_clause_set_size == 19


def test_measure_matches_the_documented_mushroom_figures():
    m = baseline.measure(
        "mushroom", "datasets/mushroom/rules.txt", "datasets/mushroom/data-mushroom.lp"
    )
    assert m.rule_atoms == 10
    assert m.distinct_ranks == 3
    assert m.patterns == 1024
    assert m.applicable_rule_set_classes == 11
    assert m.base_rank_calls == 24
    assert m.naive_total_calls == 5440
    assert m.shipped_total_calls == 6144
    assert m.collapsed_total_calls == 66


def test_base_rank_calls_matches_an_independent_instrumented_count():
    ruleset = parse_rules(REPO / "datasets" / "cancer" / "rules.txt")
    instances = parse_instances(REPO / "datasets" / "cancer" / "data-cancer.lp")
    label_atom = safe_label_atom(ruleset, instances)
    with count_calls() as c:
        base_rank(ruleset.to_kb(label_atom))
    independent_calls = c.calls

    m = baseline.measure(
        "cancer", "datasets/cancer/rules.txt", "datasets/cancer/data-cancer.lp"
    )
    assert m.base_rank_calls == independent_calls


def test_naive_and_shipped_and_collapsed_are_internally_consistent():
    for name, rules, lp in [
        ("cancer", "datasets/cancer/rules.txt", "datasets/cancer/data-cancer.lp"),
        ("mushroom", "datasets/mushroom/rules.txt", "datasets/mushroom/data-mushroom.lp"),
    ]:
        m = baseline.measure(name, rules, lp)
        assert m.collapsed_total_calls <= m.shipped_total_calls
        assert m.shipped_mean_calls == m.shipped_total_calls / m.patterns
        assert (
            m.collapsed_mean_calls
            == m.collapsed_total_calls / m.applicable_rule_set_classes
        )
        for count in (
            m.base_rank_calls,
            m.naive_total_calls,
            m.shipped_total_calls,
            m.collapsed_total_calls,
        ):
            assert count >= 0
        for wall_clock in (
            m.wall_clock_naive_s,
            m.wall_clock_shipped_s,
            m.wall_clock_collapsed_s,
        ):
            assert wall_clock >= 0.0


def test_render_names_every_dataset_and_its_speedup():
    m = baseline.measure(
        "cancer", "datasets/cancer/rules.txt", "datasets/cancer/data-cancer.lp"
    )
    text = baseline.render([m])
    assert "cancer" in text
    assert "23" in text  # base_rank_calls
    assert "400 -> 64" in text  # shipped -> collapsed, the headline reduction
