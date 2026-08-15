"""Contains classes for state."""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .transitition import Transition

class State:
    """Class that represents states.

    Parameters
    ----------
    name
        The class' name.
    initial
        The class' state type, in terms of initial state.
    final
        the class' state type, in terms of final state.

    Attributes
    ----------
    id
        The instance's id.
    name
        The class' name.
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

        class StateExample(Scene):
            def construct(self):
                state = State("q0", initial=True)
                label = Text(f"State: {state.name}", font_size=24)
                self.add(label)
"""

    id_iter = itertools.count()

    def __init__(self, name: str, initial: bool | None = None, final: bool | None = None, id: int | None = None) -> None:
        """Initialize the State instance."""
        if id is not None:
            self.id = int(id)
        else:
            self.id = next(self.id_iter)

        self.name = name
        self.initial = initial
        self.final = final

        #list of transitions links this state to others
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

    def get_transition_by_transition_to_state_id(self, transition_to_state_id: int) -> "Transition | None":
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
        return 'State id: {self.id}, name: {self.name}'.format(self=self)