"""Readers for the input formats.

Rulesets (e.g. datasets/cancer/rules.txt): `<id>: IF a(i)=v & a(j,k)=v ... THEN y=<0|1>`
Instances come two ways:
  - `data-*.lp`:      `val(<instance>, a(<atom>), <0|1>).`  (ASP facts; class is guessed)
  - `instances.csv`:  `instance_id, <one column per feature atom>, y`  (class is `y`)

Atoms have two shapes: `a(i)` is a plain binary indicator and `a(i,j)` is one-hot bin
`j` of attribute `i` (see model.Atom). Cancer is all `a(i)`, bank all `a(i,j)`, mushroom
a mix, sometimes in one rule.

Atom indices aren't contiguous: cancer has no a(6) (Bare Nuclei, dropped upstream
because of missing values).
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path

from .model import Atom, Body, Rule, RuleSet, format_atom

_RULE = re.compile(r"^\s*([^:]+?)\s*:\s*IF\s+(.+?)\s+THEN\s+y\s*=\s*([01])\s*$", re.I)
# a(i)=v or a(i,j)=v; the second index is optional.
_LITERAL = re.compile(r"a\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\)\s*=\s*([01])")
_FACT = re.compile(
    r"val\(\s*(\d+)\s*,\s*a\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\)\s*,\s*([01])\s*\)\s*\."
)
# A bare atom name, as it appears in a CSV column header: a(i) or a(i,j).
_ATOM_NAME = re.compile(r"a\(\s*(\d+)\s*(?:,\s*(\d+)\s*)?\)")


def _atom(index: str, value_bin: str | None) -> Atom:
    return (int(index),) if value_bin is None else (int(index), int(value_bin))


def parse_atom_name(name: str) -> Atom:
    match = _ATOM_NAME.fullmatch(name.strip())
    if not match:
        raise ValueError(f"not an atom name: {name!r}")
    return _atom(*match.groups())


def parse_rules(path: str | Path) -> RuleSet:
    rules: list[Rule] = []
    for lineno, line in enumerate(Path(path).read_text().splitlines(), start=1):
        line = line.split("#")[0].strip()
        if not line:
            continue
        match = _RULE.match(line)
        if not match:
            raise ValueError(f"{path}:{lineno}: cannot parse rule: {line!r}")
        rule_id, conditions, label = match.groups()

        # Split on & and require every piece to be a literal, don't findall. A findall
        # for a(i)=v silently drops a(i,j)=v pieces, which is what happened on mushroom
        # (rules 0-6 got truncated bodies). See tests/test_two_index_atoms.py.
        literals = []
        for conjunct in conditions.split("&"):
            lit = _LITERAL.fullmatch(conjunct.strip())
            if not lit:
                raise ValueError(
                    f"{path}:{lineno}: cannot parse literal {conjunct.strip()!r} "
                    f"in {line!r}"
                )
            index, value_bin, value = lit.groups()
            literals.append((_atom(index, value_bin), value == "1"))

        body: Body = frozenset(literals)
        if len({a for a, _ in literals}) != len(literals):
            raise ValueError(
                f"{path}:{lineno}: an atom appears twice in the body (duplicate or "
                f"contradictory literal): {line!r}"
            )
        if not body:
            raise ValueError(f"{path}:{lineno}: rule has no conditions: {line!r}")
        rules.append(Rule(rule_id, body, int(label)))

    # Ids must be unique: conditionals key the rank dict, so two identical rules would
    # collapse into one entry and a conditional would vanish without an error.
    counts = Counter(rule.id for rule in rules)
    duplicates = sorted(rule_id for rule_id, n in counts.items() if n > 1)
    if duplicates:
        raise ValueError(f"{path}: duplicate rule ids: {duplicates}")

    atoms = {a for rule in rules for a, _ in rule.body}
    return RuleSet(tuple(rules), {a: format_atom(a) for a in sorted(atoms)})


def parse_instances(path: str | Path) -> dict[int, dict[Atom, int]]:
    instances: dict[int, dict[Atom, int]] = {}
    for lineno, line in enumerate(Path(path).read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        fact = _FACT.fullmatch(line)
        if not fact:
            raise ValueError(f"{path}:{lineno}: not a val/3 fact: {line!r}")
        instance, index, value_bin, value = fact.groups()
        instances.setdefault(int(instance), {})[_atom(index, value_bin)] = int(value)
    return instances


def read_instances_csv(
    path: str | Path,
) -> tuple[dict[int, dict[Atom, int]], dict[int, int]]:
    with Path(path).open(newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError(f"{path}: empty file") from None

        if not header or header[0] != "instance_id":
            raise ValueError(
                f"{path}: first column must be 'instance_id', got {header[:1]}"
            )
        if header[-1] != "y":
            raise ValueError(
                f"{path}: last column must be the label 'y', got {header[-1]!r}"
            )

        atoms: list[Atom] = []
        for name in header[1:-1]:
            try:
                atoms.append(parse_atom_name(name))
            except ValueError:
                raise ValueError(
                    f"{path}: header column {name!r} is not an atom name"
                ) from None

        instances: dict[int, dict[Atom, int]] = {}
        labels: dict[int, int] = {}
        for lineno, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(
                    f"{path}:{lineno}: {len(row)} fields, header has {len(header)}"
                )
            instance_id = int(row[0])
            instances[instance_id] = {
                a: int(v) for a, v in zip(atoms, row[1:-1], strict=True)
            }
            labels[instance_id] = int(row[-1])
    return instances, labels


def infer_class_atom(instances: Mapping[int, Mapping[Atom, int]]) -> Atom:
    """Guess the class column: the highest atom in the data.

    For data-cancer.lp that's a(10), with features a(1)-a(9) before it. With mixed
    shapes "highest" is the largest attribute index, ties going to the two-index form.
    It's only a convention, which is why the CLI has --class-atom.
    """
    atoms = {a for values in instances.values() for a in values}
    if not atoms:
        raise ValueError("no instances found")
    return max(atoms)


def safe_label_atom(
    ruleset: RuleSet, instances: Mapping[int, Mapping[Atom, int]]
) -> Atom:
    """A fresh single-index atom above every atom in the ruleset AND the dataset.

    RuleSet.to_kb() only sees the ruleset, so for datasets/cancer/rules.txt it would pick
    a(9), which is a real dataset feature. Nothing breaks now since patterns are
    projected onto rule atoms first, but it's a trap for anyone who forgets to project.
    """
    dataset_atoms = {a for values in instances.values() for a in values}
    known = set(ruleset.atoms) | set(ruleset.atom_names) | dataset_atoms
    return (max((a[0] for a in known), default=0) + 1,)


def to_body(assignment: Mapping[Atom, int], atoms: Iterable[Atom] | None = None) -> Body:
    """Turn {atom: 0|1} into a Body, optionally projected onto `atoms` (columns no rule
    mentions are dropped).

    A projected body is complete over `atoms`: an atom missing from `assignment` counts
    as 0. Bank's .lp files only record the active bin of each one-hot attribute, so the
    absent bins have to mean false. If they were dropped, a rule needing a(i,j)=0 would
    look inapplicable and MSW would abstain by mistake. Cancer and mushroom write every
    0 out, so they're unaffected. Instances with missing values were dropped upstream.
    """
    if atoms is None:
        pairs: Iterable[tuple[Atom, int]] = assignment.items()
    else:
        pairs = ((a, assignment.get(a, 0)) for a in atoms)
    return frozenset((a, bool(value)) for a, value in pairs)
