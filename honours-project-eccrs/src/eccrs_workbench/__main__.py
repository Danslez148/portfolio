"""CLI: validate, translate, rank, query, compare.

python -m eccrs_workbench datasets/cancer/rules.txt datasets/cancer/data-cancer.lp
python -m eccrs_workbench datasets/bank/rules.txt \
    --instances-csv datasets/bank/instances.csv
python -m eccrs_workbench tests/fixtures/scholarship.rules.txt

You can give instances as .lp or --instances-csv. The CSV's y column is the true
label, so the class isn't guessed.
"""

from __future__ import annotations

import argparse
import sys

from . import explanation, report, validator
from .base_rank import INFINITY, base_rank
from .model import Atom, format_atom
from .parser import (
    infer_class_atom,
    parse_instances,
    parse_rules,
    read_instances_csv,
    safe_label_atom,
)


def _atom_spec(text: str) -> Atom:
    try:
        return tuple(int(part) for part in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(f"not an atom: {text!r}") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eccrs_workbench", description=__doc__)
    parser.add_argument(
        "rules", help="ECCRS ruleset file (e.g. datasets/cancer/rules.txt)"
    )
    parser.add_argument("data", nargs="?", help="instances as ASP val/3 facts (.lp)")
    parser.add_argument(
        "--instances-csv",
        metavar="PATH",
        help="instances as upstream instances.csv (instance_id, feature columns, y); "
        "the y column is the ground truth, so --class-atom is not consulted",
    )
    parser.add_argument(
        "--class-atom",
        type=_atom_spec,
        metavar="I[,J]",
        help="atom holding the ground-truth class, e.g. 10 or 4,1 (default: highest). "
        "Ignored with --instances-csv.",
    )
    parser.add_argument("--traces", type=int, default=2, help="sample traces to print")
    args = parser.parse_args(argv)

    if args.instances_csv and args.data:
        parser.error("give either a .lp data file or --instances-csv, not both")

    ruleset = parse_rules(args.rules)
    if args.instances_csv:
        instances, truths = read_instances_csv(args.instances_csv)
    else:
        instances = parse_instances(args.data) if args.data else {}
        truths = None
    atom_list = ", ".join(format_atom(a) for a in sorted(ruleset.atoms))
    print(f"Ruleset: {len(ruleset.rules)} rules over atoms {atom_list}")

    print("\n== Phase 1: assumption validation ==")
    violations = validator.validate(ruleset)
    if not violations:
        print("  all three assumptions hold")
    for violation in violations:
        print(f"  VIOLATION [{violation.check}] {violation.detail}")
    if violations:
        # Warn and keep going. The theorem no longer promises agreement, so the
        # comparison below is worth seeing.
        print("  -> continuing anyway; the alignment guarantee does not apply")

    print("\n== Phase 2: translation ==")
    label_atom = safe_label_atom(ruleset, instances)
    kb = ruleset.to_kb(label_atom)
    print(
        f"  {len(kb.conditionals)} conditionals, "
        f"fresh label atom m = {format_atom(label_atom)}"
    )

    print("\n== Phase 3: BaseRank ==")
    ranked = base_rank(kb)
    for rank in ranked.order:
        ids = sorted(c.source_rule_id for c in ranked.at_rank(rank))
        print(f"  rank {'inf' if rank == INFINITY else rank}: {', '.join(ids)}")

    print("\n== Phase 4: agreement analysis ==")
    agreements = []
    if instances:
        if truths is not None:
            print(f"  {len(instances)} instances; ground truth from the CSV y column")
            agreements.append(
                report.over_instances(ruleset, ranked, instances, truths=truths)
            )
        else:
            class_atom = args.class_atom or infer_class_atom(instances)
            print(f"  ground-truth class taken from {format_atom(class_atom)}")
            agreements.append(
                report.over_instances(ruleset, ranked, instances, class_atom)
            )
    agreements.append(report.over_patterns(ruleset, ranked))
    print(report.render(agreements))

    if args.traces:
        print("\n== Explanation traces ==")
        rows = agreements[0].rows
        # Divergences first, since those are the interesting ones.
        chosen = list(agreements[0].divergences)[: args.traces]
        chosen += [row for row in rows if row.agrees][: args.traces - len(chosen)]
        for row in chosen:
            print(explanation.explain(ruleset, ranked, row.pattern, row.key), end="\n\n")

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
