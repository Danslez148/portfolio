ECCRS Workbench Package  --  Breast Cancer Dataset

Learned ECCRS rules for the cancer dataset, a set of test
instances, and the ECCRS MSW predictions for each instance.

ASSUMPTION CHECK
----------------
  strict_global_closure : HOLDS
  sanity                : HOLDS
  no_total_override     : HOLDS
  All three hold        : YES

FILES BREAKDOWN
-----
  rules.json
      The 12 ECCRS rules learned on the full cancer training set.
      Each rule has: idx, label (0 or 1), body (feature=value conditions),
      support, correct, and a human-readable rule_str.

  rules.txt
      The same rules as  IF ... THEN y=0/1,  one per line.
      Rule numbers match rules.json.

  instances.csv
      175 test instances (a 25% stratified holdout from the full dataset).
      Columns: instance_id, one column per feature atom, then y.
      y is the true target label (0 or 1). Every feature value is 0 or 1.

  msw_predictions.csv
      The ECCRS Most-Specific-Wins prediction for each instance.
      Key columns:
        y_true                  : true label
        msw_pred                : ECCRS decision: 0, 1, or abstain
        applicable_rule_indices : all rules whose conditions are met
        maximal_rule_indices    : the most specific applicable rules
                                   (these are the ones that decide)

  assumptions.json
      Whether the three alignment assumptions hold for this ruleset.

  data-cancer.lp
      Original .lp dataset file showing how raw data maps to feature atoms.

FEATURE NAMES
-------------
Each feature column is named a(i), where i is the original attribute
number. These are straight binary indicators: 1 means the attribute
is present or true, 0 means it is not.

The column y is the target label (0 or 1). It corresponds to the
last attribute in data-cancer.lp (the highest-numbered a(k) entry).

