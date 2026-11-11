ECCRS Workbench Package  --  bank

Learned ECCRS rules for the bank dataset, a set of test
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
      The 21 ECCRS rules learned on the full bank training set.
      Each rule has: idx, label (0 or 1), body (feature=value conditions),
      support, correct, and a human-readable rule_str.

  rules.txt
      The same rules as  IF ... THEN y=0/1,  one per line.
      Rule numbers match rules.json.

  instances.csv
      11303 test instances (a 25% stratified holdout from the full dataset).
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

  data-bank.lp
      Original .lp dataset file showing how raw data maps to feature atoms.

FEATURE NAMES
-------------
Each feature column is named a(i,j), where i is the original
attribute number and j is the value bin. This is a one-hot encoding:
for a given attribute i, exactly one bin j will be 1 and the rest
will be 0. For example, if attribute 3 has four possible values, you
will see columns a(3,1), a(3,2), a(3,3), a(3,4), and exactly one of
them is 1 for each instance.

The column y is the target label (0 or 1). It corresponds to the
last attribute in data-bank.lp (the highest-numbered a(k) entry).
