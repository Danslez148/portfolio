"""naive.py only exists so its SAT calls can be counted, so before those counts go in
a table it has to agree with what it stands in for, like every other implementation
here.
"""

import random

from eccrs_workbench import naive
from eccrs_workbench.base_rank import INFINITY, base_rank
from eccrs_workbench.model import Rule, RuleSet, atom
from eccrs_workbench.rational_closure import query as production_query


def _agrees(ruleset, ranked, pattern):
    prod = production_query(ranked, pattern)
    naive_verdict = naive.query(ranked, pattern, ranked.kb.label_atom)
    return (
        prod.possible == naive_verdict.possible
        and prod.supports_positive == naive_verdict.supports_positive
        and prod.supports_negative == naive_verdict.supports_negative
        and prod.label == naive_verdict.label
    )


def test_agrees_with_production_on_cancer(cancer_rules):
    ranked = base_rank(cancer_rules.to_kb())
    for pattern in _patterns(cancer_rules.atoms):
        assert _agrees(cancer_rules, ranked, pattern), pattern


def test_agrees_with_production_on_scholarship(scholarship):
    ranked = base_rank(scholarship.to_kb())
    for pattern in _patterns(scholarship.atoms):
        assert _agrees(scholarship, ranked, pattern), pattern


def _patterns(atoms):
    import itertools

    atoms = sorted(atoms)
    for bits in itertools.product([False, True], repeat=len(atoms)):
        yield frozenset(zip(atoms, bits, strict=True))


P, B, M = atom(1), atom(2), atom(3)


def _ranked(*rules):
    ruleset = RuleSet(
        tuple(Rule(rid, frozenset(body), label) for rid, body, label in rules)
    )
    return ruleset, base_rank(ruleset.to_kb(M))


def test_agrees_on_the_impossible_pattern():
    """Case (a): tests/test_rational_closure.py's CONFLICTING KB."""
    ruleset, ranked = _ranked(
        ("r1", [(P, True)], 1), ("r2", [(P, True)], 0), ("r3", [(B, True)], 1)
    )
    pattern = frozenset({(P, True), (B, True)})
    verdict = naive.query(ranked, pattern, M)
    assert verdict.br_pattern == INFINITY
    assert not verdict.possible
    assert verdict.label is None
    assert _agrees(ruleset, ranked, pattern)


def test_agrees_on_a_possible_pattern_with_infinite_base_rank():
    """OPPOSING from test_rational_closure.py: no infinite-rank conditional at all,
    yet the pattern p & b still reaches base rank inf."""
    ruleset, ranked = _ranked(("r1", [(P, True)], 1), ("r2", [(B, True)], 0))
    pattern = frozenset({(P, True), (B, True)})
    verdict = naive.query(ranked, pattern, M)
    assert verdict.br_pattern == INFINITY
    assert verdict.possible
    assert verdict.label is None
    assert _agrees(ruleset, ranked, pattern)


def test_base_rank_of_agrees_with_the_binary_search(boat_kb, scholarship):
    """Same property that test_rational_closure.py's
    test_binary_search_agrees_with_the_published_linear_scan pins the shipped binary
    search against, run against this module instead."""
    from eccrs_workbench.rational_closure import base_rank_of as production_base_rank_of

    rng = random.Random(1729)
    for kb in (boat_kb, scholarship.to_kb()):
        ranked = base_rank(kb)
        atoms = sorted(
            {atom for c in ranked.ranks for atom, _ in c.body} | {kb.label_atom}
        )
        for _ in range(200):
            formula = frozenset(
                (a, rng.choice([True, False]))
                for a in rng.sample(atoms, rng.randint(1, len(atoms)))
            )
            assert naive.base_rank_of(ranked, formula) == production_base_rank_of(
                ranked, formula
            )
