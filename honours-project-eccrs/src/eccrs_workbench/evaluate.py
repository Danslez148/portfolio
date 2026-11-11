"""The final evaluation run: every number the results section needs.

    python -m eccrs_workbench.evaluate          # rules.txt + instances.csv + patterns
    python -m eccrs_workbench.evaluate --full   # also the full data-*.lp instance sets

`--full` is separate because `data-bank.lp` and `data-mushroom.lp` are 16-18 MB and take
 seconds to parse and evaluate; the other populations take well under a second.

Three populations per dataset, each with the same columns (n, agree, disagree,
both_abstain, agreement_pct):

- csv_holdout:   the upstream 25% stratified holdout, true label from `y`
- lp_instances:  the whole `.lp` dataset, true label guessed (highest atom id); only
                 with --full
- pattern_space: every complete pattern over the ruleset's atoms (2^a) from
                 `report.over_patterns`, plus the realisable subset under one-hot
                 mutual exclusion

`agree`, `disagree` and `both_abstain` are always separate raw counts.
`agreement_pct` is `(agree + both_abstain) / n`, so both operators abstaining counts as
agreeing. That matches the alignment theorem and
`report.Agreement.rate`; see `population_stats`. It changes no number on cancer,
mushroom or bank (0 both_abstain on all three), only the scholarship fixture (59.4%
without, 96.9% with).

SAT-call and wall-clock numbers come from `baseline.measure` (naive / shipped /
collapsed), so nothing is measured twice.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from . import baseline, msw, report, validator
from .base_rank import base_rank
from .explanation import explain
from .model import Body, RuleSet, format_body
from .parser import (
    infer_class_atom,
    parse_instances,
    parse_rules,
    read_instances_csv,
    safe_label_atom,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "results"

DATASETS: tuple[str, ...] = ("cancer", "mushroom", "bank")

# The scholarship counter-example. It breaks strict global exception closure, so it
# shows the theorem's hypotheses failing, not the theorem.
SCHOLARSHIP_RULES = REPO_ROOT / "tests" / "fixtures" / "scholarship.rules.txt"
SCHOLARSHIP_INSTANCE_A = frozenset(
    {((1,), True), ((2,), False), ((3,), False), ((4,), True), ((5,), True)}
)


def population_stats(agreement: report.Agreement) -> dict:
    """n / agree / disagree / both_abstain / agreement_pct for one population.

    `agree`, `disagree` and `both_abstain` are separate raw counts, so I can see how
    much of a headline figure is real label matches and how much is both sides
    abstaining.

    `agreement_pct` counts both abstaining as agreement
    """
    rows = agreement.rows
    n = len(rows)
    both_abstain = sum(1 for r in rows if r.msw_label is None and r.rc_label is None)
    agree = sum(1 for r in rows if r.msw_label == r.rc_label and r.msw_label is not None)
    disagree = n - agree - both_abstain
    return {
        "n": n,
        "agree": agree,
        "disagree": disagree,
        "both_abstain": both_abstain,
        "agreement_pct": (agree + both_abstain) / n if n else 1.0,
        "vacuous": sum(1 for r in rows if r.vacuous),
    }


def realisable_stats(agreement: report.Agreement) -> dict:
    rows = agreement.realisable_rows
    n = len(rows)
    both_abstain = sum(1 for r in rows if r.msw_label is None and r.rc_label is None)
    agree = sum(1 for r in rows if r.msw_label == r.rc_label and r.msw_label is not None)
    disagree = n - agree - both_abstain
    return {
        "n": n,
        "agree": agree,
        "disagree": disagree,
        "both_abstain": both_abstain,
        "agreement_pct": (agree + both_abstain) / n if n else 1.0,
    }


def _divergence_detail(
    name: str, population: str, agreement: report.Agreement, atom_names: dict
) -> list[dict]:
    return [
        {
            "dataset": name,
            "population": population,
            "key": row.key,
            "pattern": format_body(row.pattern, atom_names),
            "msw_label": row.msw_label,
            "rc_label": row.rc_label,
            "vacuous": row.vacuous,
        }
        for row in agreement.divergences
    ]


@dataclass(frozen=True)
class DatasetResult:
    name: str
    rules: int
    rule_atoms: int
    distinct_ranks: int
    patterns_total: int
    patterns_realisable: int
    applicable_rule_set_classes: int
    empty_applicable_patterns: int
    validator_violations: list[str]
    csv_holdout: dict | None
    lp_instances: dict | None
    pattern_space: dict
    pattern_space_realisable: dict
    msw_accuracy_csv: float | None
    msw_accuracy_lp: float | None
    divergences: list[dict]


def evaluate_dataset(
    name: str,
    rules_path: str | Path,
    csv_path: str | Path | None,
    lp_path: str | Path | None,
    *,
    include_lp: bool = False,
) -> DatasetResult:
    ruleset = parse_rules(rules_path)
    violations = validator.validate(ruleset)

    csv_instances: dict | None = None
    csv_truths: dict | None = None
    if csv_path is not None:
        csv_instances, csv_truths = read_instances_csv(csv_path)

    lp_instances: dict | None = None
    if lp_path is not None and Path(lp_path).exists():
        # Parsed even without include_lp, because safe_label_atom needs every atom the
        # dataset has (baseline.py does the same).
        # Only the agreement pass over it depends on include_lp.
        lp_instances = parse_instances(lp_path)

    label_instances = lp_instances or csv_instances or {}
    label_atom = safe_label_atom(ruleset, label_instances)
    ranked = base_rank(ruleset.to_kb(label_atom))

    patterns_total = len(list(report.complete_patterns(ruleset.atoms)))
    empty_applicable = sum(
        1
        for pattern in report.complete_patterns(ruleset.atoms)
        if not msw.applicable(ruleset, pattern)
    )
    applicable_rule_set_classes = len(
        {
            frozenset(rule.id for rule in msw.applicable(ruleset, pattern))
            for pattern in report.complete_patterns(ruleset.atoms)
        }
    )

    atom_names = ruleset.atom_names
    pattern_agreement = report.over_patterns(ruleset, ranked)
    pattern_stats = population_stats(pattern_agreement)
    pattern_realisable_stats = realisable_stats(pattern_agreement)
    divergences = _divergence_detail(name, "pattern_space", pattern_agreement, atom_names)

    csv_stats = None
    msw_accuracy_csv = None
    if csv_instances is not None:
        csv_agreement = report.over_instances(
            ruleset, ranked, csv_instances, truths=csv_truths
        )
        csv_stats = population_stats(csv_agreement)
        msw_accuracy_csv = csv_agreement.accuracy
        divergences += _divergence_detail(name, "csv_holdout", csv_agreement, atom_names)

    lp_stats = None
    msw_accuracy_lp = None
    if include_lp and lp_instances is not None:
        class_atom = infer_class_atom(lp_instances)
        lp_agreement = report.over_instances(
            ruleset, ranked, lp_instances, class_atom=class_atom
        )
        lp_stats = population_stats(lp_agreement)
        msw_accuracy_lp = lp_agreement.accuracy
        divergences += _divergence_detail(name, "lp_instances", lp_agreement, atom_names)

    return DatasetResult(
        name=name,
        rules=len(ruleset.rules),
        rule_atoms=len(ruleset.atoms),
        distinct_ranks=len(ranked.order),
        patterns_total=patterns_total,
        patterns_realisable=pattern_agreement.realisable_total,
        applicable_rule_set_classes=applicable_rule_set_classes,
        empty_applicable_patterns=empty_applicable,
        validator_violations=[f"{v.check}: {v.detail}" for v in violations],
        csv_holdout=csv_stats,
        lp_instances=lp_stats,
        pattern_space=pattern_stats,
        pattern_space_realisable=pattern_realisable_stats,
        msw_accuracy_csv=msw_accuracy_csv,
        msw_accuracy_lp=msw_accuracy_lp,
        divergences=divergences,
    )


def instance_a_trace(ruleset: RuleSet, ranked, pattern: Body) -> str:
    return explain(ruleset, ranked, pattern, key="Instance A")


def evaluate_scholarship() -> dict:
    result = evaluate_dataset(
        "scholarship", SCHOLARSHIP_RULES, None, None, include_lp=False
    )
    ruleset = parse_rules(SCHOLARSHIP_RULES)
    ranked = base_rank(ruleset.to_kb())
    trace = instance_a_trace(ruleset, ranked, SCHOLARSHIP_INSTANCE_A)
    return {"result": result, "instance_a_trace": trace}


def _sat_summary(name: str, rules_path: Path, lp_path: Path) -> dict:
    m = baseline.measure(
        name, str(rules_path.relative_to(REPO_ROOT)), str(lp_path.relative_to(REPO_ROOT))
    )
    return {
        "base_rank_calls": m.base_rank_calls,
        "naive_total_calls": m.naive_total_calls,
        "naive_mean_calls": m.naive_mean_calls,
        "naive_max_calls": m.naive_max_calls,
        "shipped_total_calls": m.shipped_total_calls,
        "shipped_mean_calls": m.shipped_mean_calls,
        "shipped_max_calls": m.shipped_max_calls,
        "collapsed_total_calls": m.collapsed_total_calls,
        "collapsed_mean_calls": m.collapsed_mean_calls,
        "collapsed_max_calls": m.collapsed_max_calls,
        "peak_clause_set_size": m.peak_clause_set_size,
        "wall_clock_naive_s": m.wall_clock_naive_s,
        "wall_clock_shipped_s": m.wall_clock_shipped_s,
        "wall_clock_collapsed_s": m.wall_clock_collapsed_s,
    }


def write_outputs(
    results: list[DatasetResult],
    out_dir: str | Path,
    *,
    scholarship: dict | None,
    sat_summaries: dict[str, dict] | None = None,
) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "datasets": [asdict(r) for r in results],
    }
    if sat_summaries is not None:
        payload["sat"] = sat_summaries
    if scholarship is not None:
        payload["scholarship"] = {
            "result": asdict(scholarship["result"]),
            "instance_a_trace": scholarship["instance_a_trace"],
        }
    (out_dir / "evaluation.json").write_text(json.dumps(payload, indent=2) + "\n")

    fieldnames = [
        "dataset",
        "population",
        "n",
        "agree",
        "disagree",
        "both_abstain",
        "agreement_pct",
        "vacuous",
    ]
    with (out_dir / "agreement.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, restval="")
        writer.writeheader()
        all_results = list(results)
        if scholarship is not None:
            all_results.append(scholarship["result"])
        for r in all_results:
            for population_name, stats in (
                ("csv_holdout", r.csv_holdout),
                ("lp_instances", r.lp_instances),
                ("pattern_space", r.pattern_space),
                ("pattern_space_realisable", r.pattern_space_realisable),
            ):
                if stats is None:
                    continue
                row = {"dataset": r.name, "population": population_name, **stats}
                writer.writerow(row)


def render_summary(results: list[DatasetResult], scholarship: dict | None = None) -> str:
    lines = [
        "| Dataset | Rules | Atoms | Ranks | Patterns | Realisable | Classes "
        "| CSV n | CSV agree % | .lp n | .lp agree % | .lp MSW acc | Pattern agree % |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        csv_n = r.csv_holdout["n"] if r.csv_holdout else "n/a"
        csv_pct = f"{r.csv_holdout['agreement_pct']:.1%}" if r.csv_holdout else "n/a"
        lp_n = r.lp_instances["n"] if r.lp_instances else "n/a"
        lp_pct = f"{r.lp_instances['agreement_pct']:.1%}" if r.lp_instances else "n/a"
        lp_acc = f"{r.msw_accuracy_lp:.1%}" if r.msw_accuracy_lp is not None else "n/a"
        lines.append(
            f"| {r.name} | {r.rules} | {r.rule_atoms} | {r.distinct_ranks} "
            f"| {r.patterns_total} | {r.patterns_realisable} "
            f"| {r.applicable_rule_set_classes} | {csv_n} | {csv_pct} "
            f"| {lp_n} | {lp_pct} | {lp_acc} "
            f"| {r.pattern_space['agreement_pct']:.1%} |"
        )
    if scholarship is not None:
        sr = scholarship["result"]
        lines += [
            "",
            f"Scholarship (counter-example, violates strict closure): "
            f"{sr.pattern_space['n']} patterns, "
            f"{sr.pattern_space['disagree']} divergence(s), "
            f"{sr.pattern_space['both_abstain']} both-abstain.",
        ]
        if sr.divergences:
            d = sr.divergences[0]
            lines.append(
                f"  divergence: {d['pattern']} -> MSW={d['msw_label']} RC={d['rc_label']}"
            )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="also evaluate the full data-*.lp instance sets (slow: 16-18 MB files)",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help=f"where to write the output files (default: {DEFAULT_OUT_DIR})",
    )
    args = parser.parse_args(argv)

    results = []
    for name in DATASETS:
        pkg = REPO_ROOT / "datasets" / name
        result = evaluate_dataset(
            name,
            pkg / "rules.txt",
            pkg / "instances.csv",
            pkg / f"data-{name}.lp",
            include_lp=args.full,
        )
        results.append(result)

    scholarship = evaluate_scholarship()

    sat_summaries = {
        name: _sat_summary(
            name,
            REPO_ROOT / "datasets" / name / "rules.txt",
            REPO_ROOT / "datasets" / name / f"data-{name}.lp",
        )
        for name in DATASETS
    }

    write_outputs(
        results, args.out_dir, scholarship=scholarship, sat_summaries=sat_summaries
    )

    print(render_summary(results, scholarship))
    print()
    print("SAT calls, naive / shipped (binary search) / A1 (collapsed), per dataset:")
    for name, s in sat_summaries.items():
        print(
            f"  {name}: {s['naive_total_calls']} / {s['shipped_total_calls']} "
            f"/ {s['collapsed_total_calls']}  "
            f"(wall-clock {s['wall_clock_naive_s']:.3f}s / "
            f"{s['wall_clock_shipped_s']:.3f}s / {s['wall_clock_collapsed_s']:.3f}s)"
        )
    print()
    print(f"Written to {args.out_dir}/evaluation.json and {args.out_dir}/agreement.csv")
    print()
    print("--- Scholarship Instance A trace ---")
    print(scholarship["instance_a_trace"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
