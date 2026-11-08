# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the DFA runtime helpers that do not require animations."""

import pytest

from manim_extensions.automata.mobjects import ManimdeterministicFiniteAutomaton

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


@pytest.fixture()
def automaton():
    return ManimdeterministicFiniteAutomaton(json_template=TEMPLATE)


def test_automaton_reports_accepting_and_rejecting_states(automaton):
    assert automaton.check_automaton_result([automaton.get_state("q2")])
    assert not automaton.check_automaton_result([automaton.get_state("q0")])


def test_next_state_options_follow_transitions(automaton):
    options = automaton.generate_next_state_options(
        automaton.get_state("q0"), automaton.transitions
    )

    assert len(options) >= 2
    assert all(isinstance(label, str) for label, _ in options.values())
