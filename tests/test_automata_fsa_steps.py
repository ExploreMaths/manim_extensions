# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the low-level finite state automaton stepping API."""

import pytest
from manim import MathTex

from manim_extensions.automata.mobjects.manim_automaton import automaton_json
from manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton import (
    ManimdeterministicFiniteAutomaton,
)


@pytest.fixture(scope="module")
def machine():
    return ManimdeterministicFiniteAutomaton(json_template=automaton_json)


def test_every_state_has_a_transition(machine):
    assert all(len(state.get_transitions()) >= 1 for state in machine.states)


def test_get_transition_by_id_roundtrip(machine):
    transition = machine.states[0].get_transitions()[0]

    assert machine.get_transition_by_id(transition.id) is not None


def test_automaton_step_with_non_matching_symbol(machine):
    result = machine.automaton_step(MathTex("a"), machine.states[0])

    assert isinstance(result, tuple)
    assert len(result) == 3


def test_automaton_step_with_matching_symbol(machine):
    state = machine.states[0]
    symbol = state.get_transitions()[0].read_symbols[0]

    result = machine.automaton_step(symbol, state)

    assert isinstance(result, tuple)
    assert len(result) == 3


def test_automaton_step_accepted_flag_is_bool(machine):
    result = machine.automaton_step(MathTex("1"), machine.states[0])

    assert isinstance(result[0], bool)
