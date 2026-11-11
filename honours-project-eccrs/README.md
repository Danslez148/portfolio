# ECCRS Rational Closure Workbench

Code for my UCT Computer Science honours project (CSC4002W), *Explanation Using Defeasible
Rulesets: Verifying ECCRS Predictions with Rational Closure*.

An ECCRS (Exception Closed Conjunctive Rule Set) classifier predicts with Most Specific
Wins (MSW): out of the rules that apply to an instance, the most specific ones decide the
label, and it abstains if none apply. An alignment theorem says MSW agrees exactly with
Rational Closure (RC) over the matching KLM knowledge base, as long as the ruleset has
strict global exception closure, sanity and no total override. This workbench checks those
three conditions, does the translation, implements RC from scratch, and measures how often
the two agree.

Daniel Schlesinger (SCHDAN066). Lexicographic Closure and System W are built by two other
students on the same BaseRank. Their code and results are not in this repo.

## What it does

1. **Validate** the three conditions on a ruleset.
2. **Translate** each rule `(B, l)` into one conditional `B |~ m` or `B |~ ~m`, with a fresh
   label atom `m`.
3. **Rank** the knowledge base with BaseRank, then answer queries with RC entailment.
4. **Compare** RC against MSW, over the dataset instances and over every complete feature
   pattern, and print a two-sided explanation trace (the ECCRS chain next to the RC rank
   comparison).

MSW is evaluated directly on the ruleset and never sees the translation, so it stays an
independent check on the RC side. There are no runtime dependencies: the SAT solver (a
plain DPLL) is written from scratch too.

## Running it

Python 3.10 or newer. Only the dev tools need installing:

```bash
pip install pytest black ruff
```

Run everything from the repo root, either after `pip install -e .` or with `src` on the
path (`PYTHONPATH=src` in bash, `$env:PYTHONPATH = "src"` in PowerShell).

**The demo** compares the naive and the optimised RC procedure on one dataset folder:

```bash
python -m eccrs_workbench.demo                  # lists the datasets and asks which one
python -m eccrs_workbench.demo cancer           # or bank, mushroom, or a path
python -m eccrs_workbench.demo bank --mode optimised --traces 3
python -m eccrs_workbench.demo cancer --html    # also writes demo-output/cancer.html
python -m eccrs_workbench.demo tests/fixtures/scholarship.rules.txt
```

It reads `rules.txt` and `instances.csv` (not the big `.lp` files) and reports SAT calls
first, wall-clock second, then n / agree / disagree / both-abstain as separate columns.
Colour turns itself off when the output is piped, or with `--no-color`. `--list` only lists
the datasets.

**The full CLI** runs all four phases:

```bash
python -m eccrs_workbench datasets/cancer/rules.txt datasets/cancer/data-cancer.lp
python -m eccrs_workbench datasets/bank/rules.txt --instances-csv datasets/bank/instances.csv
python -m eccrs_workbench tests/fixtures/scholarship.rules.txt
```

Instances are ASP `val/3` facts (`.lp`, class column guessed as the highest atom) or the
upstream `instances.csv` (`--instances-csv`, where `y` is the true label). Other options are
`--class-atom I[,J]` and `--traces N`. The exit status is non-zero if a condition is
violated, but the run carries on so you still see the comparison.

**The numbers for the paper** come from:

```bash
python -m eccrs_workbench.evaluate          # rules + instances.csv + pattern space
python -m eccrs_workbench.evaluate --full   # also the full .lp instance sets (slow)
python -m eccrs_workbench.baseline          # SAT-call and timing table, three procedures
```

## Results so far

Over every complete pattern on the ruleset's own atoms, and over the 25% stratified holdouts
(`instances.csv`), RC and MSW agree everywhere on the three learned rulesets. There are no
disagreements and no patterns where both abstain.

| Ruleset | Rules | Rule atoms | Patterns (2^a) | Realisable | Holdout instances | Disagreements |
|---|---|---|---|---|---|---|
| Breast Cancer Wisconsin | 12 | 6 | 64 | 64 | 175 | 0 |
| Mushroom | 13 | 10 | 1024 | 512 | 2031 | 0 |
| Bank Marketing | 21 | 14 | 16384 | 2880 | 11303 | 0 |

The scholarship ruleset breaks strict global exception closure on purpose. RC and MSW differ
on exactly one of its 32 patterns, the one the violation predicts.

SAT calls to cover the whole pattern space, by procedure:

| Ruleset | Naive ascending scan | Shipped binary search | Collapsed by applicable-rule set |
|---|---|---|---|
| Cancer | 360 | 400 | 64 |
| Mushroom | 5440 | 6144 | 66 |
| Bank | 92160 | 98304 | 102 |

The binary search costs more calls than the scan it replaced on all three rulesets, because
there are only three or four ranks. The collapse groups patterns by which rules they make
applicable and evaluates one representative per group, so it is exact. It still walks every
pattern once, so the 20-atom limit below still applies.

Two things to keep in mind when quoting a percentage:

- The 2^a pattern space includes patterns that cannot happen. Bank's `a(4,1)`, `a(4,2)`,
  `a(4,4)` and `a(4,5)` are one-hot bins of one attribute, so setting two of them is
  impossible. Both the full space and the realisable subset are reported, and a figure
  should always say which one it is over.
- "Agreement" counts both operators abstaining as agreement, as the theorem does. The raw
  counts are always shown separately.

Limits: three rulesets, all of which satisfy the conditions, so this shows the two
implementations agree and does not prove the theorem. `report.complete_patterns` refuses past
20 rule atoms instead of sampling.

## Layout

```
src/eccrs_workbench/   the workbench
  model.py             atoms, rules, conditionals, RuleSet.to_kb()
  parser.py            ruleset text, .lp facts and instances.csv
  sat.py               the DPLL solver, plus the SAT-call counter
  validator.py         the three conditions
  base_rank.py         BaseRank and the per-rank clause sets
  rational_closure.py  base rank of a formula, entailment, class queries
  msw.py               Most Specific Wins
  naive.py             the published ascending scan, for measurement only
  report.py            agreement over instances and over the pattern space
  explanation.py       two-sided traces
  baseline.py          SAT-call and timing measurements
  evaluate.py          the final evaluation run
  demo.py              the demo front end
  __main__.py          the CLI
tests/                 pytest; fixtures in tests/fixtures/
datasets/              cancer, bank, mushroom (rules, instances, upstream oracles)
```

## Datasets

`datasets/` holds three rulesets learned upstream by the ECCRS side of the project. Each
folder has `rules.txt`, `rules.json`, `instances.csv`, `msw_predictions.csv`,
`assumptions.json` and the original `data-*.lp` (16-18 MB for bank and mushroom).

`msw_predictions.csv` and `assumptions.json` come from a different implementation that uses
z3. `tests/test_upstream_oracles.py` compares against them, so agreement there is outside
evidence. A disagreement is something to look into, not something to loosen a test for.

Two format details matter:

- Atoms have two shapes. Cancer uses `a(i)`, bank uses `a(i,j)` throughout (attribute `i`,
  one-hot bin `j`), and mushroom mixes both, even inside one rule.
- Cancer has no `a(6)` (dropped upstream for missing values), and its class atom `a(10)` is
  1 for benign.

## Tests

```bash
python -m pytest tests/ -q
ruff check src tests
black --check src tests
```

The suite should be fully green. Most tests use small fixtures whose expected numbers can be
worked out by hand. `tests/test_rc_against_oracle.py` compares the whole ranking and
entailment stack against an independent naive implementation on random knowledge bases, and
any optimisation has to keep it passing.
