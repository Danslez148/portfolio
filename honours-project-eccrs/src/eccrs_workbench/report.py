"""Agreement analysis: does RC predict what MSW predicts?

We ask what fraction of predictions agree. We measure two populations, both
exactly and with no sampling: a dataset's instances, and every complete pattern over
the atoms the ruleset mentions.

The pattern population is the full 2^a space because that's what the theorem is stated
over. With one-hot attributes many of those patterns can't happen (two bins of one
attribute both true), so the realisable subset is reported next to it.
"""

from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass

from . import msw
from .base_rank import RankedKB
from .model import Atom, Body, RuleSet, is_realisable, one_hot_families
from .parser import to_body
from .rational_closure import query

# Enumerating patterns is exponential in the rule atoms. Past this we refuse instead of
# quietly sampling. Scaling up would mean enumerating applicable-rule-set classes.
MAX_PATTERN_ATOMS = 20


def complete_patterns(atoms: Iterable[Atom]) -> Iterator[Body]:
    atoms = sorted(atoms)
    if len(atoms) > MAX_PATTERN_ATOMS:
        raise ValueError(
            f"{len(atoms)} atoms is {2 ** len(atoms)} patterns; exhaustive enumeration "
            f"is capped at {MAX_PATTERN_ATOMS} atoms. Restrict the ruleset or enumerate "
            "equivalence classes of applicable-rule-sets instead."
        )
    for bits in itertools.product([False, True], repeat=len(atoms)):
        yield frozenset(zip(atoms, bits, strict=True))


@dataclass(frozen=True)
class Row:
    key: str
    pattern: Body
    msw_label: int | None
    rc_label: int | None
    vacuous: bool
    truth: int | None = None
    realisable: bool = True  # could this pattern actually occur?

    @property
    def agrees(self) -> bool:
        return self.msw_label == self.rc_label


@dataclass(frozen=True)
class Agreement:
    name: str
    rows: tuple[Row, ...]

    @property
    def total(self) -> int:
        return len(self.rows)

    @property
    def agreeing(self) -> int:
        return sum(row.agrees for row in self.rows)

    @property
    def divergences(self) -> tuple[Row, ...]:
        return tuple(row for row in self.rows if not row.agrees)

    @property
    def rate(self) -> float:
        return self.agreeing / self.total if self.total else 1.0

    @property
    def abstentions(self) -> int:
        return sum(row.msw_label is None for row in self.rows)

    @property
    def vacuous(self) -> int:
        return sum(row.vacuous for row in self.rows)

    @property
    def accuracy(self) -> float | None:
        labelled = [row for row in self.rows if row.truth is not None]
        if not labelled:
            return None
        return sum(row.msw_label == row.truth for row in labelled) / len(labelled)

    #    Realisable subset: rows whose pattern could really occur. Same as the whole
    #    population unless the ruleset uses one-hot attributes.

    @property
    def realisable_rows(self) -> tuple[Row, ...]:
        return tuple(row for row in self.rows if row.realisable)

    @property
    def realisable_total(self) -> int:
        return len(self.realisable_rows)

    @property
    def realisable_agreeing(self) -> int:
        return sum(row.agrees for row in self.realisable_rows)

    @property
    def realisable_divergences(self) -> tuple[Row, ...]:
        return tuple(row for row in self.realisable_rows if not row.agrees)

    @property
    def realisable_rate(self) -> float:
        rows = self.realisable_rows
        return self.realisable_agreeing / len(rows) if rows else 1.0

    @property
    def has_unrealisable(self) -> bool:
        return self.realisable_total != self.total


def _row(
    ruleset: RuleSet,
    ranked: RankedKB,
    key: str,
    pattern: Body,
    truth=None,
    realisable: bool = True,
) -> Row:
    verdict = query(ranked, pattern)
    # The two class queries should never both hold. They do in the vacuous case
    # (pattern contradicts the classical part of the KB), which is flagged.
    assert verdict.vacuous or not (
        verdict.supports_positive and verdict.supports_negative
    ), f"both class queries entailed for {key}"
    return Row(
        key,
        pattern,
        msw.predict(ruleset, pattern),
        verdict.label,
        verdict.vacuous,
        truth,
        realisable,
    )


def over_patterns(ruleset: RuleSet, ranked: RankedKB) -> Agreement:
    families = one_hot_families(ruleset.atoms)
    rows = tuple(
        _row(
            ruleset,
            ranked,
            f"p{i}",
            pattern,
            realisable=is_realisable(pattern, families),
        )
        for i, pattern in enumerate(complete_patterns(ruleset.atoms))
    )
    return Agreement(f"feature patterns (2^{len(ruleset.atoms)})", rows)


@dataclass(frozen=True)
class PatternClass:
    """One class of complete patterns: all the patterns that satisfy exactly the same
    set of rule bodies.

    Both operators only look at that set. For MSW
    it's the whole input `A(F)`. For RC each clause is `{not b : b in B} or {label}`,
    which a pattern only falsifies by satisfying all of `B`, so a rule whose body isn't
    satisfied constrains nothing. One representative decides the class and its verdict
    is weighted by `count`.
    """

    applicable: frozenset[str]  # A(F): ids of rules whose body these patterns satisfy
    representative: Body
    count: int  # complete patterns in this class
    realisable: int  # ... of which this many can actually occur
    unrealisable: int  # ... and this many can't (two one-hot bins of one attribute)
    msw_label: int | None
    rc_label: int | None
    vacuous: bool

    @property
    def agrees(self) -> bool:
        return self.msw_label == self.rc_label


@dataclass(frozen=True)
class ClassAgreement:
    name: str
    classes: tuple[PatternClass, ...]

    @property
    def total(self) -> int:
        return sum(c.count for c in self.classes)

    @property
    def agreeing(self) -> int:
        return sum(c.count for c in self.classes if c.agrees)

    @property
    def divergences(self) -> tuple[PatternClass, ...]:
        return tuple(c for c in self.classes if not c.agrees)

    @property
    def rate(self) -> float:
        return self.agreeing / self.total if self.total else 1.0

    @property
    def abstentions(self) -> int:
        return sum(c.count for c in self.classes if c.msw_label is None)

    @property
    def vacuous(self) -> int:
        return sum(c.count for c in self.classes if c.vacuous)

    #    Realisable subset, weighted the same way. One class can hold both kinds of
    #    pattern, so the split is stored per class, not read off the representative.

    @property
    def realisable_total(self) -> int:
        return sum(c.realisable for c in self.classes)

    @property
    def realisable_agreeing(self) -> int:
        return sum(c.realisable for c in self.classes if c.agrees)

    @property
    def realisable_divergence_patterns(self) -> int:
        return sum(c.realisable for c in self.classes if not c.agrees)

    @property
    def realisable_rate(self) -> float:
        total = self.realisable_total
        return self.realisable_agreeing / total if total else 1.0

    @property
    def has_unrealisable(self) -> bool:
        return self.realisable_total != self.total


def collapse_patterns(ruleset: RuleSet, ranked: RankedKB) -> ClassAgreement:
    """The applicable-rule-set collapse: `over_patterns` with the same 2^a patterns and
    verdicts, but RC and MSW run once per class instead of once per pattern.

    First pass: walk every pattern and key it by `A(F)` (a subset test, no SAT).
    Second pass: evaluate one representative per class. Class sizes come out of the
    first pass, so the weighted percentages are exact and no model counting is needed.
    """
    families = one_hot_families(ruleset.atoms)
    rules = ruleset.rules

    representatives: dict[frozenset[str], Body] = {}
    counts: dict[frozenset[str], int] = defaultdict(int)
    realisable_counts: dict[frozenset[str], int] = defaultdict(int)
    for pattern in complete_patterns(ruleset.atoms):
        key = frozenset(rule.id for rule in rules if rule.body <= pattern)
        representatives.setdefault(key, pattern)
        counts[key] += 1
        if is_realisable(pattern, families):
            realisable_counts[key] += 1

    classes: list[PatternClass] = []
    for key, representative in representatives.items():
        verdict = query(ranked, representative)
        assert verdict.vacuous or not (
            verdict.supports_positive and verdict.supports_negative
        ), f"both class queries entailed for class {sorted(key)}"
        classes.append(
            PatternClass(
                applicable=key,
                representative=representative,
                count=counts[key],
                realisable=realisable_counts[key],
                unrealisable=counts[key] - realisable_counts[key],
                msw_label=msw.predict(ruleset, representative),
                rc_label=verdict.label,
                vacuous=verdict.vacuous,
            )
        )

    name = f"pattern classes ({len(classes)} of 2^{len(ruleset.atoms)})"
    return ClassAgreement(name, tuple(classes))


def over_instances(
    ruleset: RuleSet,
    ranked: RankedKB,
    instances: Mapping[int, Mapping[Atom, int]],
    class_atom: Atom | None = None,
    truths: Mapping[int, int] | None = None,
) -> Agreement:
    def truth_of(instance_id: int, values: Mapping[Atom, int]) -> int | None:
        if truths is not None:
            return truths.get(instance_id)
        return None if class_atom is None else values.get(class_atom)

    rows = tuple(
        _row(
            ruleset,
            ranked,
            str(instance_id),
            to_body(values, ruleset.atoms),
            truth_of(instance_id, values),
        )
        for instance_id, values in instances.items()
    )
    return Agreement("dataset instances", rows)


def render(agreements: Iterable[Agreement], max_divergences: int = 10) -> str:
    agreements = list(agreements)
    lines = [
        "| population | n | MSW = RC | agreement | MSW abstains "
        "| vacuous | MSW accuracy |",
        "|---|---|---|---|---|---|---|",
    ]
    for a in agreements:
        accuracy = "n/a" if a.accuracy is None else f"{a.accuracy:.1%}"
        lines.append(
            f"| {a.name} | {a.total} | {a.agreeing} | {a.rate:.1%} "
            f"| {a.abstentions} | {a.vacuous} | {accuracy} |"
        )

    for a in agreements:
        if a.has_unrealisable:
            lines += [
                "",
                f"Realisable subset ({a.name}): {a.realisable_total} of {a.total} "
                "patterns are physically possible under one-hot mutual exclusion; "
                f"MSW = RC on {a.realisable_agreeing} ({a.realisable_rate:.1%}), "
                f"{len(a.realisable_divergences)} divergences.",
            ]

    for a in agreements:
        if not a.divergences:
            lines += ["", f"No MSW/RC divergence over {a.name}."]
            continue
        lines += ["", f"Divergences over {a.name} ({len(a.divergences)}):"]
        for row in a.divergences[:max_divergences]:
            lines.append(f"  {row.key}: MSW={row.msw_label} RC={row.rc_label}")
        if len(a.divergences) > max_divergences:
            lines.append(f"  ... and {len(a.divergences) - max_divergences} more")
    return "\n".join(lines)
