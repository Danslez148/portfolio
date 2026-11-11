"""Fixtures wrapping the worked examples in tests/examples.py."""

import pytest

from eccrs_workbench.parser import parse_instances, parse_rules
from tests.examples import FIXTURES, REPO, boat_knowledge_base


@pytest.fixture
def scholarship():
    return parse_rules(FIXTURES / "scholarship.rules.txt")


@pytest.fixture
def cancer_rules():
    return parse_rules(REPO / "datasets" / "cancer" / "rules.txt")


@pytest.fixture
def cancer_instances():
    return parse_instances(REPO / "datasets" / "cancer" / "data-cancer.lp")


@pytest.fixture
def boat_kb():
    return boat_knowledge_base()
