"""Differential test: the shipped RC against a from-first-principles oracle.

The shipped code is optimised (cumulative per-rank clause sets, binary search over
ranks, memoisation, a hand-written DPLL underneath). Any of those could be subtly
wrong in a way the worked examples wouldn't catch, since they only cover two KBs.

The oracle below is deliberately naive and slow: exceptionality by truth tables,
ranks by the literal E_i sequence, base rank by an ascending scan. It shares no code
with the implementation except the data model, so agreement over random KBs is real
evidence.
"""

import itertools
import random

import pytest

from eccrs_workbench.base_rank import INFINITY, base_rank
from eccrs_workbench.model import Conditional, ConditionalKB, atom, materialise, negate
from eccrs_workbench.rational_closure import base_rank_of, entails

ATOMS = [atom(1), atom(2), atom(3), atom(4)]


def _satisfiable(clauses, assumptions, atoms):
    for bits in itertools.product([False, True], repeat=len(atoms)):
        world = dict(zip(atoms, bits, strict=True))
        if all(world[a] == p for a, p in assumptions) and all(
            any(world[a] == p for a, p in clause) for clause in clauses
        ):
            return True
    return False


def _oracle_ranks(conditionals, atoms):
    remaining, ranks, rank = list(conditionals), {}, 0
    while remaining:
        clauses = materialise(remaining)
        exceptional = [c for c in remaining if not _satisfiable(clauses, c.body, atoms)]
        ordinary = [c for c in remaining if c not in exceptional]
        if not ordinary:
            ranks.update({c: INFINITY for c in remaining})
            break
        ranks.update({c: rank for c in ordinary})
        remaining, rank = exceptional, rank + 1
    return ranks


def _oracle_base_rank_of(ranks, formula, atoms):
    for rank in sorted(set(ranks.values())):
        clauses = materialise([c for c, r in ranks.items() if r >= rank])
        if _satisfiable(clauses, formula, atoms):
            return rank
    return INFINITY


def _oracle_levels(ranks):
    """The sequence E_0 > E_1 > ... > E_inf, as clause lists, ascending.

    E_inf is always the last level, and just empty if no conditional has infinite
    rank. Leaving it out is the mistake this file exists to catch, so it's written
    out and not derived from the ranks present.
    """
    present = sorted(set(ranks.values()))
    for rank in present:
        yield materialise([c for c, r in ranks.items() if r >= rank])
    if INFINITY not in present:
        yield []


def _oracle_entails(ranks, alpha, beta, atoms):
    """The published procedure: strip levels while alpha is exceptional, then ask.

    This doesn't go through _oracle_base_rank_of. That returns a rank value, and
    INFINITY means both the classical level and "satisfiable nowhere", so a caller
    can't tell them apart. Scanning here keeps them separate: the check happens at the
    first level where alpha is satisfiable, and the classical level is an ordinary
    member of the scan. Only running off the end (alpha unsatisfiable even with the
    classical clauses) makes the conditional vacuously true.
    """
    for clauses in _oracle_levels(ranks):
        if _satisfiable(clauses, alpha, atoms):
            return not _satisfiable(clauses, alpha | {negate(beta)}, atoms)
    return True


def _random_kb(rng):
    conditionals = []
    for i in range(rng.randint(1, 5)):
        size = rng.randint(1, 2)
        body = frozenset((a, rng.choice([True, False])) for a in rng.sample(ATOMS, size))
        head_atom = rng.choice(ATOMS)
        if any(atom == head_atom for atom, _ in body):
            continue  # a conditional whose head repeats a body atom is degenerate
        conditionals.append(
            Conditional(body, (head_atom, rng.choice([True, False])), f"c{i}")
        )
    if not conditionals:
        return None
    return ConditionalKB(tuple(conditionals), label_atom=ATOMS[-1])


@pytest.mark.parametrize("seed", range(30))
def test_ranks_and_entailment_match_the_oracle(seed):
    rng = random.Random(seed)
    checked_kbs = 0
    for _ in range(12):
        kb = _random_kb(rng)
        if kb is None:
            continue
        checked_kbs += 1

        ranked = base_rank(kb)
        oracle = _oracle_ranks(kb.conditionals, ATOMS)
        assert ranked.ranks == oracle, f"rank table differs for {kb.conditionals}"

        for _ in range(10):
            alpha = frozenset(
                (a, rng.choice([True, False]))
                for a in rng.sample(ATOMS, rng.randint(1, 3))
            )
            beta_atom = rng.choice(ATOMS)
            beta = (beta_atom, rng.choice([True, False]))

            assert base_rank_of(ranked, alpha) == _oracle_base_rank_of(
                oracle, alpha, ATOMS
            ), f"br differs: kb={kb.conditionals} alpha={alpha}"
            assert entails(ranked, alpha, beta) == _oracle_entails(
                oracle, alpha, beta, ATOMS
            ), f"entailment differs: kb={kb.conditionals} alpha={alpha} beta={beta}"
    assert checked_kbs > 0
