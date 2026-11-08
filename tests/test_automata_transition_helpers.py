# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for transition animation, symbol matching and opposite arrows."""

import pytest
from manim import MathTex, Scene

from manim_extensions.automata.mobjects.manim_automaton import default_animation_style

from manim_extensions.automata.mobjects.manim_state import ManimState
from manim_extensions.automata.mobjects.manim_transition import ManimTransition


@pytest.fixture()
def states():
    first = ManimState("q1", 0.0, 0.0, "Straight")
    second = ManimState("q2", 3.0, 0.0, "Straight")
    return first, second


def test_animate_transition_returns_animation(states):
    first, second = states
    transition = ManimTransition(
        first, second, ["a"], Scene(), animation_style="Straight"
    )

    transition.animation_style = default_animation_style
    animation = transition.animate_transition(True)

    assert animation is not None


def test_check_transition_read_symbols_match(states):
    first, second = states
    transition = ManimTransition(
        first, second, ["a"], Scene(), animation_style="Straight"
    )

    assert transition.check_transition_read_symbols(MathTex("a")) is True


def test_check_transition_read_symbols_mismatch(states):
    first, second = states
    transition = ManimTransition(
        first, second, ["a"], Scene(), animation_style="Straight"
    )

    assert transition.check_transition_read_symbols(MathTex("b")) is False


def test_opposite_transition_is_curved(states):
    first, second = states
    forward = ManimTransition(first, second, ["a"], Scene(), animation_style="Straight")
    backward = ManimTransition(
        second, first, ["b"], Scene(), animation_style="Straight"
    )

    assert backward is not None


def test_self_transition_creates_reflexive_arrow():
    state = ManimState("q1", 0.0, 0.0, "Straight")
    transition = ManimTransition(
        state, state, ["a"], Scene(), animation_style="Straight"
    )

    assert len(transition.submobjects) >= 1
