"""Tests for MSW, the ECCRS operator that RC gets checked against.

Reference cases are Instances A-D, the four scholarship worked examples.
"""

from eccrs_workbench import msw
from tests.examples import INSTANCE_A, INSTANCE_B, INSTANCE_C, INSTANCE_D


def test_instance_a_exception_to_exception_awards(scholarship):
    assert {r.id for r in msw.applicable(scholarship, INSTANCE_A)} == {"r1", "r2", "r3"}
    assert {r.id for r in msw.maximal(msw.applicable(scholarship, INSTANCE_A))} == {"r3"}
    assert msw.predict(scholarship, INSTANCE_A) == 1


def test_instance_b_exception_denies(scholarship):
    assert {r.id for r in msw.applicable(scholarship, INSTANCE_B)} == {"r1", "r2"}
    assert {r.id for r in msw.maximal(msw.applicable(scholarship, INSTANCE_B))} == {"r2"}
    assert msw.predict(scholarship, INSTANCE_B) == 0


def test_instance_c_default_awards(scholarship):
    assert {r.id for r in msw.applicable(scholarship, INSTANCE_C)} == {"r4"}
    assert msw.predict(scholarship, INSTANCE_C) == 1


def test_instance_d_uncovered_abstains(scholarship):
    assert msw.applicable(scholarship, INSTANCE_D) == []
    assert msw.predict(scholarship, INSTANCE_D) is None


def test_maximal_uses_strict_specificity(scholarship):
    """A rule must not override itself: maximality needs strict superset, not >=."""
    applicable = msw.applicable(scholarship, INSTANCE_C)
    assert msw.maximal(applicable) == applicable  # single rule, nothing more specific
