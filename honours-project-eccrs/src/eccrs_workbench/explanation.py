"""Two-sided explanation traces.

For one pattern we print the ECCRS default/exception chain and the RC entailment side
by side, so we can see they match.
"""

from __future__ import annotations

from . import msw
from .base_rank import INFINITY, RankedKB
from .model import Body, RuleSet, format_body, format_literal
from .rational_closure import query


def _rank(rank) -> str:
    return "inf" if rank == INFINITY else str(rank)


def eccrs_trace(ruleset: RuleSet, pattern: Body) -> list[str]:
    applicable = msw.applicable(ruleset, pattern)
    maximal = msw.maximal(applicable)
    maximal_ids = {rule.id for rule in maximal}
    names = ruleset.atom_names

    lines = [f"ECCRS side  (pattern {format_body(pattern, names)})"]
    if not applicable:
        lines.append("  no applicable rules -> abstain")
        return lines

    for rule in sorted(applicable, key=lambda r: (len(r.body), r.id)):
        overriders = sorted(other.id for other in applicable if rule.body < other.body)
        status = (
            "MAXIMAL"
            if rule.id in maximal_ids
            else f"overridden by {', '.join(overriders)}"
        )
        # Rule ids are printed as they are in the ruleset file, so they can be grepped.
        lines.append(
            f"  {rule.id}: {format_body(rule.body, names)} => {rule.label}   [{status}]"
        )
    label = msw.predict(ruleset, pattern)
    verdict = "abstain (maximal rules disagree)" if label is None else f"label = {label}"
    lines.append(f"  MSW: {verdict}")
    return lines


def rc_trace(ruleset: RuleSet, ranked: RankedKB, pattern: Body) -> list[str]:
    verdict = query(ranked, pattern)
    names = ranked.kb.atom_names
    positive = format_literal((ranked.kb.label_atom, True), names)

    lines = [
        "RC side",
        f"  query 1:  F |~ {positive}     (supports class 1)",
        f"  query 2:  F |~ ~{positive}    (supports class 0)",
        f"  br(F) = {_rank(verdict.br_pattern)}, "
        f"br(F & {positive}) = {_rank(verdict.br_with_positive)}, "
        f"br(F & ~{positive}) = {_rank(verdict.br_with_negative)}",
    ]

    if verdict.vacuous:
        lines.append(
            "  F is inconsistent with the classical part of K: "
            "RC entails both queries vacuously"
        )
        return lines
    if verdict.label is None:
        # Two ways here: an ordinary tie, or br(F) = inf with F still possible
        # (settled classically). For a KB from a ruleset the second always abstains:
        # every rank-inf conditional has a body E_inf rules out, so a possible complete
        # pattern triggers none of them and m stays free. So the comparison printed
        # below only runs for finite br(F), where it really decided the answer.
        lines.append("  neither query entailed -> abstain")
        return lines

    decisive = [
        conditional
        for conditional, rank in ranked.ranks.items()
        if rank == verdict.br_pattern and conditional.body <= pattern
    ]
    comparison = (
        f"br(F) < br(F & ~{positive})"
        if verdict.label == 1
        else f"br(F) < br(F & {positive})"
    )
    lines.append(f"  {comparison} holds -> RC entails class {verdict.label}")
    lines.append(
        "  decisive conditionals at rank "
        f"{_rank(verdict.br_pattern)}, from ECCRS rules: "
        + (", ".join(sorted(c.source_rule_id for c in decisive)) or "none")
    )
    return lines


def explain(ruleset: RuleSet, ranked: RankedKB, pattern: Body, key: str = "") -> str:
    """The full two-sided trace, ending with whether the two sides agree."""
    header = f"--- pattern {key} ---" if key else "---"
    eccrs_label = msw.predict(ruleset, pattern)
    rc_label = query(ranked, pattern).label
    agreement = (
        "AGREE"
        if eccrs_label == rc_label
        else f"DIVERGE (MSW={eccrs_label}, RC={rc_label})"
    )
    body = [
        header,
        *eccrs_trace(ruleset, pattern),
        "",
        *rc_trace(ruleset, ranked, pattern),
    ]
    return "\n".join([*body, f"  => {agreement}"])
