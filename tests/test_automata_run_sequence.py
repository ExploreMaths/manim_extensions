# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for low-level automaton run helpers."""

import pytest
from manim import Scene

from manim_extensions.automata.mobjects.manim_automaton import automaton_json
from manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton import (
    ManimdeterministicFiniteAutomaton,
)


@pytest.fixture()
def machine():
    scene = Scene()
    instance = ManimdeterministicFiniteAutomaton(json_template=automaton_json)
    scene.add(instance)
    return instance


def test_run_sequence_returns_next_states(machine):
    history = []

    token = machine.construct_automaton_input("a").submobjects[0]
    next_states, accepted = machine.run_sequence(token, [machine.states[0]], history)

    assert isinstance(next_states, list)
    assert isinstance(accepted, bool)
    assert len(history) == 1


def test_export_and_load_recorded_path(machine, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    machine.recorded_path = [("q0", "q1")]

    machine.export_recorded_path_to_file()
    loaded = machine.load_recorded_path_from_file("recorded_path.txt")

    assert loaded is not None
