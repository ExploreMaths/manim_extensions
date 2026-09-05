# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""State class for automata visualizations.

This module provides state visualization for automata.

"""

from manim import *
from .automata_dependencies.automata import State


class ManimState(State, VGroup):
    """Class that describes the graphical representation of a State instance,
    it is also used to simulate tautomata.

    Parameters
    ----------
    name : str
        Name of the state (e.g. ``"q0"``).
    x : float
        X coordinate of the state in the automaton layout.
    y : float
        Y coordinate of the state in the automaton layout.
    animation_style : dict
        Styling configuration for state and transition animations.
    initial : bool, optional
        If ``True``, mark this state as the initial state.
    final : bool, optional
        If ``True``, mark this state as a final (accepting) state.
    scaling : float, optional
        Coordinate-scaling factor applied to the state position.
    id : int, optional
        Numeric identifier matching the JFLAP XML state id.
    **kwargs
        Key words arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Attributes
    ----------

    state
        Reference to a State instance.
    circle
        Circle Mobject
    text
        Text Mobject representation of the name from State instance.

    Examples
    --------
    .. manim:: ManimStateExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_state import ManimState

       class ManimStateExample(Scene):
           def construct(self):
               style = {
                   "highlight_state": {"color": PURE_YELLOW},
                   "animate_transition": {"animation_function": FadeToColor, "accept_color": PURE_YELLOW, "reject_color": RED, "run_time": 0.5, "time_width": 2},
                   "token_highlight": {"animation_function": FadeToColor, "color": PURE_YELLOW},
               }
               state = ManimState("q0", 0, 0, style, initial=True)
               self.add(state)
    """

    def __init__(
        self,
        name: str,
        x: float,
        y: float,
        animation_style: dict[str, object],
        initial: bool | None = None,
        final: bool | None = None,
        scaling: float = 10,
        id: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize the ManimState instance."""
        State.__init__(self, name=name, initial=initial, final=final, id=id)

        # manim settings for animations and colors
        self.animation_style = animation_style

        self.text = Tex(name, font_size=100)
        self.circle = Circle(radius=2, color=BLUE)

        if True:
            self.initialise_subscript()
            VGroup.__init__(
                self, self.circle, self.text, self.subscript, name=name, **kwargs
            )

        else:
            VGroup.__init__(self, self.circle, self.text, name=name, **kwargs)

        self.set_x(x / scaling)
        self.set_y(
            (y * -1) / scaling
        )  # multiply y by -1 to flip the y axis, more similar to JFLAP

        if self.final:
            self.set_to_final_state()
        if self.initial:
            self.set_to_initial_state()

    def update_subscript(self, number: int | str) -> None:
        """Replace the state's subscript label with a new number or string.

        Parameters
        ----------
        number : int or str
            New subscript content.
        """
        self.remove(self.subscript)
        self.subscript = Tex(str(number), font_size=50)
        self.subscript.set_x(self.text.get_x() + -0.5)
        self.subscript.set_y(self.text.get_y() + -0.5)
        self.add(self.subscript)

    def initialise_subscript(self) -> None:
        """Create the initial subscript (``0``) positioned next to the state text."""
        self.subscript = Tex(0, font_size=50)
        self.subscript.set_x(self.text.get_x() + -0.5)
        self.subscript.set_y(self.text.get_y() + -0.5)

    def set_to_final_state(self) -> None:
        """Add an outer concentric circle to mark this state as a final state."""
        state_outer = Circle(radius=self.width * 0.4, color=BLUE)
        # move x and y of outerloop to be in the same position as parameter:state
        state_outer.set_x(self.circle.get_x())
        state_outer.set_y(self.circle.get_y())
        self.add(state_outer)

    def set_to_initial_state(self) -> None:
        """Add an incoming arrow to mark this state as the initial state."""
        arrow = Arrow(
            start=LEFT * 5,
            end=self,
            color=BLUE,
            buff=0.1,
            tip_style={"stroke_width": 5},
        )
        self.add(arrow)