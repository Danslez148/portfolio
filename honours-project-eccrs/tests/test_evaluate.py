"""Tests for the final evaluation run (evaluate.py).

One command produces every number the paper's results section needs, written to
committed machine-readable files. These tests cover the fast paths only (rules.txt,
instances.csv and the pattern space). The full `.lp` path works but is slow (16-18 MB
files), so we check it by running `python -m eccrs_workbench.evaluate --full` and
reading the output, the same reason `data-bank.lp` and `data-mushroom.lp` stay out
of the rest of the suite.
"""

from __future__ import annotations

import json

import pytest

from eccrs_workbench import evaluate, report
from eccrs_workbench.base_rank import base_rank
from eccrs_workbench.parser import parse_rules
from tests.examples import EXPECTED_MSW, FIXTURES, INSTANCE_A, REPO


def _scholarship_ranked():
    ruleset = parse_rules(FIXTURES / "scholarship.rules.txt")
    return ruleset, base_rank(ruleset.to_kb())


# population_stats: the three-way partition (agree / disagree / both-abstain)


def test_population_stats_partitions_add_up_to_n():
    ruleset, ranked = _scholarship_ranked()
    agreement = report.over_patterns(ruleset, ranked)
    stats = evaluate.population_stats(agreement)
    assert stats["n"] == 32
    assert stats["agree"] + stats["disagree"] + stats["both_abstain"] == 32


def test_population_stats_counts_empty_applicable_patterns_as_both_abstain_not_agree():
    """Scholarship has 12 of 32 patterns with an empty applicable set.
    MSW abstains there, and per the alignment theorem's case 1 so does RC -- so those
    12 must land in both_abstain, not silently inflate the agree count the way
    `Row.agrees` (None == None) would if used directly."""
    ruleset, ranked = _scholarship_ranked()
    agreement = report.over_patterns(ruleset, ranked)
    stats = evaluate.population_stats(agreement)
    assert stats["both_abstain"] == 12


def test_population_stats_the_one_known_divergence_is_not_both_abstain():
    """The scholarship counter-example: MSW abstains (tie r3/r5) but RC entails class
    1. Not-equal labels, so it belongs in `disagree`, not `both_abstain`."""
    ruleset, ranked = _scholarship_ranked()
    agreement = report.over_patterns(ruleset, ranked)
    stats = evaluate.population_stats(agreement)
    assert stats["disagree"] == 1
    assert stats["agree"] == 32 - 12 - 1


def test_population_stats_agreement_pct_counts_mutual_abstention_as_agreement():
    """The theorem (Madzime2026 5, 7.1) counts both sides abstaining as agreement
    ("agree exactly... including the case where both abstain"), and the existing
    `report.Agreement.rate` already does (test_scholarship_alignment.py's positive
    control). So `agreement_pct` has to count both_abstain in the numerator, not just
    `agree`."""
    ruleset, ranked = _scholarship_ranked()
    agreement = report.over_patterns(ruleset, ranked)
    stats = evaluate.population_stats(agreement)
    assert stats["agreement_pct"] == pytest.approx(
        (stats["agree"] + stats["both_abstain"]) / 32
    )
    assert stats["agreement_pct"] == pytest.approx(31 / 32)


def test_population_stats_agreement_pct_matches_the_existing_agreement_rate():
    ruleset, ranked = _scholarship_ranked()
    agreement = report.over_patterns(ruleset, ranked)
    stats = evaluate.population_stats(agreement)
    assert stats["agreement_pct"] == pytest.approx(agreement.rate)


# evaluate_dataset: one dataset end to end, fast path only


def test_evaluate_dataset_cancer_matches_known_numbers():
    result = evaluate.evaluate_dataset(
        "cancer",
        REPO / "datasets" / "cancer" / "rules.txt",
        REPO / "datasets" / "cancer" / "instances.csv",
        REPO / "datasets" / "cancer" / "data-cancer.lp",
        include_lp=False,
    )
    assert result.rules == 12
    assert result.rule_atoms == 6
    assert result.patterns_total == 64
    assert result.patterns_realisable == 64  # cancer has no one-hot families
    assert result.applicable_rule_set_classes == 10  # as in test_pattern_classes
    assert result.validator_violations == []
    assert result.csv_holdout["n"] == 175
    assert result.csv_holdout["agree"] == 175
    assert result.csv_holdout["both_abstain"] == 0
    assert result.pattern_space["n"] == 64
    assert result.pattern_space["agree"] == 64
    assert result.divergences == []
    assert result.lp_instances is None  # include_lp=False


@pytest.mark.parametrize(
    "name, expected_classes",
    [
        ("cancer", 10),
        ("mushroom", 11),
        ("bank", 17),
    ],
)
def test_evaluate_dataset_all_three_agree_everywhere_over_csv_and_patterns(
    name, expected_classes
):
    result = evaluate.evaluate_dataset(
        name,
        REPO / "datasets" / name / "rules.txt",
        REPO / "datasets" / name / "instances.csv",
        REPO / "datasets" / name / f"data-{name}.lp",
        include_lp=False,
    )
    assert result.applicable_rule_set_classes == expected_classes
    assert result.csv_holdout["disagree"] == 0
    assert result.csv_holdout["both_abstain"] == 0
    assert result.pattern_space["disagree"] == 0
    assert result.pattern_space["both_abstain"] == 0
    assert result.pattern_space["agreement_pct"] == 1.0
    assert result.empty_applicable_patterns == 0
    assert result.divergences == []


def test_evaluate_dataset_reports_validator_violations_when_present():
    result = evaluate.evaluate_dataset(
        "scholarship", FIXTURES / "scholarship.rules.txt", None, None, include_lp=False
    )
    assert any(v.startswith("strict closure") for v in result.validator_violations)
    assert result.pattern_space["n"] == 32
    assert result.pattern_space["disagree"] == 1
    assert result.pattern_space["both_abstain"] == 12
    assert result.empty_applicable_patterns == 12
    assert len(result.divergences) == 1
    div = result.divergences[0]
    assert div["msw_label"] is None
    assert div["rc_label"] == 1
    # the divergence is the all-atoms-true pattern: every rule atom positive, none negated
    assert "~" not in div["pattern"]
    assert all(f"a({i})" in div["pattern"] for i in range(1, 6))


def test_evaluate_dataset_csv_holdout_is_none_without_a_csv_path():
    result = evaluate.evaluate_dataset(
        "scholarship", FIXTURES / "scholarship.rules.txt", None, None, include_lp=False
    )
    assert result.csv_holdout is None


# the scholarship worked example (Instance A), for the paper


def test_scholarship_instance_a_trace_matches_the_literature():
    ruleset, ranked = _scholarship_ranked()
    pattern, expected_label = EXPECTED_MSW["A"]
    assert pattern == INSTANCE_A
    trace = evaluate.instance_a_trace(ruleset, ranked, INSTANCE_A)
    assert "AGREE" in trace
    assert f"label = {expected_label}" in trace


# writing the committed output files


def test_write_outputs_round_trips_through_json_and_csv(tmp_path):
    result = evaluate.evaluate_dataset(
        "cancer",
        REPO / "datasets" / "cancer" / "rules.txt",
        REPO / "datasets" / "cancer" / "instances.csv",
        REPO / "datasets" / "cancer" / "data-cancer.lp",
        include_lp=False,
    )
    evaluate.write_outputs([result], tmp_path, scholarship=None)

    json_path = tmp_path / "evaluation.json"
    csv_path = tmp_path / "agreement.csv"
    assert json_path.exists()
    assert csv_path.exists()

    data = json.loads(json_path.read_text())
    assert data["datasets"][0]["name"] == "cancer"
    assert data["datasets"][0]["pattern_space"]["n"] == 64

    csv_text = csv_path.read_text()
    assert "cancer" in csv_text
    assert "pattern_space" in csv_text
    # header + at least (csv_holdout, pattern_space) rows for one dataset
    assert len(csv_text.strip().splitlines()) >= 3


def test_default_output_folder_is_results():
    assert evaluate.DEFAULT_OUT_DIR == REPO / "results"


def test_render_summary_mentions_every_dataset():
    results = [
        evaluate.evaluate_dataset(
            "cancer",
            REPO / "datasets" / "cancer" / "rules.txt",
            REPO / "datasets" / "cancer" / "instances.csv",
            REPO / "datasets" / "cancer" / "data-cancer.lp",
            include_lp=False,
        )
    ]
    summary = evaluate.render_summary(results)
    assert "cancer" in summary
