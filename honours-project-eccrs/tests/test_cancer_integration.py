"""End to end on the real inputs: datasets/cancer/rules.txt over the 699 Breast Cancer
Wisconsin instances in datasets/cancer/data-cancer.lp.

There are no hand-computed answers here, so we check that the two operators agree,
plus the accuracy figure and the structural invariants.
"""

from eccrs_workbench import explanation, report
from eccrs_workbench.base_rank import base_rank
from eccrs_workbench.model import atom
from eccrs_workbench.parser import infer_class_atom, safe_label_atom, to_body
from eccrs_workbench.rational_closure import query


def ranked_cancer_kb(cancer_rules, cancer_instances):
    return base_rank(cancer_rules.to_kb(safe_label_atom(cancer_rules, cancer_instances)))


def test_dataset_parses_as_expected(cancer_instances):
    assert len(cancer_instances) == 699
    assert infer_class_atom(cancer_instances) == atom(10)
    # a(6), Bare Nuclei, dropped upstream for missing values, is absent entirely.
    assert {a for values in cancer_instances.values() for a in values} == {
        atom(i) for i in (1, 2, 3, 4, 5, 7, 8, 9, 10)
    }


def test_label_atom_does_not_collide_with_a_dataset_feature(
    cancer_rules, cancer_instances
):
    """Rule atoms stop at a(8), so a naive max+1 picks a(9) -- a real feature."""
    assert safe_label_atom(cancer_rules, cancer_instances) == atom(11)
    assert cancer_rules.to_kb().label_atom == atom(9)  # the trap, documented


def test_msw_and_rc_agree_on_every_instance(cancer_rules, cancer_instances):
    agreement = report.over_instances(
        cancer_rules,
        ranked_cancer_kb(cancer_rules, cancer_instances),
        cancer_instances,
        infer_class_atom(cancer_instances),
    )
    assert agreement.total == 699
    assert agreement.divergences == ()
    assert agreement.rate == 1.0


def test_msw_accuracy_against_the_ground_truth_class(cancer_rules, cancer_instances):
    agreement = report.over_instances(
        cancer_rules,
        ranked_cancer_kb(cancer_rules, cancer_instances),
        cancer_instances,
        infer_class_atom(cancer_instances),
    )
    assert agreement.abstentions == 0
    assert sum(row.msw_label == row.truth for row in agreement.rows) == 664
    assert agreement.accuracy == 664 / 699


def test_msw_and_rc_agree_on_every_feature_pattern(cancer_rules, cancer_instances):
    """The dataset exercises only 10 distinct applicable-rule-sets, so the observed
    instances alone are weak evidence. All 2^6 patterns close that gap."""
    agreement = report.over_patterns(
        cancer_rules, ranked_cancer_kb(cancer_rules, cancer_instances)
    )
    assert agreement.total == 64
    assert agreement.divergences == ()


def test_the_two_class_queries_are_never_both_entailed(cancer_rules, cancer_instances):
    ranked = ranked_cancer_kb(cancer_rules, cancer_instances)
    for values in cancer_instances.values():
        verdict = query(ranked, to_body(values, cancer_rules.atoms))
        assert not verdict.vacuous
        assert not (verdict.supports_positive and verdict.supports_negative)


def test_a_trace_names_the_same_rule_on_both_sides(cancer_rules, cancer_instances):
    """Instance 2 is decided by rule 11 (a2=1 -> class 0), the most general rule, with
    nothing more specific applying. Both sides of the trace must say so."""
    ranked = ranked_cancer_kb(cancer_rules, cancer_instances)
    trace = explanation.explain(
        cancer_rules, ranked, to_body(cancer_instances[2], cancer_rules.atoms), key="2"
    )
    assert "MSW: label = 0" in trace
    assert "RC entails class 0" in trace
    assert "11" in trace.split("from ECCRS rules:")[1]
    assert "11: a(2) =>" in trace  # the ECCRS side names the same rule
    assert "=> AGREE" in trace
