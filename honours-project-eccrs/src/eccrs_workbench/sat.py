"""A from-scratch DPLL satisfiability check.

Every BaseRank step and RC query boils down to one question: are these clauses, plus
some asserted unit literals, satisfiable?

No SAT library, on purpose: writing it from scratch is a project requirement (albeit
self-imposed). The clauses all come from B -> l rule translations, so they're short
and close to Horn, and plain DPLL is fine at this size.

Atoms are found from the clauses themselves, so we never reason about dataset
attributes that no rule mentions.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from contextlib import contextmanager
from dataclasses import dataclass

from .model import Clause, Literal, negate


@dataclass
class CallCounter:
    calls: int = 0
    peak_clause_set_size: int = 0


_active: CallCounter | None = None


@contextmanager
def count_calls():
    """Count `satisfiable` calls made anywhere in this block.

    The counting is inside `satisfiable` itself instead of a wrapper around it.
    `base_rank.py` and `rational_closure.py` import the function by name, so swapping
    `sat.satisfiable` later wouldn't reach them. Checking a module-level counter does.

    Nested windows are independent: the inner one gets its own counter and the outer
    one carries on afterwards. The counter is dropped when the `with` ends, even on an
    exception, so nothing leaks between tests or runs.
    """
    global _active
    counter = CallCounter()
    previous = _active
    _active = counter
    try:
        yield counter
    finally:
        _active = previous


def satisfiable(clauses: Iterable[Clause], assumptions: Iterable[Literal] = ()) -> bool:
    working = [set(c) for c in clauses] + [{lit} for lit in assumptions]
    if _active is not None:  # does nothing unless a count_calls window is open
        _active.calls += 1
        if len(working) > _active.peak_clause_set_size:
            _active.peak_clause_set_size = len(working)
    return _dpll(working)


def _dpll(clauses: list[set[Literal]] | None) -> bool:
    if clauses is None:  # an earlier assignment emptied a clause
        return False

    # Unit propagation until nothing changes.
    while True:
        unit = next((c for c in clauses if len(c) == 1), None)
        if unit is None:
            break
        clauses = _assign(clauses, next(iter(unit)))
        if clauses is None:
            return False

    if not clauses:
        return True
    if any(not c for c in clauses):
        return False

    # Pure literal: an atom that only ever appears one way can just be set to satisfy it.
    literals = {lit for clause in clauses for lit in clause}
    pure = next((lit for lit in literals if negate(lit) not in literals), None)
    if pure is not None:
        return _dpll(_assign(clauses, pure))

    # Branch on the most common literal.
    branch = Counter(lit for clause in clauses for lit in clause).most_common(1)[0][0]
    return _dpll(_assign(clauses, branch)) or _dpll(_assign(clauses, negate(branch)))


def _assign(clauses: list[set[Literal]], literal: Literal) -> list[set[Literal]] | None:
    opposite = negate(literal)
    simplified: list[set[Literal]] = []
    for clause in clauses:
        if literal in clause:
            continue  # already satisfied
        if opposite in clause:
            clause = clause - {opposite}
            if not clause:
                return None  # conflict
        simplified.append(clause)
    return simplified
