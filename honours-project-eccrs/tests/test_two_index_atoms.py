"""Two-index atoms: one-hot bins a(i,j) next to plain indicators a(i).

Cancer is all single-index, bank all two-index, and mushroom mixes both in one rule.
`_LITERAL` used to match only `a(i)=v`, so bank raised on line 1 ("rule has no
conditions") and mushroom parsed rules 0-6 with silently truncated bodies before
rule 7 raised.

A dropped literal means a wrong atom, and that gives plausible numbers that are
wrong. So we pin two things: every literal shape parses, and a conjunct that doesn't
parse is an error, not a silent drop.
"""

import pytest

from eccrs_workbench.model import atom
from eccrs_workbench.parser import parse_instances, parse_rules


def _rules(tmp_path, text):
    path = tmp_path / "r.rules.txt"
    path.write_text(text)
    return parse_rules(path)


def test_two_index_literals_parse_into_the_body(tmp_path):
    """Bank rule 0 shape: every literal is a(i,j)."""
    ruleset = _rules(tmp_path, "0: IF a(15,9)=0 & a(16,3)=1 & a(4,1)=0 THEN y=1\n")
    (rule,) = ruleset.rules
    assert rule.body == frozenset(
        {(atom(15, 9), False), (atom(16, 3), True), (atom(4, 1), False)}
    )
    assert rule.label == 1


def test_a_mixed_rule_keeps_every_literal(tmp_path):
    """Mushroom rule 0 shape: four two-index bins and one plain indicator, one rule."""
    ruleset = _rules(
        tmp_path,
        "0: IF a(12,2)=0 & a(18,5)=0 & a(3,9)=0 & a(5,7)=1 & a(8)=1 THEN y=0\n",
    )
    (rule,) = ruleset.rules
    assert rule.body == frozenset(
        {
            (atom(12, 2), False),
            (atom(18, 5), False),
            (atom(3, 9), False),
            (atom(5, 7), True),
            (atom(8), True),
        }
    )


def test_atom_identity_is_stable_across_parses(tmp_path):
    text = "0: IF a(4,1)=1 & a(8)=0 THEN y=1\n"
    first = _rules(tmp_path, text)
    second = _rules(tmp_path, text)
    assert first.rules[0].body == second.rules[0].body
    assert set(first.atoms) == set(second.atoms) == {atom(4, 1), atom(8)}


def test_one_hot_bins_of_one_attribute_are_distinct_atoms(tmp_path):
    ruleset = _rules(tmp_path, "0: IF a(4,1)=1 & a(4,2)=0 THEN y=1\n")
    (rule,) = ruleset.rules
    assert atom(4, 1) != atom(4, 2)
    assert len(rule.body) == 2
    assert ruleset.atoms == frozenset({atom(4, 1), atom(4, 2)})


def test_indicator_and_bin_with_the_same_index_are_distinct_atoms(tmp_path):
    ruleset = _rules(tmp_path, "0: IF a(4)=1 & a(4,1)=0 THEN y=1\n")
    (rule,) = ruleset.rules
    assert atom(4) != atom(4, 1)
    assert len(rule.body) == 2
    assert ruleset.atoms == frozenset({atom(4), atom(4, 1)})


def test_a_conjunct_that_does_not_parse_is_an_error_never_a_silent_drop(tmp_path):
    """The mushroom regression. `a(9,)=0` is not a well-formed literal; the old
    findall approach would drop it (and `a(5,7)=1`) and keep only `a(8)=1`."""
    with pytest.raises(ValueError, match="literal"):
        _rules(tmp_path, "0: IF a(5,7)=1 & a(9,)=0 & a(8)=1 THEN y=0\n")


def test_a_repeated_atom_in_one_body_is_an_error(tmp_path):
    with pytest.raises(ValueError, match="duplicate|contradict|collaps"):
        _rules(tmp_path, "0: IF a(4,1)=1 & a(4,1)=0 THEN y=1\n")


def test_instances_parse_two_index_facts_with_the_same_identity(tmp_path):
    """parse_instances must assign the identity parse_rules does, or the projection
    in report.over_instances silently misaligns."""
    path = tmp_path / "d.lp"
    path.write_text("val(1,a(4,1),1).\nval(1,a(8),0).\nval(2,a(4,2),1).\n")
    instances = parse_instances(path)
    assert instances == {1: {atom(4, 1): 1, atom(8): 0}, 2: {atom(4, 2): 1}}


def test_instances_reject_an_unparseable_fact_line(tmp_path):
    path = tmp_path / "d.lp"
    path.write_text("val(1,a(4,1),1).\nval(1,a(9,),0).\n")
    with pytest.raises(ValueError, match="val/3|fact"):
        parse_instances(path)
