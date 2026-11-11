"""Rational Closure query answering.

The reference query: on the boat KB, FlyingDutchman |~ -floats must be entailed.
"""

import math
import random

from eccrs_workbench.base_rank import INFINITY, base_rank, is_exceptional
from eccrs_workbench.explanation import rc_trace
from eccrs_workbench.model import Rule, RuleSet, atom
from eccrs_workbench.rational_closure import (
    base_rank_of,
    classify,
    entails,
    is_possible,
    query,
)
from tests.examples import (
    BOAT,
    DUTCHMAN,
    EXPECTED_MSW,
    FLOATS,
    INSTANCE_A,
    INSTANCE_B,
    INSTANCE_C,
    INSTANCE_D,
    LEAKY,
)


def test_flying_dutchman_typically_does_not_float(boat_kb):
    ranked = base_rank(boat_kb)
    assert entails(ranked, frozenset({(DUTCHMAN, True)}), (FLOATS, False))
    assert not entails(ranked, frozenset({(DUTCHMAN, True)}), (FLOATS, True))


def test_the_rank_comparison_behind_that_answer(boat_kb):
    ranked = base_rank(boat_kb)
    dutchman = frozenset({(DUTCHMAN, True)})
    assert base_rank_of(ranked, dutchman) == 1
    assert base_rank_of(ranked, dutchman | {(FLOATS, True)}) == math.inf


def test_leaky_boats_do_not_float(boat_kb):
    ranked = base_rank(boat_kb)
    assert entails(ranked, frozenset({(LEAKY, True)}), (FLOATS, False))


def test_boats_typically_float(boat_kb):
    ranked = base_rank(boat_kb)
    assert entails(ranked, frozenset({(BOAT, True)}), (FLOATS, True))


def _base_rank_of_linear(ranked, formula):
    """Literal transcription of the published ascending scan."""
    for rank in ranked.order:
        if not is_exceptional(ranked.tail_clauses[rank], formula):
            return rank
    return INFINITY


def test_binary_search_agrees_with_the_published_linear_scan(boat_kb, scholarship):
    rng = random.Random(4242)
    for kb in (boat_kb, scholarship.to_kb()):
        ranked = base_rank(kb)
        atoms = sorted(
            {atom for c in ranked.ranks for atom, _ in c.body} | {kb.label_atom}
        )
        for _ in range(300):
            formula = frozenset(
                (a, rng.choice([True, False]))
                for a in rng.sample(atoms, rng.randint(1, len(atoms)))
            )
            assert base_rank_of(ranked, formula) == _base_rank_of_linear(ranked, formula)


def test_scholarship_instances(scholarship):
    ranked = base_rank(scholarship.to_kb())
    assert classify(ranked, INSTANCE_A) == 1
    assert classify(ranked, INSTANCE_B) == 0
    assert classify(ranked, INSTANCE_C) == 1
    assert classify(ranked, INSTANCE_D) is None


def test_instance_a_is_decided_at_the_exception_to_exception_rank(scholarship):
    """Instance A: a1 & a4 & a5 supports the award at the decisive rank."""
    verdict = query(base_rank(scholarship.to_kb()), INSTANCE_A)
    assert (verdict.br_pattern, verdict.br_with_negative) == (2, math.inf)
    assert verdict.supports_positive and not verdict.supports_negative


def test_never_both_queries_at_once(scholarship):
    ranked = base_rank(scholarship.to_kb())
    for name, (pattern, _) in EXPECTED_MSW.items():
        verdict = query(ranked, pattern)
        assert not (verdict.supports_positive and verdict.supports_negative), name


# The classical level is not the same thing as impossibility
#
# base_rank_of reports inf for two different situations, and only one of them makes
# a conditional vacuously true:
#
#   (a) the formula is unsatisfiable even with the classical clauses -- impossible;
#   (b) the formula is exceptional at every finite rank but consistent with them --
#       possible, and answered at the classical level like any other formula.
#
# Reading inf as (a) makes RC entail everything from a perfectly ordinary antecedent.
# The two knowledge bases below are the smallest cases of each.

P, B, M = atom(1), atom(2), atom(3)


def _ranked(*rules):
    ruleset = RuleSet(
        tuple(Rule(rid, frozenset(body), label) for rid, body, label in rules)
    )
    return ruleset, base_rank(ruleset.to_kb(M))


# K = {p |~ m, p |~ -m, b |~ m}. The two p conditionals contradict each other, so
# neither can ever be non-exceptional and both sit at rank inf; E_inf is equivalent
# to ~p. b |~ m is ordinary and sits at rank 0.
CONFLICTING = (
    ("r1", [(P, True)], 1),
    ("r2", [(P, True)], 0),
    ("r3", [(B, True)], 1),
)


def test_the_conflicting_pair_is_classical_and_the_ordinary_rule_is_not():
    _, ranked = _ranked(*CONFLICTING)
    by_id = {c.source_rule_id: r for c, r in ranked.ranks.items()}
    assert by_id == {"r1": INFINITY, "r2": INFINITY, "r3": 0}


def test_an_antecedent_that_survives_only_classically_is_not_a_free_pass():
    """b & ~m has base rank inf, but it is satisfiable with E_inf, so RC must answer
    its queries at the classical level rather than entailing everything."""
    _, ranked = _ranked(*CONFLICTING)
    alpha = frozenset({(B, True), (M, False)})

    assert base_rank_of(ranked, alpha) == INFINITY
    assert is_possible(ranked, alpha)

    # E_inf is ~p, which says nothing about b or m, so none of these follow.
    assert not entails(ranked, alpha, (B, False))
    assert not entails(ranked, alpha, (P, True))
    assert not entails(ranked, alpha, (M, True))
    # What E_inf does say, it still entails.
    assert entails(ranked, alpha, (P, False))


def test_a_genuinely_impossible_antecedent_still_entails_everything():
    """Case (a): p is refuted by E_inf itself, so p |~ anything holds vacuously."""
    _, ranked = _ranked(*CONFLICTING)
    alpha = frozenset({(P, True)})

    assert base_rank_of(ranked, alpha) == INFINITY
    assert not is_possible(ranked, alpha)
    assert entails(ranked, alpha, (M, True))
    assert entails(ranked, alpha, (M, False))
    assert entails(ranked, alpha, (B, True))


def test_only_the_impossible_pattern_is_reported_vacuous():
    """Verdict.vacuous read br_pattern == inf, so it claimed case (b) as vacuous too."""
    _, ranked = _ranked(*CONFLICTING)

    impossible = query(ranked, frozenset({(P, True), (B, True)}))
    assert impossible.br_pattern == INFINITY
    assert impossible.vacuous
    assert impossible.supports_positive and impossible.supports_negative
    assert impossible.label is None


# K = {p |~ m, b |~ -m}. Both are ordinary, so nothing has infinite rank at all and
# E_inf is empty -- yet the pattern p & b is exceptional at rank 0 (it fires both
# rules, forcing m and ~m) and so still gets base rank inf. This is the case that
# needs no infinite-rank conditional to reach, which is what makes it easy to miss.
OPPOSING = (
    ("r1", [(P, True)], 1),
    ("r2", [(B, True)], 0),
)


def test_a_possible_pattern_with_infinite_base_rank_is_not_vacuous():
    ruleset, ranked = _ranked(*OPPOSING)
    assert ranked.order == (0,)  # nothing classical: E_inf is empty

    verdict = query(ranked, frozenset({(P, True), (B, True)}))
    assert verdict.br_pattern == INFINITY
    assert verdict.possible and not verdict.vacuous
    # Answered at the classical level, where the empty E_inf leaves m free.
    assert not verdict.supports_positive and not verdict.supports_negative
    assert verdict.label is None

    trace = "\n".join(rc_trace(ruleset, ranked, verdict.pattern))
    assert "vacuously" not in trace
    assert "abstain" in trace


def test_the_impossible_pattern_trace_says_why():
    ruleset, ranked = _ranked(*CONFLICTING)
    pattern = frozenset({(P, True), (B, True)})
    trace = "\n".join(rc_trace(ruleset, ranked, pattern))
    assert "inconsistent with the classical part" in trace
    assert "vacuously" in trace
