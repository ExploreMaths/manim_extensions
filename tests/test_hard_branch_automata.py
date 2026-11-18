# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for automata state lookups and non-deterministic stepping."""

import pytest
from manim import MathTex

from manim_extensions.automata.mobjects.automata_dependencies.automata import (
    FiniteStateAutomaton,
    PushDownAutomaton,
)
from manim_extensions.automata.mobjects.automata_dependencies.state import State

BRANCHING_TEMPLATE = {
    "structure": {
        "automaton": {
            "state": [
                {"@id": "0", "@name": "q0", "initial": ""},
                {"@id": "1", "@name": "q1", "final": ""},
                {"@id": "2", "@name": "q2", "final": ""},
            ],
            "transition": [
                {"@id": "0", "from": "0", "to": "1", "read": "a"},
                {"@id": "1", "from": "0", "to": "2", "read": "a"},
            ],
        }
    }
}


@pytest.fixture()
def branching_automaton():
    return FiniteStateAutomaton(json_template=BRANCHING_TEMPLATE)


@pytest.fixture()
def branching_pda():
    from manim_extensions.automata.mobjects.automata_dependencies.transition import (
        Transition,
    )

    pda = PushDownAutomaton()
    q0 = State("q0", initial=True, id=0)
    q1 = State("q1", final=True, id=1)
    q2 = State("q2", final=True, id=2)
    first = Transition(q0, q1)
    first.id = 0
    second = Transition(q0, q2)
    second.id = 1
    first.read_symbols = [MathTex("a")]
    second.read_symbols = [MathTex("a")]
    q0.add_transition_to_state(first)
    q0.add_transition_to_state(second)
    pda.states = [q0, q1, q2]
    pda.transitions = [first, second]
    return pda


def test_state_get_transition_by_id_and_unknown(branching_automaton):
    state = branching_automaton.states[0]
    expected = state.get_transitions()[0]

    assert state.get_transition(expected.id) is expected
    assert state.get_transition(999) is None


def test_state_get_transition_by_destination_id_and_unknown(branching_automaton):
    state = branching_automaton.states[0]
    expected = state.get_transitions()[0]

    found = state.get_transition_by_transition_to_state_id(expected.transition_to.id)
    assert found is expected
    assert state.get_transition_by_transition_to_state_id(999) is None


def test_state_string_representation(branching_automaton):
    assert str(branching_automaton.states[0]) == "State id: 0, name: q0"


def test_non_deterministic_step_returns_all_matching_states(branching_pda):
    accepted, next_states, transition_ids = branching_pda.automaton_step(
        MathTex("a"), branching_pda.states[0], deterministic=False
    )

    assert accepted is True
    assert len(next_states) == 2
    assert transition_ids == [0, 1]


def test_deterministic_step_returns_first_matching_state(branching_pda):
    accepted, next_states, transition_ids = branching_pda.automaton_step(
        MathTex("a"), branching_pda.states[0], deterministic=True
    )

    assert accepted is True
    assert len(next_states) == 1
    assert transition_ids == [0]


def test_step_without_matching_transition(branching_pda):
    accepted, next_states, transition_ids = branching_pda.automaton_step(
        MathTex("z"), branching_pda.states[0], deterministic=False
    )

    assert accepted is False
    assert next_states == []
    assert transition_ids == []


def test_state_without_transitions_returns_empty_transition(branching_automaton):
    state = State(id=7, name="isolated")
    assert state.get_transitions() == []
    assert state.get_transition(0) is None


def test_xml_parser_reads_mapping(tmp_path):
    from manim_extensions.automata.mobjects.automata_dependencies.xml_parser import (
        parse_xml_file,
    )

    xml_file = tmp_path / "automaton.xml"
    xml_file.write_text(
        '<?xml version="1.0"?><structure><automaton><state id="0"/></automaton></structure>'
    )

    parsed = parse_xml_file(str(xml_file))

    assert parsed["structure"]["automaton"]["state"]["@id"] == "0"
