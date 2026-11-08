# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the interactive NDA path builder and state helpers."""

import pytest
from manim import Scene

from manim_extensions.automata.mobjects.manim_automaton import automaton_json
from manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton import (
    ManimdeterministicFiniteAutomaton,
)


@pytest.fixture()
def cli_machine(monkeypatch, tmp_path):
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: "0")
    monkeypatch.chdir(tmp_path)
    machine = ManimdeterministicFiniteAutomaton(json_template=automaton_json, cli=True)
    return machine


def test_cli_machine_enables_nda_builder(cli_machine):
    assert cli_machine.nda_builder is True


def test_add_manim_state_appends_submobject(cli_machine):
    state = cli_machine.states[0]
    before = len(cli_machine.submobjects)

    cli_machine.add_manim_state(state)

    assert len(cli_machine.submobjects) >= before


def test_initial_state_is_unique(cli_machine):
    assert cli_machine.get_initial_state() is not None
