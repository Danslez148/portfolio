"""Worked examples from the literature, as data. Shared by conftest and the tests."""

from pathlib import Path

from eccrs_workbench.model import Body, Conditional, ConditionalKB, atom

REPO = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# Scholarship atoms. Single-index, so atom(i) == (i,).
GPA, NEED, SERVICE, FLAG, RESEARCH = (atom(1), atom(2), atom(3), atom(4), atom(5))


def pattern(*values: int) -> Body:
    """A complete feature pattern over a(1)..a(n): pattern(1,0,0,1,1) is Instance A."""
    return frozenset((atom(i), bool(v)) for i, v in enumerate(values, start=1))


# Instances A-D, the four scholarship worked examples, with their known MSW outputs.
INSTANCE_A = pattern(1, 0, 0, 1, 1)  # exception-to-exception -> award  (1)
INSTANCE_B = pattern(1, 0, 0, 1, 0)  # exception              -> deny   (0)
INSTANCE_C = pattern(0, 1, 1, 0, 0)  # default                -> award  (1)
INSTANCE_D = pattern(0, 0, 0, 0, 0)  # uncovered              -> abstain(None)

EXPECTED_MSW = {
    "A": (INSTANCE_A, 1),
    "B": (INSTANCE_B, 0),
    "C": (INSTANCE_C, 1),
    "D": (INSTANCE_D, None),
}

# Kaliski's boat / leaky / FlyingDutchman KB.
BOAT, FLOATS, LEAKY, DUTCHMAN = (atom(1), atom(2), atom(3), atom(4))
BOAT_NAMES = {BOAT: "boat", FLOATS: "floats", LEAKY: "leaky", DUTCHMAN: "FlyingDutchman"}


def boat_knowledge_base() -> ConditionalKB:
    """Built directly rather than parsed: this is a KLM knowledge base with arbitrary
    consequents, not an ECCRS ruleset over a single class atom, so it has no rules.txt
    representation."""
    conditionals = (
        Conditional(frozenset({(BOAT, True)}), (FLOATS, True), "boat|~floats"),
        Conditional(frozenset({(LEAKY, True)}), (BOAT, True), "leaky|~boat"),
        Conditional(frozenset({(LEAKY, True)}), (FLOATS, False), "leaky|~-floats"),
        Conditional(frozenset({(DUTCHMAN, True)}), (BOAT, True), "FD|~boat"),
        Conditional(frozenset({(DUTCHMAN, True)}), (LEAKY, True), "FD|~leaky"),
    )
    return ConditionalKB(conditionals, label_atom=FLOATS, atom_names=BOAT_NAMES)
