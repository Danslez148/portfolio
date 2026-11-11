"""The alignment theorem, as a test.

Madzime (2026) 4: if a ruleset has strict global exception
closure, sanity and no total override, RC on the translated KB agrees exactly with
the original ruleset's MSW predictions, including abstaining where no rule applies.

The five-rule scholarship set doesn't meet those conditions (test_validator.py), so
here it's used for the four published instances and to show where the guarantee
stops. The theorem itself is tested on a ruleset that does meet them, and at scale
in test_cancer_integration.py.
"""

from eccrs_workbench import msw, report
from eccrs_workbench.base_rank import base_rank
from eccrs_workbench.parser import parse_rules
from eccrs_workbench.rational_closure import classify
from eccrs_workbench.validator import validate
from tests.examples import EXPECTED_MSW, FIXTURES, pattern


def test_published_instances_agree(scholarship):
    """Instances A-D: award / deny / award / abstain, both sides."""
    ranked = base_rank(scholarship.to_kb())
    for name, (instance, expected) in EXPECTED_MSW.items():
        assert msw.predict(scholarship, instance) == expected, f"MSW, instance {name}"
        assert classify(ranked, instance) == expected, f"RC, instance {name}"


def test_the_only_divergence_is_where_the_hypotheses_fail(scholarship):
    """Over all 32 patterns exactly one diverges: a1&a2&a3&a4&a5.

    MSW has two inclusion-maximal rules there, r3 (award) and r5 (deny), which
    disagree, so it abstains. RC has no tie to lose and entails the award. That
    pattern is the witness for the r3/r5 strict-closure violation, so it's the
    theorem's hypothesis failing, not the theorem.
    """
    agreement = report.over_patterns(scholarship, base_rank(scholarship.to_kb()))
    assert agreement.total == 32
    assert len(agreement.divergences) == 1

    (divergence,) = agreement.divergences
    assert divergence.pattern == pattern(1, 1, 1, 1, 1)
    assert (divergence.msw_label, divergence.rc_label) == (None, 1)
    assert {
        r.id for r in msw.maximal(msw.applicable(scholarship, divergence.pattern))
    } == {
        "r3",
        "r5",
    }


def test_alignment_holds_over_the_whole_feature_space_when_hypotheses_hold():
    """The positive control: a ruleset that passes all three checks aligns exactly."""
    closed = parse_rules(FIXTURES / "scholarship_closed.rules.txt")
    assert validate(closed) == []

    agreement = report.over_patterns(closed, base_rank(closed.to_kb()))
    assert agreement.total == 2 ** len(closed.atoms)
    assert agreement.divergences == ()
    assert agreement.rate == 1.0


def test_both_labels_and_abstention_actually_occur(scholarship):
    """Guards against a vacuous pass: if MSW returned None everywhere, agreement
    would be trivially high. All three outcomes must be exercised."""
    rows = report.over_patterns(scholarship, base_rank(scholarship.to_kb())).rows
    assert {row.msw_label for row in rows} == {0, 1, None}
