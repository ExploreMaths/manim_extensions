# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Manim automaton mobjects built from a JSON template."""

from manim import Scene

from manim_extensions.automata.mobjects import (
    ManimdeterministicFiniteAutomaton,
    ManimNondeterministicFiniteAutomaton,
)

TEMPLATE = {
    "structure": {
        "automaton": {
            "state": [
                {"@id": "0", "@name": "q0", "initial": "", "x": "0", "y": "0"},
                {"@id": "1", "@name": "q1", "x": "200", "y": "0"},
                {"@id": "2", "@name": "q2", "final": "", "x": "400", "y": "0"},
            ],
            "transition": [
                {"from": "0", "to": "1", "read": "a"},
                {"from": "1", "to": "2", "read": "b"},
                {"from": "2", "to": "2", "read": "b"},
            ],
        }
    }
}


def test_deterministic_automaton_is_built():
    automaton = ManimdeterministicFiniteAutomaton(json_template=TEMPLATE)

    assert len(automaton.states) == 3
    assert len(automaton.transitions) == 3
    assert len(automaton.submobjects) == 6


def test_state_lookups():
    automaton = ManimdeterministicFiniteAutomaton(json_template=TEMPLATE)

    assert automaton.get_state("q1").name == "q1"
    assert automaton.get_state("missing") is None
    assert automaton.get_state_by_id(2).name == "q2"
    assert automaton.get_state_by_id(99) is None


def test_nondeterministic_automaton_is_built():
    automaton = ManimNondeterministicFiniteAutomaton(json_template=TEMPLATE)

    assert len(automaton.states) == 3


def test_automaton_can_be_added_to_a_scene():
    automaton = ManimdeterministicFiniteAutomaton(json_template=TEMPLATE)
    scene = Scene()
    scene.add(automaton)

    assert automaton in scene.mobjects
