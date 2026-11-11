"""Core types: atoms, literals, ECCRS rules, KLM conditionals, materialisation.

An atom is an int tuple, a literal is (atom, polarity), and bodies and clauses are
frozensets. That makes "more specific" a subset test and keeps everything hashable,
so it can be a key in the rank and memo dicts.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

# (i,) for a plain indicator a(i), (i, j) for a one-hot bin a(i,j). The two shapes never
# compare equal, so a two-index dataset can't be read as single-index by accident. Tuples
# sort attribute-then-bin, which is the order in the ruleset file, so traces line up.
Atom = tuple[int, ...]
# (atom, polarity). polarity True = positive.
Literal = tuple[Atom, bool]
# A conjunction of literals, no atom appearing twice.
Body = frozenset[Literal]
# A disjunction of literals.
Clause = frozenset[Literal]


def atom(index: int, value_bin: int | None = None) -> Atom:
    return (index,) if value_bin is None else (index, value_bin)


def format_atom(a: Atom) -> str:
    return f"a({','.join(map(str, a))})"


def one_hot_families(atoms: Iterable[Atom]) -> dict[int, frozenset[Atom]]:
    """Two-index atoms grouped by attribute index (groups of one bin are dropped).

    Each group is the one-hot bins of one attribute, so at most one is true in a real
    instance. This is the only place we read attribute structure off atom names, and it
    trusts the upstream encoding to make same-index a(i,j) atoms one-hot. Single-index
    a(i) atoms are independent and never grouped.
    """
    by_index: dict[int, set[Atom]] = {}
    for a in atoms:
        if len(a) == 2:
            by_index.setdefault(a[0], set()).add(a)
    return {i: frozenset(bins) for i, bins in by_index.items() if len(bins) > 1}


def is_realisable(pattern: Body, families: Mapping[int, frozenset[Atom]]) -> bool:
    """True if the pattern sets at most one bin per one-hot family, so it could
    occur. At most one, not exactly one: the true bin might be one no rule mentions."""
    return all(sum((a, True) in pattern for a in bins) <= 1 for bins in families.values())


def negate(literal: Literal) -> Literal:
    return (literal[0], not literal[1])


@dataclass(frozen=True)
class Rule:
    id: str
    body: Body
    label: int


@dataclass(frozen=True)
class Conditional:
    body: Body
    label: Literal  # always the label atom m, signed
    source_rule_id: str


@dataclass(frozen=True, eq=False)
class ConditionalKB:
    conditionals: tuple[Conditional, ...]
    label_atom: Atom
    atom_names: Mapping[Atom, str] = field(default_factory=dict)

    def materialised_clauses(self) -> list[Clause]:
        return materialise(self.conditionals)


@dataclass(frozen=True, eq=False)
class RuleSet:
    rules: tuple[Rule, ...]
    atom_names: Mapping[Atom, str] = field(default_factory=dict)

    @property
    def atoms(self) -> frozenset[Atom]:
        return frozenset(a for rule in self.rules for a, _ in rule.body)

    def to_kb(self, label_atom: Atom | None = None) -> ConditionalKB:
        """Translate to a KLM conditional KB: label 1 becomes B |~ m, label 0 becomes
        B |~ ~m, one conditional per rule.

        The default m goes above every atom we know about, including ones only in
        atom_names. That still only sees the ruleset; pass label_atom from
        parser.safe_label_atom to also clear the dataset's atoms.
        """
        if label_atom is None:
            known = set(self.atoms) | set(self.atom_names)
            label_atom = (max((a[0] for a in known), default=0) + 1,)
        conditionals = tuple(
            Conditional(rule.body, (label_atom, rule.label == 1), rule.id)
            for rule in self.rules
        )
        names = dict(self.atom_names)
        names.setdefault(label_atom, "m")
        return ConditionalKB(conditionals, label_atom, names)


def materialise(conditionals: Iterable[Conditional]) -> list[Clause]:
    """B |~ l becomes the one clause {~b for b in B} + {l}."""
    return [frozenset({negate(b) for b in c.body} | {c.label}) for c in conditionals]


def format_literal(literal: Literal, names: Mapping[Atom, str]) -> str:
    a, polarity = literal
    return ("" if polarity else "~") + names.get(a, format_atom(a))


def format_body(body: Body, names: Mapping[Atom, str]) -> str:
    return " & ".join(format_literal(lit, names) for lit in sorted(body)) or "true"
