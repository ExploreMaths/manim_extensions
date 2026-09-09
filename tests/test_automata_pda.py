# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the pushdown automaton (PDA) mobject.

Regressions for the fixes in ``c675ee2`` (play_string UnboundLocalError,
uniform list-of-animation-lists return, str input handling).
"""

from manim.animation.animation import prepare_animation

from manim_extensions.automata.mobjects.manim_pushdown_automaton import (
    ManimPushDownAutomaton,
    pushdown_automaton_json,
)


def _assert_animation_sequences(sequences):
    """play_string returns a uniform list of lists of playable animations."""
    assert isinstance(sequences, list)
    assert len(sequences) > 0
    for sequence in sequences:
        assert isinstance(sequence, list)
        for anim in sequence:
            prepare_animation(anim)


class TestPushDownAutomaton:
    def test_construct_default_template(self):
        pda = ManimPushDownAutomaton()
        assert pda is not None
        assert isinstance(pda.stack, list)

    def test_construct_from_json_template(self):
        pda = ManimPushDownAutomaton(json_template=pushdown_automaton_json)
        assert len(pda.states) > 0

    def test_push_pop(self):
        pda = ManimPushDownAutomaton()
        pda.stack.clear()
        pda.push("X")
        assert pda.stack[-1] == "X"
        assert pda.pop() == "X"
        assert pda.pop() is None

    def test_play_string_accepts_str(self):
        # Regression: str input used to crash with UnboundLocalError.
        pda = ManimPushDownAutomaton()
        sequences = pda.play_string("01")
        _assert_animation_sequences(sequences)

    def test_play_string_accepts_input_mobject(self):
        pda = ManimPushDownAutomaton()
        automaton_input = pda.construct_automaton_input("01")
        sequences = pda.play_string(automaton_input)
        _assert_animation_sequences(sequences)

    def test_get_initial_state_and_check_result(self):
        pda = ManimPushDownAutomaton()
        initial = pda.get_initial_state()
        assert initial is not None
        states = pda.get_states()
        assert isinstance(states, list)
        assert initial in states
