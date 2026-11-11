"""BaseRank against the boat / leaky / FlyingDutchman trace.

Reference: Kaliski's thesis (Algorithm 1, and the worked example of this same KB in
5.3), which goes:

    1. "K |= -leaky and K |= -FlyingDutchman and so E1 = {leaky -> boat,
       leaky -> -floats, FlyingDutchman -> boat, FlyingDutchman -> leaky}."
    2. "E1 has no exceptional antecedents, and so E2 = {}."
    3. "E2 has no exceptional antecedents and so E3 = {}. Since E2 = E3, the loop
       is terminated."

so R0 = {boat -> floats}, R1 = the other four and R_infinity = {}, which is the
expected table below. The two FlyingDutchman conditionals end up at rank 1, not
infinity. E_{i+1} comes from the materialisation of E_i, the CURRENT subset. Once
boat|~floats is gone at rank 0 nothing forces `floats` any more and FlyingDutchman
becomes satisfiable. Checking exceptionality against the whole KB instead would give
the wrong table, which is the mistake
test_exceptionality_is_judged_against_remaining_conditionals_only guards against.
Infinite ranks come from a non-empty fixpoint E_i = E_{i+1} (see
test_infinite_rank_for_classically_inconsistent_antecedent), not from running out of
conditionals.

The reference query for this KB is checked in test_rational_closure.py.
"""

import math

from eccrs_workbench.base_rank import base_rank, is_exceptional
from eccrs_workbench.model import Conditional, ConditionalKB, atom, materialise


def ranks_by_id(ranked):
    return {c.source_rule_id: r for c, r in ranked.ranks.items()}


def test_boat_rank_table(boat_kb):
    assert ranks_by_id(base_rank(boat_kb)) == {
        "boat|~floats": 0,
        "leaky|~boat": 1,
        "leaky|~-floats": 1,
        "FD|~boat": 1,
        "FD|~leaky": 1,
    }


def test_boat_order_is_ascending(boat_kb):
    assert base_rank(boat_kb).order == (0, 1)


def test_exceptionality_of_each_antecedent_at_the_first_iteration(boat_kb):
    """Iteration 1: leaky and FlyingDutchman are exceptional, boat is not. This
    matches Kaliski's trace."""
    clauses = materialise(boat_kb.conditionals)
    assert {
        c.source_rule_id: is_exceptional(clauses, c.body) for c in boat_kb.conditionals
    } == {
        "boat|~floats": False,
        "leaky|~boat": True,
        "leaky|~-floats": True,
        "FD|~boat": True,
        "FD|~leaky": True,
    }


def test_exceptionality_is_judged_against_remaining_conditionals_only(boat_kb):
    """The key BaseRank invariant, as a test.

    Dropping the rank-0 conditional makes FlyingDutchman satisfiable; keeping it
    would not. This single distinction is what produces the whole rank table.
    """
    remaining = [c for c in boat_kb.conditionals if c.source_rule_id != "boat|~floats"]
    dutchman = frozenset({(atom(4), True)})
    assert is_exceptional(materialise(boat_kb.conditionals), dutchman)
    assert not is_exceptional(materialise(remaining), dutchman)


def test_tail_clauses_shrink_as_rank_rises(boat_kb):
    ranked = base_rank(boat_kb)
    assert [len(ranked.tail_clauses[r]) for r in ranked.order] == [5, 4]


def test_infinite_rank_for_classically_inconsistent_antecedent():
    """p |~ q and p |~ -q leave p exceptional at every level, so both are classical."""
    p, q = atom(1), atom(2)
    kb = ConditionalKB(
        (
            Conditional(frozenset({(p, True)}), (q, True), "p|~q"),
            Conditional(frozenset({(p, True)}), (q, False), "p|~-q"),
        ),
        label_atom=q,
    )
    ranked = base_rank(kb)
    assert ranks_by_id(ranked) == {"p|~q": math.inf, "p|~-q": math.inf}
    assert ranked.order == (math.inf,)


def test_scholarship_rank_table(scholarship):
    """The translated scholarship KB: defaults at 0, exceptions at 1, the
    exception-to-exception at 2 (worked out by hand from the five rules)."""
    ranked = base_rank(scholarship.to_kb())
    assert ranks_by_id(ranked) == {"r1": 0, "r4": 0, "r2": 1, "r5": 1, "r3": 2}
