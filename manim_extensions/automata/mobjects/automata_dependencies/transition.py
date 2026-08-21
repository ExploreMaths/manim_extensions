# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from __future__ import annotations

import itertools

from .state import State

class Transition:
    """Class that represents transitions between states.

    Parameters
    ----------
    transition_from
        Json object that describes an automaton.
    transition_to
        Path of XML format file describing an automaton.
    input_symbol
        The class' input symbol.
    Attributes
    ----------
    id
        The instance's id.
    transition_from
        The state where the transition begins.
    transition_to
        The state where the transition ends.
    input_symbol
        The symbols that the transition requires.

    Examples
    --------
    .. manim:: TransitionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.automata_dependencies.state import State
       from manim_extensions.automata.mobjects.automata_dependencies.transition import Transition

       class TransitionExample(Scene):
           def construct(self):
               s1 = State("q0")
               s2 = State("q1")
               trans = Transition(s1, s2)
               label = Text(f"Transition: {trans.transition_from.name} -> {trans.transition_to.name}", font_size=24)
               self.add(label)
"""
    id_iter = itertools.count()


    def __init__(self, transition_from: State, transition_to: State) -> None:
        """Initialize the Transition instance."""
        self.id = next(self.id_iter)
        self.transition_from = transition_from
        self.transition_to = transition_to