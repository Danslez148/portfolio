"""Phase 1: check the three conditions the alignment theorem needs.

Strict global exception closure, sanity and no total override.
"Global" means the whole Boolean feature space, not just the
instances we've seen. That's strict closure rather than relaxed closure, and the
theorem needs the strict one.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

from .model import Rule, RuleSet, negate
from .sat import satisfiable


@dataclass(frozen=True)
class Violation:
    check: str
    detail: str


def _can_coapply(first: Rule, second: Rule) -> bool:
    """Could one instance satisfy both bodies?

    False if the bodies disagree on some atom, since then nothing triggers both and
    closure says nothing about the pair. Skip this test and you wrongly reject valid
    rulesets: in datasets/cancer/rules.txt rule 6 (a2=0 & a4=0 & a8=0 -> 1) and rule 10
    (a2=0 & a8=1 -> 0) are incomparable with opposite labels, but they disagree on a8 so
    they can never both apply.
    """
    return not any(negate(literal) in second.body for literal in first.body)


def check_sanity(ruleset: RuleSet) -> list[Violation]:
    return [
        Violation(
            "sanity", f"rules {a.id} and {b.id} share a body but disagree on the label"
        )
        for a, b in itertools.combinations(ruleset.rules, 2)
        if a.body == b.body and a.label != b.label
    ]


def check_strict_closure(ruleset: RuleSet) -> list[Violation]:
    return [
        Violation(
            "strict closure",
            f"rules {a.id} and {b.id} have opposite labels and can both apply, "
            "but neither body is strictly more specific than the other",
        )
        for a, b in itertools.combinations(ruleset.rules, 2)
        if a.label != b.label
        and _can_coapply(a, b)
        and not (a.body < b.body or b.body < a.body)
    ]


def check_no_total_override(ruleset: RuleSet) -> list[Violation]:
    """Every rule has to fire somewhere without being overridden.

    Overriding means reaching a different conclusion, so only a strictly more specific
    rule with the OPPOSITE label counts. A more specific rule with the same label
    reinforces it: it may push the rule out of M(F) but the conclusion stands.

    We ask the solver for an assignment that satisfies the rule's body and falsifies
    every opposite-label refinement: unit clauses for B, plus one clause of negated
    leftover literals for each rule C with B strictly inside C and the opposite label.

    Being overridden on every instance we've seen is not a violation. This is over the
    whole feature space, so it's a SAT question and not a count over the data.
    """
    violations = []
    for rule in ruleset.rules:
        blockers = [
            frozenset(negate(literal) for literal in other.body - rule.body)
            for other in ruleset.rules
            if rule.body < other.body and other.label != rule.label
        ]
        if not satisfiable(blockers, rule.body):
            violations.append(
                Violation("no total override", f"rule {rule.id} is overridden everywhere")
            )
    return violations


def validate(ruleset: RuleSet) -> list[Violation]:
    return (
        check_sanity(ruleset)
        + check_strict_closure(ruleset)
        + check_no_total_override(ruleset)
    )
