"""Differential test against the upstream ECCRS implementation's own outputs.

Each dataset package ships two oracle files, made by a different author's
implementation using z3 rather than this workbench's DPLL, and sharing no code with
it:

  assumptions.json     -- strict_global_closure, sanity, no_total_override: each
                          true/false with violation lists
  msw_predictions.csv  -- per instance: y_true, msw_pred (0 / 1 / "abstain"),
                          applicable_rule_indices, maximal_rule_indices

Agreement is external evidence. A disagreement is a finding to investigate and
report, never a reason to loosen an assertion, skip an instance or add a tolerance
The files are compared against and never regenerated.

The rule-index columns matter most: they catch a right label reached for the wrong
reason, which a label-only check would miss.
"""

from __future__ import annotations

import ast
import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from eccrs_workbench import msw, validator
from eccrs_workbench.parser import parse_atom_name, parse_rules, to_body
from tests.examples import REPO

DATASETS = ("cancer", "mushroom", "bank")


def _package(name: str) -> Path:
    return REPO / "datasets" / name


# Reading the oracle files


@dataclass(frozen=True)
class OracleRow:
    instance_id: int
    pattern: frozenset
    pred: str  # "0", "1" or "abstain", verbatim from the oracle
    applicable: frozenset[int]
    maximal: frozenset[int]


def _read_msw_predictions(name: str, rule_atoms: frozenset) -> list[OracleRow]:
    path = _package(name) / "msw_predictions.csv"
    rows: list[OracleRow] = []
    with path.open(newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        y_at = header.index("y_true")
        feature_atoms = [parse_atom_name(h) for h in header[1:y_at]]
        assert rule_atoms <= set(feature_atoms), (
            f"{name}: rule atoms missing from msw_predictions.csv columns: "
            f"{sorted(rule_atoms - set(feature_atoms))}"
        )
        col = {h: i for i, h in enumerate(header)}
        for raw in reader:
            if not raw:
                continue
            values = {a: int(v) for a, v in zip(feature_atoms, raw[1:y_at], strict=True)}
            rows.append(
                OracleRow(
                    instance_id=int(raw[0]),
                    pattern=to_body(values, rule_atoms),
                    pred=raw[col["msw_pred"]].strip(),
                    applicable=frozenset(
                        ast.literal_eval(raw[col["applicable_rule_indices"]])
                    ),
                    maximal=frozenset(ast.literal_eval(raw[col["maximal_rule_indices"]])),
                )
            )
    return rows


def _read_assumptions(name: str) -> dict:
    return json.loads((_package(name) / "assumptions.json").read_text())


# The comparison


@dataclass
class Comparison:
    name: str
    n_instances: int = 0
    pred_matches: int = 0
    applicable_matches: int = 0
    maximal_matches: int = 0
    assumptions_checked: int = 0
    assumptions_matched: int = 0
    mismatches: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.mismatches


def _my_pred(pattern: frozenset, ruleset) -> str:
    label = msw.predict(ruleset, pattern)
    return "abstain" if label is None else str(label)


def compare(name: str) -> Comparison:
    ruleset = parse_rules(_package(name) / "rules.txt")
    index_of = {rule.id: i for i, rule in enumerate(ruleset.rules)}
    result = Comparison(name)

    # Assumptions
    checks = {
        "strict_global_closure": (
            validator.check_strict_closure(ruleset),
            "strict_global_closure_violations",
        ),
        "sanity": (validator.check_sanity(ruleset), "sanity_violations"),
        "no_total_override": (
            validator.check_no_total_override(ruleset),
            "no_total_override_failed_rule_indices",
        ),
    }
    oracle = _read_assumptions(name)
    for key, (my_violations, detail_key) in checks.items():
        result.assumptions_checked += 1
        my_holds = my_violations == []
        if my_holds == oracle[key]:
            result.assumptions_matched += 1
        else:
            result.mismatches.append(
                f"[{name}] assumption {key}: mine={'holds' if my_holds else 'FAILS'} "
                f"({[v.detail for v in my_violations]}), "
                f"oracle={oracle[key]} ({oracle.get(detail_key)})"
            )

    # MSW predictions, applicable set, maximal set
    for row in _read_msw_predictions(name, ruleset.atoms):
        result.n_instances += 1
        applicable = msw.applicable(ruleset, row.pattern)
        maximal = msw.maximal(applicable)
        my_applicable = frozenset(index_of[r.id] for r in applicable)
        my_maximal = frozenset(index_of[r.id] for r in maximal)
        my_pred = _my_pred(row.pattern, ruleset)

        pred_ok = my_pred == row.pred
        app_ok = my_applicable == row.applicable
        max_ok = my_maximal == row.maximal
        result.pred_matches += pred_ok
        result.applicable_matches += app_ok
        result.maximal_matches += max_ok

        if not (pred_ok and app_ok and max_ok):
            result.mismatches.append(
                f"[{name}] instance {row.instance_id}: "
                f"pred mine={my_pred} oracle={row.pred}; "
                f"applicable mine={sorted(my_applicable)} "
                f"oracle={sorted(row.applicable)}; "
                f"maximal mine={sorted(my_maximal)} oracle={sorted(row.maximal)}"
            )
    return result


# Tests


@pytest.fixture(scope="session")
def comparisons() -> dict[str, Comparison]:
    return {name: compare(name) for name in DATASETS}


@pytest.mark.parametrize("name", DATASETS)
def test_assumptions_match_the_z3_oracle(comparisons, name):
    result = comparisons[name]
    assert result.assumptions_matched == result.assumptions_checked, "\n".join(
        m for m in result.mismatches if "assumption" in m
    )


@pytest.mark.parametrize("name", DATASETS)
def test_msw_predictions_applicable_and_maximal_sets_match(comparisons, name):
    result = comparisons[name]
    assert result.pred_matches == result.n_instances, "\n".join(result.mismatches)
    assert result.applicable_matches == result.n_instances, "\n".join(result.mismatches)
    assert result.maximal_matches == result.n_instances, "\n".join(result.mismatches)


def test_print_the_per_dataset_table(comparisons):
    lines = [
        "",
        f"{'dataset':<10} {'instances':>10} {'pred':>12} {'applicable':>12} "
        f"{'maximal':>12} {'assumptions':>12}",
    ]
    for name in DATASETS:
        r = comparisons[name]
        lines.append(
            f"{name:<10} {r.n_instances:>10} "
            f"{f'{r.pred_matches}/{r.n_instances}':>12} "
            f"{f'{r.applicable_matches}/{r.n_instances}':>12} "
            f"{f'{r.maximal_matches}/{r.n_instances}':>12} "
            f"{f'{r.assumptions_matched}/{r.assumptions_checked}':>12}"
        )
    total = sum(r.n_instances for r in comparisons.values())
    lines.append(f"{'TOTAL':<10} {total:>10}")
    print("\n".join(lines))
    assert all(r.clean for r in comparisons.values()), "\n".join(
        m for r in comparisons.values() for m in r.mismatches
    )
