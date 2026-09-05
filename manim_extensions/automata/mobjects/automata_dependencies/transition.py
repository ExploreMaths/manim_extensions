# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Transition representation for automata.

This module provides the Transition class for representing state transitions in automata.

"""

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
               trans.read_symbols = ["a", "b"]
               s1.add_transition_to_state(trans)
               c1, c2 = Circle(radius=0.6).shift(LEFT * 2), Circle(radius=0.6).shift(RIGHT * 2)
               arrow = Arrow(c1, c2, buff=0.65)
               self.add(
                   c1,
                   Text(s1.name, font_size=24).move_to(c1),
                   c2,
                   Text(s2.name, font_size=24).move_to(c2),
                   arrow,
                   MathTex("a, b").next_to(arrow.get_center(), UP, buff=0.2),
               )
               caption = Text(
                   f"Transition {trans.id}: {trans.transition_from.name} -> {trans.transition_to.name}, read={trans.read_symbols}",
                   font_size=20,
               ).to_edge(DOWN)
               self.add(caption)
    """

    id_iter = itertools.count()

    def __init__(self, transition_from: State, transition_to: State) -> None:
        """Initialize the Transition instance."""
        self.id = next(self.id_iter)
        self.transition_from = transition_from
        self.transition_to = transition_to