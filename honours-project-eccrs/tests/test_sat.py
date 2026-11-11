"""Tests for the from-scratch DPLL solver.

It's our own code, so it needs its own evidence: known-answer cases plus a property
test against brute-force truth tables.
"""

import itertools
import random

from eccrs_workbench.model import negate
from eccrs_workbench.sat import satisfiable

A, B, C = (1, True), (2, True), (3, True)


def test_no_clauses_is_satisfiable():
    assert satisfiable([])


def test_empty_clause_is_unsatisfiable():
    assert not satisfiable([frozenset()])


def test_trivially_satisfiable():
    assert satisfiable([frozenset({A, B}), frozenset({negate(A), C})])


def test_contradictory_units_are_unsatisfiable():
    assert not satisfiable([frozenset({A}), frozenset({negate(A)})])


def test_assumptions_are_asserted_as_units():
    implication = [frozenset({negate(A), B})]  # A -> B
    assert satisfiable(implication, frozenset({A}))
    assert satisfiable(implication, frozenset({negate(A), negate(B)}))
    assert not satisfiable(implication, frozenset({A, negate(B)}))


def test_requires_backtracking():
    # Pigeonhole-ish: forces the search past unit propagation and pure literals.
    clauses = [
        frozenset({A, B}),
        frozenset({A, negate(B)}),
        frozenset({negate(A), B}),
        frozenset({negate(A), negate(B)}),
    ]
    assert not satisfiable(clauses)


def _brute_force(clauses, atoms):
    for bits in itertools.product([False, True], repeat=len(atoms)):
        assignment = dict(zip(atoms, bits, strict=True))
        if all(any(assignment[a] == p for a, p in clause) for clause in clauses):
            return True
    return False


def test_agrees_with_truth_table_enumeration():
    rng = random.Random(20260813)
    atoms = [1, 2, 3, 4, 5, 6]
    for _ in range(400):
        clauses = [
            frozenset(
                (a, rng.choice([True, False]))
                for a in rng.sample(atoms, rng.randint(1, 3))
            )
            for _ in range(rng.randint(1, 12))
        ]
        assert satisfiable(clauses) == _brute_force(clauses, atoms), clauses


def test_agrees_with_truth_table_enumeration_under_assumptions():
    rng = random.Random(66)
    atoms = [1, 2, 3, 4, 5]
    for _ in range(200):
        clauses = [
            frozenset(
                (a, rng.choice([True, False]))
                for a in rng.sample(atoms, rng.randint(1, 3))
            )
            for _ in range(rng.randint(1, 8))
        ]
        assumptions = frozenset(
            (a, rng.choice([True, False])) for a in rng.sample(atoms, rng.randint(0, 2))
        )
        # An assumption set that contradicts itself is UNSAT by construction.
        if any(negate(lit) in assumptions for lit in assumptions):
            continue
        expected = _brute_force(
            clauses + [frozenset({lit}) for lit in assumptions], atoms
        )
        assert satisfiable(clauses, assumptions) == expected, (clauses, assumptions)
