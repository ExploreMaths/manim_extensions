# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Contains classes for state."""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .transition import Transition


class State:
    """Class that represents states.

    Parameters
    ----------
    name : str
        The state's name (e.g. ``"q0"``).
    initial : bool, optional
        If ``True``, mark this state as the initial state.
    final : bool, optional
        If ``True``, mark this state as a final (accepting) state.
    id : int, optional
        Numeric identifier matching the JFLAP XML state id.

    Attributes
    ----------
    id
        The instance's id.
    name
        The state's name.
    initial
        If the instance is an initial state or not.
    final
        If the instance is a final state or not.

    Examples
    --------
    .. manim:: StateExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.automata_dependencies.state import State
       from manim_extensions.automata.mobjects.automata_dependencies.transition import Transition

       class StateExample(Scene):
           def construct(self):
               start = State("q0", initial=True)
               end = State("q1", final=True)
               transition = Transition(start, end)
               transition.read_symbols = ["a"]
               start.add_transition_to_state(transition)
               c1, c2 = Circle(radius=0.6).shift(LEFT * 2), Circle(radius=0.6).shift(RIGHT * 2)
               self.add(
                   Arrow(LEFT * 4.5, c1.get_left(), buff=0.1),
                   c1,
                   Text(start.name, font_size=24).move_to(c1),
                   Circle(radius=0.45).move_to(c2),
                   c2,
                   Text(end.name, font_size=24).move_to(c2),
                   Arrow(c1, c2, buff=0.65),
                   MathTex("a").next_to(ORIGIN, UP, buff=0.3),
               )
               outgoing = start.get_transition_by_transition_to_state_id(end.id)
               caption = Text(
                   f"State {start.name} has {len(start.transitions)} outgoing transition(s) to {outgoing.transition_to.name}",
                   font_size=20,
               ).to_edge(DOWN)
               self.add(caption)
    """

    id_iter = itertools.count()

    def __init__(
        self,
        name: str,
        initial: bool | None = None,
        final: bool | None = None,
        id: int | None = None,
    ) -> None:
        """Initialize the State instance."""
        if id is not None:
            self.id = int(id)
        else:
            self.id = next(self.id_iter)

        self.name = name
        self.initial = initial
        self.final = final

        # list of transitions links this state to others
        self.transitions = []

    def add_transition_to_state(self, transition: "Transition") -> list:
        """Add a transition to the state's transition list.

        Parameters
        ----------
        transition : Transition
            The transition to register for this state.
        """
        self.transitions.append(transition)
        return self.transitions

    def get_transition(self, id: int) -> "Transition":
        """Return the transition matching the given identifier.

        Parameters
        ----------
        id : int
            The transition identifier to look up.
        """
        for transition in self.transitions:
            if transition.id == id:
                return transition
        return None

    def get_transition_by_transition_to_state_id(
        self, transition_to_state_id: int
    ) -> "Transition | None":
        """Return the transition whose destination state matches the given id.

        Parameters
        ----------
        transition_to_state_id
            Identifier of the target state.
        """
        for transition in self.transitions:
            if transition.transition_to.id == transition_to_state_id:
                return transition
        return None

    def __str__(self) -> str:
        """Internal __str__ hook."""
        return "State id: {self.id}, name: {self.name}".format(self=self)
