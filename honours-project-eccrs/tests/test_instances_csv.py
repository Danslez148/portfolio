"""The CSV instance reader, next to the ASP val/3 .lp reader.

The upstream packages ship instances.csv: instance_id, one column per feature atom,
then y (the true label). Headers are atom names, and two-index names contain commas,
so they are quoted: `instance_id,"a(1,1)","a(1,2)",a(10),...,y`. A plain split(",")
would mangle every two-index column (the same bug as in the ruleset parser), so we
use the csv module.

y is the ground truth, which replaces infer_class_atom's "highest atom id" guess for
CSV inputs. infer_class_atom is still used for .lp inputs.
"""

import pytest

from eccrs_workbench.model import atom
from eccrs_workbench.parser import parse_rules, read_instances_csv


def _csv(tmp_path, text):
    path = tmp_path / "instances.csv"
    path.write_text(text)
    return path


def test_reads_instance_ids_feature_columns_and_labels(tmp_path):
    path = _csv(
        tmp_path,
        "instance_id,a(1),a(2),y\n" "7,1,0,1\n" "8,0,0,0\n",
    )
    instances, labels = read_instances_csv(path)
    assert instances == {7: {atom(1): 1, atom(2): 0}, 8: {atom(1): 0, atom(2): 0}}
    assert labels == {7: 1, 8: 0}


def test_quoted_two_index_headers_are_not_split_on_the_embedded_comma(tmp_path):
    """The critical case: "a(1,2)" is one column, not two."""
    path = _csv(
        tmp_path,
        'instance_id,"a(1,1)","a(1,2)",a(10),y\n' "3,1,0,1,1\n",
    )
    instances, labels = read_instances_csv(path)
    assert instances == {3: {atom(1, 1): 1, atom(1, 2): 0, atom(10): 1}}
    assert labels == {3: 1}


def test_csv_column_and_rule_literal_for_one_atom_resolve_to_the_same_id(tmp_path):
    rule_path = tmp_path / "r.rules.txt"
    rule_path.write_text("0: IF a(1,2)=1 & a(10)=0 THEN y=1\n")
    ruleset = parse_rules(rule_path)

    path = _csv(tmp_path, 'instance_id,"a(1,2)",a(10),y\n5,1,0,1\n')
    instances, _ = read_instances_csv(path)

    assert ruleset.atoms == {atom(1, 2), atom(10)}
    assert ruleset.atoms <= set(instances[5])  # same tuple ids, not just same names


def test_y_is_the_label_not_a_feature_atom(tmp_path):
    path = _csv(tmp_path, "instance_id,a(1),y\n1,1,0\n")
    instances, labels = read_instances_csv(path)
    assert set(instances[1]) == {atom(1)}
    assert ("y", 0) not in instances[1].items()
    assert labels[1] == 0


def test_values_are_ints(tmp_path):
    path = _csv(tmp_path, "instance_id,a(1),y\n1,1,0\n")
    instances, labels = read_instances_csv(path)
    assert instances[1][atom(1)] == 1 and isinstance(instances[1][atom(1)], int)
    assert labels[1] == 0 and isinstance(labels[1], int)


def test_a_header_that_is_not_instance_id_y_or_an_atom_name_raises(tmp_path):
    path = _csv(tmp_path, "instance_id,a(1),junk,y\n1,1,1,0\n")
    with pytest.raises(ValueError, match="header|column"):
        read_instances_csv(path)


def test_a_missing_y_column_raises(tmp_path):
    path = _csv(tmp_path, "instance_id,a(1),a(2)\n1,1,0\n")
    with pytest.raises(ValueError, match="y"):
        read_instances_csv(path)


def test_row_order_is_preserved(tmp_path):
    path = _csv(tmp_path, "instance_id,a(1),y\n30,1,1\n10,0,0\n20,1,0\n")
    instances, _ = read_instances_csv(path)
    assert list(instances) == [30, 10, 20]


# -- The three real upstream CSVs. Counts are fixed; do not adjust them to fit.
#    Cancer's CSV is a 25% stratified holdout (175), NOT the 699 of data-cancer.lp.


@pytest.mark.parametrize(
    "name, n_instances",
    [("cancer", 175), ("mushroom", 2031), ("bank", 11303)],
)
def test_real_csv_loads_with_the_expected_row_count_and_matching_atom_ids(
    name, n_instances
):
    from tests.examples import REPO

    ruleset = parse_rules(REPO / "datasets" / name / "rules.txt")
    instances, labels = read_instances_csv(REPO / "datasets" / name / "instances.csv")

    assert len(instances) == n_instances
    assert len(labels) == n_instances
    assert set(labels.values()) == {0, 1}

    csv_atoms = {a for values in instances.values() for a in values}
    assert ruleset.atoms <= csv_atoms  # every rule atom is a CSV column, same id
