"""The data model and the two input parsers.

Checks materialised_clauses() against the boat KB and the parser's rejection
paths.
"""

import pytest

from eccrs_workbench.model import atom, format_body, materialise, negate
from eccrs_workbench.parser import parse_rules, to_body
from tests.examples import BOAT, DUTCHMAN, FLOATS, LEAKY


def test_negate_is_an_involution():
    assert negate(negate((3, True))) == (3, True)
    assert negate((3, True)) == (3, False)


def test_materialised_clauses_of_the_boat_kb(boat_kb):
    assert set(boat_kb.materialised_clauses()) == {
        frozenset({(BOAT, False), (FLOATS, True)}),  # boat -> floats
        frozenset({(LEAKY, False), (BOAT, True)}),  # leaky -> boat
        frozenset({(LEAKY, False), (FLOATS, False)}),  # leaky -> -floats
        frozenset({(DUTCHMAN, False), (BOAT, True)}),  # FD -> boat
        frozenset({(DUTCHMAN, False), (LEAKY, True)}),  # FD -> leaky
    }
    assert boat_kb.materialised_clauses() == materialise(boat_kb.conditionals)


def test_translation_maps_labels_onto_the_fresh_atom(scholarship):
    kb = scholarship.to_kb()
    assert kb.label_atom not in scholarship.atoms
    by_rule = {c.source_rule_id: c.label for c in kb.conditionals}
    assert by_rule["r1"] == (kb.label_atom, True)  # label 1 -> m
    assert by_rule["r2"] == (kb.label_atom, False)  # label 0 -> ~m
    assert len(kb.conditionals) == len(scholarship.rules)  # exactly one per rule


def test_bodies_render_in_atom_order():
    body = frozenset({(atom(7), True), (atom(2), False), (atom(1), True)})
    names = {atom(1): "a1", atom(2): "a2", atom(7): "a7"}
    assert format_body(body, names) == "a1 & ~a2 & a7"


def test_two_index_atoms_sort_in_attribute_then_bin_order():
    body = frozenset(
        {(atom(4, 2), True), (atom(4, 1), False), (atom(4), True), (atom(3, 9), True)}
    )
    assert format_body(body, {}) == "a(3,9) & a(4) & ~a(4,1) & a(4,2)"


def test_parser_reads_signed_literals_and_labels(scholarship):
    rule = next(r for r in scholarship.rules if r.id == "r2")
    assert rule.body == frozenset({(atom(1), True), (atom(4), True)})
    assert rule.label == 0
    assert scholarship.atoms == {atom(1), atom(2), atom(3), atom(4), atom(5)}


def test_parser_rejects_duplicate_rule_ids(tmp_path):
    path = tmp_path / "dupes.rules.txt"
    path.write_text("x: IF a(1)=1 THEN y=1\nx: IF a(2)=1 THEN y=0\n")
    with pytest.raises(ValueError, match="duplicate rule ids"):
        parse_rules(path)


def test_parser_rejects_malformed_lines(tmp_path):
    path = tmp_path / "bad.rules.txt"
    path.write_text("x: IF a(1)=1 THEN maybe\n")
    with pytest.raises(ValueError, match="cannot parse rule"):
        parse_rules(path)


def test_parser_skips_comments_and_blank_lines(tmp_path):
    path = tmp_path / "commented.rules.txt"
    path.write_text("# a comment\n\nx: IF a(1)=1 THEN y=1  # trailing\n")
    assert len(parse_rules(path).rules) == 1


def test_to_body_projects_onto_the_requested_atoms():
    assignment = {atom(1): 1, atom(2): 0, atom(10): 1}
    assert to_body(assignment, [atom(1), atom(2)]) == frozenset(
        {(atom(1), True), (atom(2), False)}
    )
    assert to_body(assignment) == frozenset(
        {(atom(1), True), (atom(2), False), (atom(10), True)}
    )


def test_to_body_completes_a_projection_with_false():
    """One-hot .lp files (bank) record only the active bin per attribute. A mentioned
    atom absent from the instance reads as 0: the projected body is
    complete over the requested atoms."""
    assert to_body({atom(4, 4): 1}, [atom(4, 4), atom(4, 5)]) == frozenset(
        {(atom(4, 4), True), (atom(4, 5), False)}
    )
