# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for running input strings through the manim automata."""

import pytest
from manim import Scene

from manim_extensions.automata.mobjects.manim_automaton import automaton_json
from manim_extensions.automata.mobjects.manim_automaton_input import ManimAutomataInput
from manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton import (
    ManimdeterministicFiniteAutomaton,
)


@pytest.fixture()
def automaton():
    scene = Scene()
    machine = ManimdeterministicFiniteAutomaton(json_template=automaton_json)
    scene.add(machine)
    return scene, machine


def test_automaton_builds_states_and_mobjects(automaton):
    _, machine = automaton

    assert len(machine.states) == 4
    assert len(machine.submobjects) == 8


def test_play_string_from_text(automaton):
    _, machine = automaton

    animations = machine.play_string("ab")

    assert len(animations) >= 1
    assert all(isinstance(entry, list) for entry in animations)


def test_play_string_from_constructed_input(automaton):
    _, machine = automaton

    manim_input = machine.construct_automaton_input("a")
    animations = machine.play_string(manim_input)

    assert machine.manim_automata_input is manim_input
    assert len(animations) >= 1


def test_manim_automata_input_exposes_tokens(automaton):
    _, machine = automaton

    manim_input = ManimAutomataInput("ab", machine.animation_style)

    assert len(manim_input.submobjects) >= 1
