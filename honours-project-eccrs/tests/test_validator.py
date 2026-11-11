"""Phase 1 assumption validation.

Two findings are pinned here because the write-up depends on them and they'd be
easy to break:

  * cancer's rules.txt passes all three checks: sanity, strict global closure and no
    total override. Rules 7 and 9 are never inclusion-maximal (a refinement always
    applies), but that isn't the same as being overridden: a refinement with the
    same label doesn't override, so no-total-override still holds.
  * the five-rule scholarship ruleset does NOT satisfy strict global exception
    closure.
"""

from eccrs_workbench.model import Rule, RuleSet
from eccrs_workbench.validator import (
    check_no_total_override,
    check_sanity,
    check_strict_closure,
    validate,
)


def ruleset(*specs) -> RuleSet:
    rules = tuple(Rule(rid, frozenset(body), label) for rid, body, label in specs)
    atoms = {atom for r in rules for atom, _ in r.body}
    return RuleSet(rules, {a: f"a{a}" for a in sorted(atoms)})


def test_sanity_flags_identical_bodies_with_opposite_labels():
    clash = ruleset(("x", {(1, True)}, 1), ("y", {(1, True)}, 0))
    assert len(check_sanity(clash)) == 1
    assert check_sanity(ruleset(("x", {(1, True)}, 1), ("y", {(1, True)}, 1))) == []


def test_closure_flags_incomparable_opposite_label_rules():
    incomparable = ruleset(("x", {(1, True)}, 1), ("y", {(2, True)}, 0))
    assert len(check_strict_closure(incomparable)) == 1


def test_closure_accepts_a_default_exception_chain():
    chain = ruleset(
        ("x", {(1, True)}, 1),
        ("y", {(1, True), (2, True)}, 0),
        ("z", {(1, True), (2, True), (3, True)}, 1),
    )
    assert check_strict_closure(chain) == []


def test_closure_ignores_rules_that_can_never_co_apply(cancer_rules):
    """The regression that matters: rules 6 and 10 of rules.txt have opposite labels
    and incomparable bodies, but disagree on a8, so no instance triggers both. A
    pairwise check without the joint-satisfiability guard rejects a valid ruleset."""
    six, ten = [r for r in cancer_rules.rules if r.id in {"6", "10"}]
    pair = RuleSet((six, ten), cancer_rules.atom_names)
    assert not (six.body < ten.body or ten.body < six.body)
    assert six.label != ten.label
    assert check_strict_closure(pair) == []


def test_cancer_ruleset_satisfies_sanity_and_strict_closure(cancer_rules):
    assert check_sanity(cancer_rules) == []
    assert check_strict_closure(cancer_rules) == []


def test_cancer_ruleset_satisfies_no_total_override(cancer_rules):
    assert check_no_total_override(cancer_rules) == []


def test_a_same_label_refinement_does_not_override(cancer_rules):
    """The distinction the check turns on.

    Rule 7 (a1=1 & a2=1 & a5=0 -> 0) is refined by rule 3 (adds a7=1, label 0) and
    rule 5 (adds a7=0, label 1). Since a(7) is binary one of them always applies, so
    rule 7 is never inclusion-maximal -- but at a7=1 the refinement that applies is
    rule 3, which AGREES with it. Rule 7's conclusion still stands there, so it is
    subsumed, not overridden. Counting same-label refinements as overrides wrongly
    reports rules 7 and 9 as violations.
    """
    seven, three, five = (
        next(r for r in cancer_rules.rules if r.id == rid) for rid in ("7", "3", "5")
    )
    assert seven.body < three.body and seven.body < five.body
    assert three.label == seven.label  # agrees -> not an override
    assert five.label != seven.label  # disagrees -> a genuine override
    assert check_no_total_override(RuleSet((seven, three, five), {})) == []


def test_no_total_override_accepts_a_rule_with_room_to_fire():
    chain = ruleset(("x", {(1, True)}, 1), ("y", {(1, True), (2, True)}, 0))
    assert check_no_total_override(chain) == []  # x fires whenever a2 is false


def test_no_total_override_flags_a_rule_with_nowhere_left_to_fire():
    """The red half of the red-green pair: a2 is binary, so the two opposite-label
    refinements between them cover every instance where x applies."""
    smothered = ruleset(
        ("x", {(1, True)}, 1),
        ("y", {(1, True), (2, True)}, 0),
        ("z", {(1, True), (2, False)}, 0),
    )
    violations = check_no_total_override(smothered)
    assert [v.detail.split()[1] for v in violations] == ["x"]


def test_published_scholarship_ruleset_violates_strict_closure(scholarship):
    """A finding, not a bug in the fixture: the scholarship worked example
    pairs an a1-branch against an a2&a3-branch whose opposite-label rules are
    incomparable and can co-apply. The alignment theorem therefore does not cover it
    -- see test_scholarship_alignment.py, where exactly one pattern diverges."""
    checks = {v.check for v in validate(scholarship)}
    assert checks == {"strict closure"}
    offending = {
        tuple(sorted((v.detail.split()[1], v.detail.split()[3])))
        for v in check_strict_closure(scholarship)
    }
    assert offending == {("r1", "r5"), ("r2", "r4"), ("r3", "r5")}
