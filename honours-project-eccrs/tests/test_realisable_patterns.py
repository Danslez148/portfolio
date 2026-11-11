"""One-hot mutual exclusion and the realisable pattern subspace.

The theorem is stated over the whole Boolean space of the KB's atoms, so
`over_patterns` still enumerates all 2^a patterns and that stays the headline
number. But with one-hot attributes (a(i,j) is value bin j of attribute i) at most
one bin per attribute is true in a real instance, so many of the 2^a patterns can't
occur. We also report the size of that realisable subset and the agreement over it,
exactly, with no sampling.
"""

from eccrs_workbench.base_rank import base_rank
from eccrs_workbench.model import atom, is_realisable, one_hot_families
from eccrs_workbench.parser import parse_rules
from eccrs_workbench.report import over_patterns


def _rules(tmp_path, text):
    path = tmp_path / "r.rules.txt"
    path.write_text(text)
    return parse_rules(path)


def test_one_hot_families_groups_two_index_atoms_by_attribute():
    atoms = [atom(4, 1), atom(4, 2), atom(4, 5), atom(12, 1), atom(12, 2), atom(3, 5)]
    families = one_hot_families(atoms)
    assert families == {
        4: frozenset({atom(4, 1), atom(4, 2), atom(4, 5)}),
        12: frozenset({atom(12, 1), atom(12, 2)}),
    }
    # a(3,5) is the only bin of attribute 3, a lone bin carries no exclusion.
    assert 3 not in families


def test_one_hot_families_never_groups_single_index_indicators():
    """a(4) is an independent binary (mushroom "bruises?"), not a one-hot bin, even
    if a(4,j) atoms are also present for some reason."""
    assert one_hot_families([atom(4), atom(8)]) == {}
    assert one_hot_families([atom(4), atom(4, 1), atom(4, 2)]) == {
        4: frozenset({atom(4, 1), atom(4, 2)})
    }


def test_is_realisable_allows_at_most_one_bin_per_family():
    families = {1: frozenset({atom(1, 1), atom(1, 2), atom(1, 3)})}
    one_bin = frozenset({(atom(1, 1), True), (atom(1, 2), False), (atom(1, 3), False)})
    no_bin = frozenset({(atom(1, 1), False), (atom(1, 2), False), (atom(1, 3), False)})
    two_bins = frozenset({(atom(1, 1), True), (atom(1, 2), True), (atom(1, 3), False)})
    assert is_realisable(one_bin, families)
    assert is_realisable(no_bin, families)  # true value is a bin no rule mentions
    assert not is_realisable(two_bins, families)


def test_is_realisable_is_trivially_true_without_families():
    body = frozenset({(atom(1), True), (atom(2), False)})
    assert is_realisable(body, {})


# A one-hot recast of the scholarship ruleset: the two independent
# atoms a(1) and a(2) become bins a(1,1) and a(1,2) of one attribute. The single
# MSW/RC divergence (r3 and r5 both maximal, opposite labels, MSW abstains, RC entails
# the award) now falls on a pattern that sets both bins true: unrealisable.
_ONE_HOT_SCHOLARSHIP = """\
r1: IF a(1,1)=1 THEN y=1
r2: IF a(1,1)=1 & a(4)=1 THEN y=0
r3: IF a(1,1)=1 & a(4)=1 & a(5)=1 THEN y=1
r4: IF a(1,2)=1 & a(3)=1 THEN y=1
r5: IF a(1,2)=1 & a(3)=1 & a(4)=1 THEN y=0
"""


def test_over_patterns_reports_the_realisable_subset_exactly(tmp_path):
    """Atoms a(1,1), a(1,2), a(3), a(4), a(5): attribute 1 has two one-hot bins, so of
    2^5 = 32 patterns the 8 that set both bins true are unrealisable, leaving 24."""
    ruleset = _rules(tmp_path, _ONE_HOT_SCHOLARSHIP)
    agreement = over_patterns(ruleset, base_rank(ruleset.to_kb()))
    assert agreement.total == 32
    assert agreement.realisable_total == 24
    assert {r.realisable for r in agreement.rows} == {True, False}
    for row in agreement.rows:
        both_bins = {(atom(1, 1), True), (atom(1, 2), True)} <= row.pattern
        assert row.realisable == (not both_bins)


def test_realisable_stats_exclude_the_impossible_region(tmp_path):
    """The one full-space divergence sits entirely in the unrealisable region: MSW
    abstains where r3 and r5 tie, RC entails class 1, and that pattern sets both bins
    of attribute 1 true. Agreement over realisable patterns is therefore complete."""
    ruleset = _rules(tmp_path, _ONE_HOT_SCHOLARSHIP)
    agreement = over_patterns(ruleset, base_rank(ruleset.to_kb()))
    assert len(agreement.divergences) == 1
    assert agreement.rate < 1.0
    assert all(not row.realisable for row in agreement.divergences)
    assert agreement.realisable_divergences == ()
    assert agreement.realisable_rate == 1.0
