# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import Circle

from manim_extensions.automata import ManimAutomaton, ManimNonDeterminsticFiniteAutomaton
from manim_extensions.automata.mobjects.automata_dependencies.state import State
from manim_extensions.automata.mobjects.automata_dependencies.transitition import Transition
from manim_extensions.automata.mobjects.manim_state import ManimState
from manim_extensions.automata.mobjects.manim_transition import ManimTransition


def test_automata_core_api():
    start = ManimState("A", 0, 0, {}, initial=True, final=False, scaling=1, id=1)
    end = ManimState("B", 2, 0, {}, initial=False, final=True, scaling=1, id=2)

    state = State("Q")
    transition = Transition(state, state)
    assert state.id >= 0
    assert transition.transition_from is state
    assert transition.transition_to is state

    automaton = ManimAutomaton()
    assert automaton is not None
    assert hasattr(automaton, "states")
    assert hasattr(automaton, "transitions")

    trans = ManimTransition(
        start,
        end,
        ["a"],
        parent_automaton=automaton,
        animation_style={
            "animate_transition": {
                "animation_function": None,
                "accept_color": None,
                "reject_color": None,
            }
        },
    )
    assert trans.transition_from is start
    assert trans.transition_to is end
    assert len(trans.read_symbols) == 1

    nda = ManimNonDeterminsticFiniteAutomaton()
    assert hasattr(nda, "nda_builder")
