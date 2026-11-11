"""Query answering copied straight from the published pseudocode.

Only used for measurement; nothing in the normal path imports it.
`rational_closure.base_rank_of` binary-searches `RankedKB.tail_clauses`. This one
scans the ranks in order and rebuilds the clause set at every rank, like the
published pseudocode, so the baseline table can show what the paper's version costs
against what we ship. What it isolates is binary versus linear search. `query` below
still makes exactly three `base_rank_of` calls and reads the case (a)/(b) split off
them, which is what `rational_closure.query` boils down to once its cache is counted,
so memoisation isn't being measured here.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base_rank import INFINITY, Rank, RankedKB
from .model import Body, materialise
from .sat import satisfiable


def base_rank_of(ranked: RankedKB, formula: Body) -> Rank:
    """Ascending scan, rebuilding the clauses at each rank, as in the published
    pseudocode.

    It skips `RankedKB.tail_clauses` on purpose: that cache is one of the shipped
    optimisations and this is meant to cost the plain pseudocode. Rebuilding changes
    the wall-clock but not the SAT-call count, which is still one `satisfiable` call
    per rank visited.
    """
    for rank in ranked.order:
        clauses = materialise([c for c, r in ranked.ranks.items() if r >= rank])
        if satisfiable(clauses, formula):
            return rank
    return INFINITY


def _classical_clauses(ranked: RankedKB):
    return materialise([c for c, r in ranked.ranks.items() if r == INFINITY])


@dataclass(frozen=True)
class Verdict:
    br_pattern: Rank
    possible: bool
    supports_positive: bool
    supports_negative: bool

    @property
    def label(self) -> int | None:
        if not self.possible:
            return None
        if self.supports_positive and not self.supports_negative:
            return 1
        if self.supports_negative and not self.supports_positive:
            return 0
        return None


def query(ranked: RankedKB, pattern: Body, label_atom) -> Verdict:
    positive, negative = (label_atom, True), (label_atom, False)
    br_pattern = base_rank_of(ranked, pattern)
    br_positive = base_rank_of(ranked, pattern | {positive})
    br_negative = base_rank_of(ranked, pattern | {negative})

    if br_pattern != INFINITY:
        return Verdict(
            br_pattern=br_pattern,
            possible=True,
            supports_positive=br_pattern < br_negative,
            supports_negative=br_pattern < br_positive,
        )

    # br_pattern is INFINITY: either exceptional everywhere (impossible) or only
    # surviving at the classical level. That's case (a) vs (b), see rational_closure.py.
    e_inf = _classical_clauses(ranked)
    if not satisfiable(e_inf, pattern):
        return Verdict(
            br_pattern, possible=False, supports_positive=True, supports_negative=True
        )
    return Verdict(
        br_pattern=br_pattern,
        possible=True,
        supports_positive=not satisfiable(e_inf, pattern | {negative}),
        supports_negative=not satisfiable(e_inf, pattern | {positive}),
    )
