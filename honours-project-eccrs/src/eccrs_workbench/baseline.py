"""SAT-call measurement for the pattern-space run.

Prints the markdown tables of SAT-call counts and timings for each dataset. Rerun it
after any later optimisation to get the next numbers from the same code path; that's
why it's a script.

    python -m eccrs_workbench.baseline

Three paths are measured side by side over the whole pattern space:

- **naive**: the plain published pseudocode in `naive.py` (ascending scan, clauses
  rebuilt at each rank), once per pattern;
- **shipped**: `rational_closure.query` (binary search, cumulative clause sets,
  memoisation), once per pattern;
- **A1** (the applicable-rule-set collapse): `report.collapse_patterns`, the shipped
  query run once per class of patterns instead of once per pattern.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from . import msw, naive, rational_closure, report
from .base_rank import base_rank
from .parser import parse_instances, parse_rules, safe_label_atom
from .sat import count_calls

REPO_ROOT = Path(__file__).resolve().parents[2]

# (name, rules.txt, data-*.lp). We use the .lp rather than instances.csv because it has
# every atom the ruleset could mention, which safe_label_atom has to stay above
# (see parser.safe_label_atom).
DATASETS: tuple[tuple[str, str, str], ...] = (
    ("cancer", "datasets/cancer/rules.txt", "datasets/cancer/data-cancer.lp"),
    ("mushroom", "datasets/mushroom/rules.txt", "datasets/mushroom/data-mushroom.lp"),
    ("bank", "datasets/bank/rules.txt", "datasets/bank/data-bank.lp"),
)

WALL_CLOCK_REPS = 5


@dataclass(frozen=True)
class Measurement:
    name: str
    rules: int
    rule_atoms: int
    distinct_ranks: int
    patterns: int
    applicable_rule_set_classes: int
    base_rank_calls: int
    shipped_total_calls: int
    shipped_mean_calls: float
    shipped_max_calls: int
    naive_total_calls: int
    naive_mean_calls: float
    naive_max_calls: int
    collapsed_total_calls: int
    collapsed_mean_calls: float
    collapsed_max_calls: int
    peak_clause_set_size: int
    wall_clock_shipped_s: float
    wall_clock_naive_s: float
    wall_clock_collapsed_s: float


def _mean(values: list[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def measure(name: str, rules_path: str, lp_path: str) -> Measurement:
    ruleset = parse_rules(str(REPO_ROOT / rules_path))
    instances = parse_instances(str(REPO_ROOT / lp_path))
    label_atom = safe_label_atom(ruleset, instances)
    kb = ruleset.to_kb(label_atom)

    # Clear the caches so earlier datasets or runs in this process don't help this one.
    rational_closure.base_rank_of.cache_clear()
    rational_closure.query.cache_clear()

    with count_calls() as c:
        ranked = base_rank(kb)
    base_rank_calls = c.calls
    peak_clause_set_size = c.peak_clause_set_size

    patterns = list(report.complete_patterns(ruleset.atoms))

    applicable_classes = {
        frozenset(rule.id for rule in msw.applicable(ruleset, pattern))
        for pattern in patterns
    }

    shipped_counts: list[int] = []
    for pattern in patterns:
        with count_calls() as c:
            rational_closure.query(ranked, pattern)
        shipped_counts.append(c.calls)
        peak_clause_set_size = max(peak_clause_set_size, c.peak_clause_set_size)

    naive_counts: list[int] = []
    for pattern in patterns:
        with count_calls() as c:
            naive.query(ranked, pattern, label_atom)
        naive_counts.append(c.calls)
        peak_clause_set_size = max(peak_clause_set_size, c.peak_clause_set_size)

    # Collapsed: the shipped query once per class. Grouping makes no SAT calls, so
    # counting the per-representative queries on a fresh cache gives exactly what
    # collapse_patterns' evaluation pass costs.
    representatives = [
        cls.representative for cls in report.collapse_patterns(ruleset, ranked).classes
    ]
    rational_closure.base_rank_of.cache_clear()
    rational_closure.query.cache_clear()
    collapsed_counts: list[int] = []
    for representative in representatives:
        with count_calls() as c:
            rational_closure.query(ranked, representative)
        collapsed_counts.append(c.calls)
        peak_clause_set_size = max(peak_clause_set_size, c.peak_clause_set_size)

    def timed_shipped() -> float:
        rational_closure.base_rank_of.cache_clear()
        rational_closure.query.cache_clear()
        start = time.perf_counter()
        for pattern in patterns:
            rational_closure.query(ranked, pattern)
        return time.perf_counter() - start

    def timed_naive() -> float:
        start = time.perf_counter()
        for pattern in patterns:
            naive.query(ranked, pattern, label_atom)
        return time.perf_counter() - start

    def timed_collapsed() -> float:
        rational_closure.base_rank_of.cache_clear()
        rational_closure.query.cache_clear()
        start = time.perf_counter()
        report.collapse_patterns(ruleset, ranked)
        return time.perf_counter() - start

    wall_clock_shipped = min(timed_shipped() for _ in range(WALL_CLOCK_REPS))
    wall_clock_naive = min(timed_naive() for _ in range(WALL_CLOCK_REPS))
    wall_clock_collapsed = min(timed_collapsed() for _ in range(WALL_CLOCK_REPS))

    return Measurement(
        name=name,
        rules=len(ruleset.rules),
        rule_atoms=len(ruleset.atoms),
        distinct_ranks=len(ranked.order),
        patterns=len(patterns),
        applicable_rule_set_classes=len(applicable_classes),
        base_rank_calls=base_rank_calls,
        shipped_total_calls=sum(shipped_counts),
        shipped_mean_calls=_mean(shipped_counts),
        shipped_max_calls=max(shipped_counts, default=0),
        naive_total_calls=sum(naive_counts),
        naive_mean_calls=_mean(naive_counts),
        naive_max_calls=max(naive_counts, default=0),
        collapsed_total_calls=sum(collapsed_counts),
        collapsed_mean_calls=_mean(collapsed_counts),
        collapsed_max_calls=max(collapsed_counts, default=0),
        peak_clause_set_size=peak_clause_set_size,
        wall_clock_shipped_s=wall_clock_shipped,
        wall_clock_naive_s=wall_clock_naive,
        wall_clock_collapsed_s=wall_clock_collapsed,
    )


def render(measurements: list[Measurement]) -> str:
    lines = [
        "| Dataset | Rules | Rule atoms | Distinct ranks | Patterns (2^a) "
        "| Applicable-rule-set classes |",
        "|---|---|---|---|---|---|",
    ]
    for m in measurements:
        lines.append(
            f"| {m.name} | {m.rules} | {m.rule_atoms} | {m.distinct_ranks} "
            f"| {m.patterns} | {m.applicable_rule_set_classes} |"
        )

    lines += [
        "",
        "Pattern-space SAT calls (total over the run, and per evaluation):",
        "",
        "| Dataset | naive scan | mean | max | shipped (binary search) | mean | max "
        "| A1 (per class) | mean | max |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for m in measurements:
        lines.append(
            f"| {m.name} "
            f"| {m.naive_total_calls} | {m.naive_mean_calls:.2f} | {m.naive_max_calls} "
            f"| {m.shipped_total_calls} | {m.shipped_mean_calls:.2f} "
            f"| {m.shipped_max_calls} "
            f"| {m.collapsed_total_calls} | {m.collapsed_mean_calls:.2f} "
            f"| {m.collapsed_max_calls} |"
        )

    lines += [
        "",
        "| Dataset | BaseRank SAT calls (one-off) | Evaluations: patterns -> classes "
        "| SAT calls: shipped -> A1 | Peak clause-set size "
        "| Wall-clock best of 5: naive / shipped / A1 |",
        "|---|---|---|---|---|---|",
    ]
    for m in measurements:
        speedup = (
            m.shipped_total_calls / m.collapsed_total_calls
            if m.collapsed_total_calls
            else 0.0
        )
        lines.append(
            f"| {m.name} | {m.base_rank_calls} "
            f"| {m.patterns} -> {m.applicable_rule_set_classes} "
            f"| {m.shipped_total_calls} -> {m.collapsed_total_calls} "
            f"({speedup:.0f}x) "
            f"| {m.peak_clause_set_size} "
            f"| {m.wall_clock_naive_s:.3f}s / {m.wall_clock_shipped_s:.3f}s "
            f"/ {m.wall_clock_collapsed_s:.3f}s |"
        )
    return "\n".join(lines)


def main() -> int:
    measurements = [measure(*spec) for spec in DATASETS]
    print(render(measurements))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
