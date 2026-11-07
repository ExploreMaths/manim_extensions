# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the finite state automaton data model."""

import pytest

from manim_extensions.automata.mobjects.automata_dependencies.automata import (
    FiniteStateAutomaton,
    PushDownAutomaton,
)

TEMPLATE = {
    "structure": {
        "automaton": {
            "state": [
                {"@id": "0", "@name": "q0", "initial": ""},
                {"@id": "1", "@name": "q1"},
                {"@id": "2", "@name": "q2", "final": ""},
            ],
            "transition": [
                {"from": "0", "to": "1", "read": "a"},
                {"from": "1", "to": "2", "read": "b"},
                {"from": "2", "to": "2", "read": "b"},
            ],
        }
    }
}


@pytest.fixture()
def automaton():
    return FiniteStateAutomaton(json_template=TEMPLATE)


def test_states_are_constructed(automaton):
    assert len(automaton.states) == 3
    assert len(automaton.transitions) == 3


def test_named_lookups(automaton):
    assert automaton.get_state("q1").name == "q1"
    assert automaton.get_state("missing") is None
    assert automaton.get_state_by_id(2).name == "q2"
    assert automaton.get_state_by_id(99) is None


def test_push_down_automaton_instantiates():
    pda = PushDownAutomaton()

    assert pda.states == []
    assert pda.transitions == []
