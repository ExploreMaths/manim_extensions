# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for automaton transition mobjects, including curved arrows."""

import pytest
from manim import Scene

from manim_extensions.automata.mobjects.manim_state import ManimState
from manim_extensions.automata.mobjects.manim_transition import ManimTransition


@pytest.fixture()
def states():
    first = ManimState("q1", 0.0, 0.0, "Straight")
    second = ManimState("q2", 3.0, 0.0, "Straight")

    return first, second


@pytest.mark.parametrize("style", ["Straight", "Curved"])
def test_transition_construction(states, style):
    first, second = states

    transition = ManimTransition(first, second, ["a"], Scene(), animation_style=style)

    assert len(transition.submobjects) >= 1


def test_convert_straight_to_curved_arrow(states):
    first, second = states
    transition = ManimTransition(
        first, second, ["a"], Scene(), animation_style="Straight"
    )

    transition.convert_straight_arrow_to_curved_arrow()

    assert len(transition.submobjects) >= 1
