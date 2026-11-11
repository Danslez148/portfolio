"""Live demo: pick a dataset folder and compare naive against optimised RC.

    python -m eccrs_workbench.demo                 # list datasets, ask which one
    python -m eccrs_workbench.demo cancer          # a folder under datasets/
    python -m eccrs_workbench.demo datasets/bank --mode optimised
    python -m eccrs_workbench.demo cancer --html   # also write demo-output/cancer.html
    python -m eccrs_workbench.demo tests/fixtures/scholarship.rules.txt

It's a thin layer over existing code and adds no reasoning of its own. A dataset folder
gives us `rules.txt` and, if there is one, `instances.csv` (`y` is the true label). The
16-18 MB `data-*.lp` files aren't loaded because they're too slow for a live demo. The
label atom `m` still goes above every atom in the ruleset and the CSV
(`parser.safe_label_atom`), doesn't change any SAT-call count.

Two paths are timed, once each (for repeated timings use
`python -m eccrs_workbench.baseline`):

- **naive**:     `naive.query`, the published ascending scan, once per complete pattern
                 (2^a of them);
- **optimised**: the shipped `rational_closure.query` plus the applicable-rule-set
                 collapse (`report.collapse_patterns`), once per class.

SAT calls are the main metric and wall-clock is secondary. Agreement
is raw counts (n, agree, disagree, both-abstain), with abstention in its own column.
The percentage is (agree + both-abstain) / n, same as `evaluate.population_stats`.
"""

from __future__ import annotations

import argparse
import html
import itertools
import os
import re
import sys
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from . import msw, naive, rational_closure, report, validator
from .base_rank import INFINITY, RankedKB, base_rank
from .evaluate import population_stats, realisable_stats
from .explanation import explain
from .model import Body, RuleSet, is_realisable, one_hot_families
from .parser import parse_rules, read_instances_csv, safe_label_atom, to_body
from .sat import count_calls

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = REPO_ROOT / "datasets"
DEFAULT_HTML_DIR = Path("demo-output")

MODES = ("naive", "optimised", "both")


class DemoError(Exception):
    """A problem we should see as a single clear line"""


# finding the dataset


@dataclass(frozen=True)
class Target:
    name: str
    rules_path: Path
    csv_path: Path | None  # None: no instance set, so only the pattern space is run


def discover_datasets(root: Path | None = None) -> list[Path]:
    root = DATASETS_DIR if root is None else root
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and (p / "rules.txt").is_file())


def _target_for_folder(folder: Path) -> Target:
    rules = folder / "rules.txt"
    if not rules.is_file():
        raise DemoError(f"{folder} has no rules.txt, so it is not a dataset folder")
    csv_path = folder / "instances.csv"
    return Target(folder.name, rules, csv_path if csv_path.is_file() else None)


def resolve_target(arg: str) -> Target:
    path = Path(arg)
    if path.is_file():
        # A bare ruleset, e.g. tests/fixtures/scholarship.rules.txt: no instance set.
        return Target(path.name.removesuffix(".txt").removesuffix(".rules"), path, None)
    if path.is_dir():
        return _target_for_folder(path)
    if (DATASETS_DIR / arg).is_dir():
        return _target_for_folder(DATASETS_DIR / arg)
    raise DemoError(f"no dataset folder or rules file called {arg!r}")


def choose_dataset() -> str:
    found = discover_datasets()
    if not found:
        raise DemoError(f"no dataset folders with a rules.txt under {DATASETS_DIR}")
    print("Datasets:")
    for number, folder in enumerate(found, start=1):
        print(f"  {number}) {folder.name}")
    try:
        answer = input("Which one? (number or name) ").strip()
    except EOFError:
        raise DemoError("no dataset chosen") from None
    if answer.isdigit() and 1 <= int(answer) <= len(found):
        return str(found[int(answer) - 1])
    if any(answer == folder.name for folder in found):
        return answer
    raise DemoError(f"{answer!r} is not one of the {len(found)} datasets listed")


@dataclass(frozen=True)
class ModeRun:
    mode: str  # "naive" or "optimised"
    pattern_units: int  # patterns (naive) or applicable-rule-set classes (optimised)
    pattern_calls: int
    pattern_seconds: float
    pattern_space: dict  # n / agree / disagree / both_abstain / agreement_pct
    realisable: dict  # the same, over the realisable subset of the pattern space
    instances: dict | None  # the same over the CSV instances; None without a CSV
    instance_calls: int
    instance_seconds: float

    @property
    def unit_name(self) -> str:
        return "patterns" if self.mode == "naive" else "classes"


@dataclass(frozen=True)
class DemoResult:
    name: str
    rules: int
    rule_atoms: int
    instance_count: int | None
    violations: dict[str, list[str]]  # condition -> violation details ([] = holds)
    rank_levels: list[tuple[str, list[str]]]  # ("0", ["r1", ...]) ... ("inf", [...])
    base_rank_calls: int
    runs: dict[str, ModeRun]
    divergences: list[tuple[str, Body]]
    traces: list[str]


def _clear_caches() -> None:
    # Start every timed pass with cold caches, like baseline.measure, so no mode gets
    # help from queries another pass already answered.
    rational_closure.base_rank_of.cache_clear()
    rational_closure.query.cache_clear()


def _class_stats(classes: report.ClassAgreement, *, realisable: bool = False) -> dict:
    def weight(c: report.PatternClass) -> int:
        return c.realisable if realisable else c.count

    n = sum(weight(c) for c in classes.classes)
    both = sum(weight(c) for c in classes.classes if c.msw_label is c.rc_label is None)
    agree = sum(
        weight(c) for c in classes.classes if c.agrees and c.msw_label is not None
    )
    return {
        "n": n,
        "agree": agree,
        "disagree": n - agree - both,
        "both_abstain": both,
        "agreement_pct": (agree + both) / n if n else 1.0,
    }


def _naive_rows(
    ranked: RankedKB,
    ruleset: RuleSet,
    label_atom,
    items: Iterator[tuple[str, Body, int | None, bool]],
) -> report.Agreement:
    rows = []
    for key, pattern, truth, realisable in items:
        verdict = naive.query(ranked, pattern, label_atom)
        rows.append(
            report.Row(
                key,
                pattern,
                msw.predict(ruleset, pattern),
                verdict.label,
                not verdict.possible,
                truth,
                realisable,
            )
        )
    return report.Agreement("naive", tuple(rows))


@dataclass(frozen=True)
class _Pass:
    run: ModeRun
    instance_rows: tuple[report.Row, ...]
    pattern_divergences: list[tuple[str, Body]]


def _timed(work):
    with count_calls() as counter:
        start = time.perf_counter()
        value = work()
        seconds = time.perf_counter() - start
    return value, counter.calls, seconds


def _instance_pass(run_instances, has_instances):
    if not has_instances:
        return None, 0, 0.0, ()
    agreement, calls, seconds = _timed(run_instances)
    return population_stats(agreement), calls, seconds, agreement.rows


def _run_naive(ruleset, ranked, label_atom, instances, truths) -> _Pass:
    families = one_hot_families(ruleset.atoms)
    patterns = (
        (f"p{i}", pattern, None, is_realisable(pattern, families))
        for i, pattern in enumerate(report.complete_patterns(ruleset.atoms))
    )
    _clear_caches()
    space, pattern_calls, pattern_seconds = _timed(
        lambda: _naive_rows(ranked, ruleset, label_atom, patterns)
    )
    stats, calls, seconds, rows = _instance_pass(
        lambda: _naive_rows(
            ranked,
            ruleset,
            label_atom,
            (
                (str(i), to_body(values, ruleset.atoms), truths.get(i), True)
                for i, values in instances.items()
            ),
        ),
        bool(instances),
    )
    run = ModeRun(
        "naive",
        len(space.rows),
        pattern_calls,
        pattern_seconds,
        population_stats(space),
        realisable_stats(space),
        stats,
        calls,
        seconds,
    )
    return _Pass(run, rows, [(row.key, row.pattern) for row in space.divergences])


def _run_optimised(ruleset, ranked, instances, truths) -> _Pass:
    _clear_caches()
    classes, pattern_calls, pattern_seconds = _timed(
        lambda: report.collapse_patterns(ruleset, ranked)
    )

    def over_instances() -> report.Agreement:
        _clear_caches()
        return report.over_instances(ruleset, ranked, instances, truths=truths)

    stats, calls, seconds, rows = _instance_pass(over_instances, bool(instances))
    run = ModeRun(
        "optimised",
        len(classes.classes),
        pattern_calls,
        pattern_seconds,
        _class_stats(classes),
        _class_stats(classes, realisable=True),
        stats,
        calls,
        seconds,
    )
    divergent = [
        (f"c{i}", c.representative) for i, c in enumerate(classes.classes) if not c.agrees
    ]
    return _Pass(run, rows, divergent)


def _natural_key(rule_id: str) -> tuple:
    return tuple(int(t) if t.isdigit() else t for t in re.split(r"(\d+)", rule_id))


def _rank_levels(ranked: RankedKB) -> list[tuple[str, list[str]]]:
    return [
        (
            "inf" if rank == INFINITY else str(rank),
            sorted((c.source_rule_id for c in ranked.at_rank(rank)), key=_natural_key),
        )
        for rank in ranked.order
    ]


def _candidate_patterns(
    ruleset: RuleSet, divergences, instance_rows
) -> Iterator[tuple[str, Body]]:
    """Traces worth showing, in order: divergences; then cases where a more specific
    rule overrides another (applicable set bigger than the maximal set); then the
    first instance / pattern."""
    yield from divergences

    instances = [(row.key, row.pattern) for row in instance_rows]
    everything = itertools.chain(
        instances,
        ((f"p{i}", p) for i, p in enumerate(report.complete_patterns(ruleset.atoms))),
    )
    for key, pattern in everything:
        applicable = msw.applicable(ruleset, pattern)
        if len(msw.maximal(applicable)) < len(applicable):
            yield key, pattern
    yield from instances[:1]
    yield from (
        (f"p{i}", p)
        for i, p in enumerate(
            itertools.islice(report.complete_patterns(ruleset.atoms), 1)
        )
    )


def _choose_traces(ruleset, ranked, divergences, instance_rows, count) -> list[str]:
    traces: list[str] = []
    seen: set[Body] = set()
    if count <= 0:
        return traces
    for key, pattern in _candidate_patterns(ruleset, divergences, instance_rows):
        if pattern in seen:
            continue
        seen.add(pattern)
        traces.append(explain(ruleset, ranked, pattern, key))
        if len(traces) == count:
            break
    return traces


def analyse(target: Target, mode: str = "both", traces: int = 2) -> DemoResult:
    if mode not in MODES:
        raise DemoError(f"mode must be one of {', '.join(MODES)}")
    ruleset = parse_rules(target.rules_path)
    if len(ruleset.atoms) > report.MAX_PATTERN_ATOMS:
        raise DemoError(
            f"{len(ruleset.atoms)} rule atoms is beyond the "
            f"{report.MAX_PATTERN_ATOMS}-atom cap on exhaustive pattern enumeration"
        )

    instances: dict = {}
    truths: dict = {}
    if target.csv_path is not None:
        instances, truths = read_instances_csv(target.csv_path)

    label_atom = safe_label_atom(ruleset, instances)
    _clear_caches()
    with count_calls() as counter:
        ranked = base_rank(ruleset.to_kb(label_atom))

    violations = {
        "sanity": [v.detail for v in validator.check_sanity(ruleset)],
        "strict closure": [v.detail for v in validator.check_strict_closure(ruleset)],
        "no total override": [
            v.detail for v in validator.check_no_total_override(ruleset)
        ],
    }

    passes: dict[str, _Pass] = {}
    if mode in ("naive", "both"):
        passes["naive"] = _run_naive(ruleset, ranked, label_atom, instances, truths)
    if mode in ("optimised", "both"):
        passes["optimised"] = _run_optimised(ruleset, ranked, instances, truths)

    # Divergences and instance rows come from one pass (the optimised one if it ran) so
    # a divergence isn't listed once per mode.
    reference = passes["optimised" if "optimised" in passes else "naive"]
    instance_rows = reference.instance_rows
    divergences = list(reference.pattern_divergences)
    divergences += [(row.key, row.pattern) for row in instance_rows if not row.agrees]

    return DemoResult(
        name=target.name,
        rules=len(ruleset.rules),
        rule_atoms=len(ruleset.atoms),
        instance_count=len(instances) if target.csv_path is not None else None,
        violations=violations,
        rank_levels=_rank_levels(ranked),
        base_rank_calls=counter.calls,
        runs={mode: p.run for mode, p in passes.items()},
        divergences=divergences,
        traces=_choose_traces(ruleset, ranked, divergences, instance_rows, traces),
    )


# rendering: one document of blocks, two renderers

Cell = str | tuple[str, str]  # text, or (text, style)


def _speedup(result: DemoResult) -> str | None:
    if not {"naive", "optimised"} <= set(result.runs):
        return None
    slow, fast = result.runs["naive"], result.runs["optimised"]
    calls = (
        f"{slow.pattern_calls / fast.pattern_calls:.1f}x" if fast.pattern_calls else "n/a"
    )
    secs = (
        f"{slow.pattern_seconds / fast.pattern_seconds:.1f}x"
        if fast.pattern_seconds
        else "n/a"
    )
    return (
        f"Speed-up over the pattern space: SAT calls {slow.pattern_calls} -> "
        f"{fast.pattern_calls} ({calls}), wall-clock {slow.pattern_seconds:.3f}s -> "
        f"{fast.pattern_seconds:.3f}s ({secs})"
    )


def _pct(stats: dict) -> Cell:
    text = f"{stats['agreement_pct']:.1%}"
    return (text, "good" if stats["disagree"] == 0 else "fail")


def _comparison_rows(result: DemoResult) -> list[list[Cell]]:
    rows: list[list[Cell]] = []
    for run in result.runs.values():
        space = f"pattern space (2^{result.rule_atoms})"
        for population, stats, evaluated, calls, seconds in (
            (
                space,
                run.pattern_space,
                f"{run.pattern_units} {run.unit_name}",
                str(run.pattern_calls),
                f"{run.pattern_seconds:.3f}s",
            ),
            ("  realisable subset", run.realisable, "-", "-", "-"),
            (
                "CSV instances",
                run.instances,
                None if run.instances is None else f"{run.instances['n']} instances",
                str(run.instance_calls),
                f"{run.instance_seconds:.3f}s",
            ),
        ):
            if stats is None:
                continue
            rows.append(
                [
                    run.mode,
                    population,
                    evaluated,
                    calls,
                    seconds,
                    str(stats["n"]),
                    str(stats["agree"]),
                    str(stats["disagree"]),
                    str(stats["both_abstain"]),
                    _pct(stats),
                ]
            )
    return rows


COMPARISON_HEADERS = [
    "mode",
    "population",
    "evaluated",
    "SAT calls",
    "time",
    "n",
    "agree",
    "disagree",
    "both-abstain",
    "agreement",
]


def build_blocks(result: DemoResult) -> list[tuple]:
    counts = f"{result.rules} rules, {result.rule_atoms} rule atoms"
    if result.instance_count is not None:
        counts += f", {result.instance_count} CSV instances"
    blocks: list[tuple] = [
        ("title", f"ECCRS workbench demo: {result.name}"),
        ("line", counts),
    ]

    blocks.append(("heading", "Validation (alignment-theorem conditions)"))
    for condition, details in result.violations.items():
        if not details:
            blocks.append(("line", (("PASS", "good"), f"  {condition}")))
        for detail in details:
            blocks.append(("line", (("FAIL", "fail"), f"  {condition}: {detail}")))
    if any(result.violations.values()):
        blocks.append(
            ("line", "The alignment guarantee does not apply; continuing anyway.")
        )

    blocks.append(
        ("heading", f"BaseRank (one-off cost: {result.base_rank_calls} SAT calls)")
    )
    for rank, ids in result.rank_levels:
        blocks.append(("line", f"  rank {rank}: {', '.join(ids)}"))

    blocks.append(("heading", "Comparison"))
    blocks.append(("table", COMPARISON_HEADERS, _comparison_rows(result)))
    blocks.append(("line", ""))
    blocks.append(("line", "agreement = (agree + both-abstain) / n"))
    blocks.append(
        (
            "line",
            "pattern space = every complete assignment over the rule atoms; "
            "realisable = those one-hot encoding allows",
        )
    )
    speedup = _speedup(result)
    if speedup:
        blocks.append(("line", ((speedup, "good"),)))

    if result.traces:
        blocks.append(("heading", "Explanation traces"))
        blocks += [("pre", trace) for trace in result.traces]
    return blocks


def _styled(text: str, style: str | None, color: bool) -> str:
    codes = {"good": "32;1", "fail": "31;1", "head": "36;1", "dim": "2"}
    if not color or style not in codes:
        return text
    return f"\x1b[{codes[style]}m{text}\x1b[0m"


def _line_text(content, color: bool) -> str:
    if isinstance(content, str):
        return content
    return "".join(
        _styled(*part, color) if isinstance(part, tuple) else part for part in content
    )


def _trace_style(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("=> AGREE"):
        return "good"
    if stripped.startswith("=> DIVERGE"):
        return "fail"
    return None


def _table_text(headers, rows, color: bool) -> list[str]:
    cells = [[c if isinstance(c, tuple) else (c, None) for c in row] for row in rows]
    widths = [
        max(len(headers[i]), *(len(row[i][0]) for row in cells))
        for i in range(len(headers))
    ]

    def fmt(index: int, text: str, style: str | None) -> str:
        padded = text.ljust(widths[index]) if index < 2 else text.rjust(widths[index])
        return _styled(padded, style, color)

    lines = ["  ".join(fmt(i, h, "dim") for i, h in enumerate(headers)).rstrip()]
    lines.append("  ".join("-" * w for w in widths))
    for row in cells:
        lines.append("  ".join(fmt(i, t, s) for i, (t, s) in enumerate(row)).rstrip())
    return lines


def render_text(result: DemoResult, color: bool = False) -> str:
    out: list[str] = []
    for block in build_blocks(result):
        kind = block[0]
        if kind == "title":
            out += [_styled(block[1], "head", color), ""]
        elif kind == "heading":
            out += ["", _styled(f"== {block[1]} ==", "head", color)]
        elif kind == "line":
            out.append(_line_text(block[1], color))
        elif kind == "table":
            out += _table_text(block[1], block[2], color)
        elif kind == "pre":
            out.append("")
            out += [
                _styled(line, _trace_style(line), color) for line in block[1].splitlines()
            ]
    return "\n".join(out)


HTML_STYLE = """
body{font-family:Segoe UI,Helvetica,Arial,sans-serif;margin:2rem auto;max-width:70rem;
padding:0 1rem;color:#1b1b1b;background:#fff}
h1{font-size:1.5rem}h2{font-size:1.1rem;margin-top:1.6rem;border-bottom:1px solid #bbb}
table{border-collapse:collapse;font-size:.9rem}
th,td{border:1px solid #ccc;padding:.25rem .6rem;text-align:right}
th:nth-child(-n+2),td:nth-child(-n+2){text-align:left}
th{background:#f0f0f0}pre{background:#f6f6f6;border:1px solid #ddd;padding:.7rem;
overflow-x:auto;font-size:.85rem}
.good{color:#0a6b1f;font-weight:bold}.fail{color:#b00020;font-weight:bold}
"""


def _span(text: str, style: str | None) -> str:
    escaped = html.escape(text)
    return f'<span class="{style}">{escaped}</span>' if style else escaped


def render_html(result: DemoResult) -> str:
    body: list[str] = []
    for block in build_blocks(result):
        kind = block[0]
        if kind == "title":
            body.append(f"<h1>{html.escape(block[1])}</h1>")
        elif kind == "heading":
            body.append(f"<h2>{html.escape(block[1])}</h2>")
        elif kind == "line":
            content = block[1]
            parts = [content] if isinstance(content, str) else list(content)
            rendered = "".join(
                _span(*p) if isinstance(p, tuple) else html.escape(p) for p in parts
            )
            body.append(f"<p>{rendered}</p>")
        elif kind == "table":
            head = "".join(f"<th>{html.escape(h)}</th>" for h in block[1])
            rows = "".join(
                "<tr>"
                + "".join(
                    f"<td>{_span(*c) if isinstance(c, tuple) else html.escape(c)}</td>"
                    for c in row
                )
                + "</tr>"
                for row in block[2]
            )
            body.append(f"<table><tr>{head}</tr>{rows}</table>")
        elif kind == "pre":
            lines = "\n".join(
                _span(line, _trace_style(line)) for line in block[1].splitlines()
            )
            body.append(f"<pre>{lines}</pre>")
    return (
        '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
        f"<title>{html.escape(result.name)} - ECCRS workbench demo</title>"
        f"<style>{HTML_STYLE}</style></head><body>\n"
        + "\n".join(body)
        + "\n</body></html>\n"
    )


# colour and the command line


def _enable_windows_vt() -> bool:
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False


def use_color(no_color_flag: bool, stream=None) -> bool:
    """Colour only on a real terminal that can render it: never into a pipe, never with
    --no-color or NO_COLOR set, and never if Windows will not enable VT mode."""
    stream = sys.stdout if stream is None else stream
    if no_color_flag or os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    if not getattr(stream, "isatty", lambda: False)():
        return False
    return _enable_windows_vt()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eccrs_workbench.demo", description=__doc__)
    parser.add_argument(
        "dataset",
        nargs="?",
        help="a folder under datasets/ (cancer), a path (datasets/bank), or a bare "
        "rules file; omitted: pick from a numbered list",
    )
    parser.add_argument("--mode", choices=MODES, default="both")
    parser.add_argument(
        "--traces", type=int, default=2, help="explanation traces to print"
    )
    parser.add_argument("--list", action="store_true", help="list the datasets and exit")
    parser.add_argument("--no-color", action="store_true", help="never use ANSI colour")
    parser.add_argument(
        "--html",
        nargs="?",
        const="",
        metavar="PATH",
        help="also write one self-contained HTML file "
        "(default demo-output/<dataset>.html)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.list:
            for number, folder in enumerate(discover_datasets(), start=1):
                print(f"  {number}) {folder.name}")
            return 0

        html_path = args.html
        dataset = args.dataset
        if (
            dataset is None
            and html_path
            and not html_path.lower().endswith((".html", ".htm"))
        ):
            # `--html cancer`: argparse read the dataset as the output path.
            dataset, html_path = html_path, ""

        target = resolve_target(dataset if dataset is not None else choose_dataset())
        result = analyse(target, args.mode, args.traces)
    except DemoError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(render_text(result, use_color(args.no_color)))

    if html_path is not None:
        path = Path(html_path) if html_path else DEFAULT_HTML_DIR / f"{result.name}.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_html(result), encoding="utf-8")
        print(f"\nHTML written to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
