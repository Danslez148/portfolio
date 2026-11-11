"""Most Specific Wins.

This is the ground truth RC gets checked against, so it's kept small and close to the
paper's definition.
"""

from __future__ import annotations

from .model import Body, Rule, RuleSet


def applicable(ruleset: RuleSet, pattern: Body) -> list[Rule]:
    return [rule for rule in ruleset.rules if rule.body <= pattern]


def maximal(rules: list[Rule]) -> list[Rule]:
    """M(F): the inclusion-maximal rules, i.e. not strictly overridden.

    The subset test has to be strict (`<`). With `<=` every rule overrides itself, M(F)
    is always empty and the classifier quietly abstains on everything.
    """
    return [rule for rule in rules if not any(rule.body < other.body for other in rules)]


def predict(ruleset: RuleSet, pattern: Body) -> int | None:
    """The label M(F) agrees on, or None (abstain) if M(F) is empty or split."""
    labels = {rule.label for rule in maximal(applicable(ruleset, pattern))}
    return labels.pop() if len(labels) == 1 else None
