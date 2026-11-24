# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

import json
from types import SimpleNamespace

from manim_extensions.automata.mobjects import (
    ManimDeterministicFiniteAutomaton,
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
            ],
        }
    }
}


def _automaton(**kwargs):
    return ManimDeterministicFiniteAutomaton(json_template=TEMPLATE, **kwargs)


def test_custom_animations_are_used():
    marker = object()
    automaton = _automaton(manim_animations=marker)
    assert automaton.manim_animations is marker


def test_xml_constructor_branch(monkeypatch):
    import manim_extensions.automata.mobjects.manim_automaton as module

    monkeypatch.setattr(module.ManimAutomaton, "process_xml", lambda self, path: None)
    automaton = module.ManimAutomaton(json_template=None, xml_file="graph.xml")
    assert automaton.states == []


def test_construct_state_rejects_second_initial():
    automaton = _automaton()
    automaton.construct_state(
        {"@id": "3", "@name": "q3", "initial": "", "x": "600", "y": "0"}
    )
    assert sum(1 for state in automaton.states if state.initial) == 1


def test_determine_input_builds_string_and_returns_mobject():
    automaton = _automaton()
    automaton.determine_input("ab")
    input_mobject = automaton.construct_automaton_input("ab")
    assert automaton.determine_input(input_mobject) is input_mobject


def test_run_with_recorded_path_short_circuits(monkeypatch):
    automaton = _automaton()
    monkeypatch.setattr(
        automaton, "load_recorded_path_from_file", lambda name: [("q0", "q1")]
    )
    monkeypatch.setattr(
        type(automaton),
        "play_automaton_path",
        lambda self, inp, path: ["ok"],
        raising=False,
    )

    assert automaton.run_input_through_automaton("ab", "path.json") == ["ok"]


def test_run_nda_without_tokens_exports_and_returns_history(monkeypatch):
    automaton = _automaton()
    automaton.nda_builder = True
    automaton.recorded_path = []
    monkeypatch.setattr(automaton, "export_recorded_path_to_file", lambda: None)

    history = automaton.run_input_through_automaton(SimpleNamespace(tokens=[]))

    assert "information" in history


def test_load_recorded_path_returns_none_for_mapping(tmp_path):
    automaton = _automaton()
    path = tmp_path / "path.json"
    path.write_text(json.dumps({"not": "a list"}))

    assert automaton.load_recorded_path_from_file(str(path)) is None


def test_run_sequence_nda_cli_records_choice(monkeypatch):
    automaton = _automaton()
    automaton.nda_builder = True
    automaton.recorded_path = []
    automaton.cli = SimpleNamespace(display_dictionary_options=lambda options: 0)
    transition = automaton.transitions[0]
    state = automaton.states[0]
    monkeypatch.setattr(
        automaton,
        "automaton_step",
        lambda token, pointer: (True, [transition.transition_to], [transition]),
    )

    history = []
    next_states, accepted = automaton.run_sequence("a", [state], history, None)

    assert accepted
    assert next_states == [transition.transition_to]
    assert automaton.recorded_path == [
        (transition.transition_from.name, transition.transition_to.name)
    ]


def test_run_sequence_nda_cli_records_choice(monkeypatch):
    automaton = _automaton()
    automaton.nda_builder = True
    automaton.recorded_path = []
    transition = automaton.transitions[0]
    state = automaton.states[0]
    monkeypatch.setattr(
        automaton,
        "automaton_step",
        lambda token, pointer: (True, [transition.transition_to], [transition]),
    )
    automaton.cli = SimpleNamespace(display_dictionary_options=lambda opts: 0)

    next_states, accepted = automaton.run_sequence("a", [state], [])

    assert accepted is True
    assert automaton.recorded_path == [("q0", "q1")]
    assert transition.transition_to in next_states
