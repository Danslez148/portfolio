"""BaseRank: rank each conditional by how exceptional its antecedent is.

Low ranks are general defaults, high ranks are more specific exceptions, and infinity
means the conditional acts like a classical fact (Kaliski 2020, Algorithm 1).
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .model import Body, Clause, Conditional, ConditionalKB, materialise
from .sat import satisfiable

Rank = int | float
INFINITY = math.inf


@dataclass(frozen=True, eq=False)
class RankedKB:
    kb: ConditionalKB
    ranks: Mapping[Conditional, Rank]
    order: tuple[Rank, ...]  # ranks present, ascending
    tail_clauses: Mapping[Rank, tuple[Clause, ...]]  # clauses of all conditionals >= r

    def at_rank(self, rank: Rank) -> list[Conditional]:
        return [c for c, r in self.ranks.items() if r == rank]


def is_exceptional(clauses: Iterable[Clause], body: Body) -> bool:
    """True if clauses + body is unsatisfiable. A plain function because BaseRank and
    query answering both use it."""
    return not satisfiable(clauses, body)


def base_rank(kb: ConditionalKB) -> RankedKB:
    """Compute the BaseRank of a conditional knowledge base."""
    remaining = list(kb.conditionals)
    ranks: dict[Conditional, Rank] = {}
    rank = 0

    while remaining:
        # Judge exceptionality against the conditionals still remaining, NOT the full
        # original KB. Using the whole KB gives a rank table that looks fine and is wrong.
        clauses = materialise(remaining)
        exceptional: list[Conditional] = []
        ordinary: list[Conditional] = []
        for conditional in remaining:  # one pass
            target = (
                exceptional if is_exceptional(clauses, conditional.body) else ordinary
            )
            target.append(conditional)

        if not ordinary:
            # Everything left is exceptional, so it's all classical.
            ranks.update({c: INFINITY for c in remaining})
            break

        ranks.update({c: rank for c in ordinary})
        remaining = exceptional
        rank += 1

    order = tuple(sorted(set(ranks.values())))
    return RankedKB(kb, ranks, order, _tail_clauses(ranks, order))


def _tail_clauses(
    ranks: Mapping[Conditional, Rank], order: tuple[Rank, ...]
) -> dict[Rank, tuple[Clause, ...]]:
    tails: dict[Rank, tuple[Clause, ...]] = {}
    accumulated: list[Clause] = []
    for rank in reversed(order):
        accumulated = (
            materialise([c for c, r in ranks.items() if r == rank]) + accumulated
        )
        tails[rank] = tuple(accumulated)
    return tails
