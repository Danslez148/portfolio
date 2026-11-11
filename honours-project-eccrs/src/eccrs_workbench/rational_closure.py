"""Rational Closure query answering on top of BaseRank.

K |=_RC a |~ b  iff  a is impossible, or a & -b is unsatisfiable at br(a).

It's not written as "br(a) < br(a & -b), or br(a) = inf" because INFINITY does two
jobs. It's the classical level, and it's also what base_rank_of returns for a formula
that's exceptional at every rank. Only the second case means "a is impossible". A
formula that's exceptional at every finite rank but consistent with the classical
clauses gets answered at the classical level, so it's not a free pass. See is_possible.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from .base_rank import INFINITY, Rank, RankedKB, is_exceptional
from .model import Body, Clause, Literal, negate
from .sat import satisfiable


@cache
def base_rank_of(ranked: RankedKB, formula: Body) -> Rank:
    """The lowest rank at which `formula` is not exceptional.

    Binary search instead of the paper's ascending scan. That works because
    tail_clauses[r] shrinks as r goes up, and dropping clauses can't make a satisfiable
    set unsatisfiable, so the ranks are a run of "exceptional" then a run of "not" and
    we want the first of the second run. O(log k) SAT calls rather than O(k).
    (test_rational_closure.py checks it against a literal ascending scan.)
    """
    if not ranked.order:  # empty KB: only a self-contradictory formula is exceptional
        return 0 if satisfiable([], formula) else INFINITY

    low, high = 0, len(ranked.order) - 1
    answer: Rank = INFINITY
    while low <= high:
        middle = (low + high) // 2
        rank = ranked.order[middle]
        if is_exceptional(ranked.tail_clauses[rank], formula):
            low = middle + 1
        else:
            answer = rank
            high = middle - 1
    return answer


def classical_clauses(ranked: RankedKB) -> tuple[Clause, ...]:
    return ranked.tail_clauses.get(INFINITY, ())


def is_possible(ranked: RankedKB, formula: Body) -> bool:
    """Is `formula` satisfiable with the classical part of K?

    `base_rank_of(...) == INFINITY` can't answer this: it mixes up "exceptional
    everywhere, so impossible" with "only survives at the classical level". Anything
    that needs the first meaning goes through here.

    A finite base rank settles it with no SAT call, since tail_clauses[r] contains every
    classical clause, so satisfiable there means satisfiable with E_inf alone.
    """
    return base_rank_of(ranked, formula) != INFINITY or satisfiable(
        classical_clauses(ranked), formula
    )


def entails(ranked: RankedKB, alpha: Body, beta: Literal) -> bool:
    br_alpha = base_rank_of(ranked, alpha)
    if br_alpha == INFINITY:
        if not is_possible(ranked, alpha):
            # alpha contradicts the classical part of K, so it holds vacuously.
            return True
        # alpha only survives at the classical level, so ask there:
        # E_inf |= alpha -> beta.
        return not satisfiable(classical_clauses(ranked), alpha | {negate(beta)})
    # For finite br(alpha), "alpha & -beta unsatisfiable at br(alpha)" is the same as
    # br(alpha) < br(alpha & -beta).
    return br_alpha < base_rank_of(ranked, alpha | {negate(beta)})


@dataclass(frozen=True)
class Verdict:
    pattern: Body
    br_pattern: Rank
    br_with_positive: Rank  # br(F & m)
    br_with_negative: Rank  # br(F & -m)
    possible: bool  # F is satisfiable with the classical part of K
    supports_positive: bool  # K |=_RC F |~ m, i.e. class 1
    supports_negative: bool  # K |=_RC F |~ -m, i.e. class 0

    @property
    def vacuous(self) -> bool:
        """F contradicts the classical part of K, so RC entails both queries.

        Not a real prediction, so it's reported separately. This is narrower than
        br(F) = inf: a pattern that's exceptional at every finite rank but consistent
        with E_inf gets answered at the classical level and has a real verdict.
        """
        return not self.possible

    @property
    def label(self) -> int | None:
        """Class 1, class 0, or None to abstain."""
        if self.vacuous:
            return None
        if self.supports_positive:
            return 1
        if self.supports_negative:
            return 0
        return None


@cache
def query(ranked: RankedKB, pattern: Body) -> Verdict:
    label_atom = ranked.kb.label_atom
    positive, negative = (label_atom, True), (label_atom, False)
    return Verdict(
        pattern=pattern,
        br_pattern=base_rank_of(ranked, pattern),
        br_with_positive=base_rank_of(ranked, pattern | {positive}),
        br_with_negative=base_rank_of(ranked, pattern | {negative}),
        possible=is_possible(ranked, pattern),
        supports_positive=entails(ranked, pattern, positive),
        supports_negative=entails(ranked, pattern, negative),
    )


def classify(ranked: RankedKB, pattern: Body) -> int | None:
    return query(ranked, pattern).label
