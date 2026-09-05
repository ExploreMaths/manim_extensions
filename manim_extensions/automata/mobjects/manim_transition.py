# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Transition class for automata visualizations.

This module provides transition visualization for automata.

"""

from __future__ import annotations

from collections.abc import Sequence

from manim import *
from typing import TYPE_CHECKING, Any
from .automata_dependencies.automata import Transition

from .manim_state import ManimState

if TYPE_CHECKING:
    from .manim_automaton import ManimAutomaton

import math


class ManimTransition(Transition, VGroup):
    """A visual transition arrow for automata diagrams.

    The object combines a Manim arrow with labels representing the read symbols
    of a finite-state transition.

    Parameters
    ----------
    transition_from : ManimState
        State at which the transition starts.
    transition_to : ManimState
        State at which the transition ends.
    read_symbols : sequence of str
        Symbols associated with the transition.
    parent_automaton : ManimAutomaton
        Parent automaton owning the transition.
    animation_style : dict
        Styling configuration used for animation playback.
    font_size : int, optional
        Font size for the read-symbol labels.  Defaults to ``100``.
    buffer : int, optional
        Spacing buffer for label positioning.  Defaults to ``1``.
    **kwargs
        Additional parameters for :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: ManimTransitionDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata import ManimdeterministicFiniteAutomaton

       class ManimTransitionDocExample(Scene):
           def construct(self):
               dfa = ManimdeterministicFiniteAutomaton()
               self.add(dfa)
               transition = dfa.transitions[0]
               start = transition.transition_from.name
               end = transition.transition_to.name
               label = Text(
                   f"Transition {start} -> {end}",
                   font_size=20,
               )
               label.next_to(dfa, DOWN, buff=1.5)
               self.add(label)
    """

    def __init__(
        self,
        transition_from: ManimState,
        transition_to: ManimState,
        read_symbols: Sequence[str],
        parent_automaton: "ManimAutomaton",
        animation_style: dict[str, Any],
        font_size: int = 100,
        buffer: int = 1,
        **kwargs: Any,
    ) -> None:
        """Initialize the ManimTransition instance."""
        Transition.__init__(self, transition_from, transition_to)
        self.circle = None
        # manim settings for animations and colors
        self.animation_style = animation_style
        # store tex mobjects of read_symbols for transitions
        self.read_symbols = []

        self.buffer = buffer

        self.parent_automaton = parent_automaton
        # create manim read symbols for transition
        for read_symbol in read_symbols:
            # Create mobjects of read_symbol
            self.read_symbols.append(MathTex(read_symbol, font_size=font_size))

        if (
            self.transition_from == self.transition_to
        ):  # create transition that points to itself
            position_1, position_2 = self.calculate_circle_vertices()
            self.create_reflexive_arrow(position_1, position_2)
        elif (
            self.transition_to.get_transition_by_transition_to_state_id(
                self.transition_from.id
            )
            is not None
        ):  # check if there already exists an arrow pointing the opposite way
            # pre-exising arrow transition converted to curved arrow
            opposite_transition = (
                self.transition_to.get_transition_by_transition_to_state_id(
                    self.transition_from.id
                )
            )
            opposite_transition.convert_straight_arrow_to_curved_arrow()

            # create this(self) arrow
            self.construct_curved_arrow()

        else:  # transition_from ----> transition_to
            self.arrow = Arrow(transition_from, transition_to, buff=0)
            self.position_text(self.buffer)

        self.rotate_symbols_parallel_to_arrow()

        VGroup.__init__(self, self.arrow, *self.read_symbols, **kwargs)

    def animate_transition(self, transition_result: bool) -> Animation:
        """Animate the transition using the configured style.

        Parameters
        ----------
        transition_result : bool
            Whether the transition is accepted by the automaton.
        """
        animation_function = self.animation_style["animate_transition"][
            "animation_function"
        ]

        color = self.animation_style["animate_transition"]["accept_color"]

        return animation_function(self.arrow, color=color)

    def calculate_circle_vertices(self) -> tuple[np.ndarray, np.ndarray]:
        """Calculate two vertices on the source state's circle for arrow endpoints.

        The vertices are placed at angles ``PI/4`` and ``3*PI/4`` on the circle.

        Returns
        -------
        tuple of numpy.ndarray
            The two vertex points ``(p1, p2)``.
        """
        circle = self.transition_from.circle

        p1 = circle.point_at_angle(PI / 4 + PI / 2)
        p2 = circle.point_at_angle(PI / 4)

        return p1, p2

    def create_reflexive_arrow(self, point1: np.ndarray, point2: np.ndarray) -> None:
        """Create a curved reflexive arrow from the source state back to itself.

        Parameters
        ----------
        point1 : numpy.ndarray
            Start point on the state circle.
        point2 : numpy.ndarray
            End point on the state circle.
        """
        self.arrow = CurvedArrow(point2, point1, angle=1.5 * PI)

        # used to position the read symbols
        center_of_arc = self.arrow.get_arc_center()
        radius = self.arrow.radius

        # positions the text above the reflexive arrow
        for index, read_symbol in enumerate(self.read_symbols):
            # positions symbols to be stacked on top of the reflexive arrow.
            read_symbol.move_to(center_of_arc).shift(UP * radius + [0, index + 1, 0])

    def calculate_direction_of_arrow_label(
        self, normal_vector_choice: int = 1
    ) -> list[float]:
        """Return the normal direction used to offset the arrow label.

        Parameters
        ----------
        normal_vector_choice : int
            Side of the transition line on which the symbol label should be placed.
        """

        x1 = self.transition_from.get_x()
        y1 = self.transition_from.get_y()

        x2 = self.transition_to.get_x()
        y2 = self.transition_to.get_y()

        difference_of_x = x2 - x1
        difference_of_y = y2 - y1

        normalised_values = normalize([difference_of_x, difference_of_y])

        # calculate normal of the line
        normal_vectors = {
            0: [-normalised_values[1], normalised_values[0], -1],
            1: [normalised_values[1], -normalised_values[0], -1],
        }

        return normal_vectors[normal_vector_choice]

    def position_text(self, buffer: float) -> None:
        """Place each read-symbol label next to the transition arrow.

        Parameters
        ----------
        buffer
            Padding distance used to separate multiple labels stacked around the arrow.
        """
        # Obtain coordinates for the centre of the line
        x1 = None
        y1 = None
        if type(self.transition_from) == list:
            x1 = self.transition_from[0]
            y1 = self.transition_from[1]
        else:
            x1 = self.transition_from.get_x()
            y1 = self.transition_from.get_y()

        x2 = self.transition_to.get_x()
        y2 = self.transition_to.get_y()

        # midpoint
        c1 = (x1 + x2) / 2
        c2 = (y1 + y2) / 2

        # normal_offset = [x for x in self.calculate_direction_of_arrow_label()]
        normal_offset = self.calculate_direction_of_arrow_label()
        for index, read_symbol in enumerate(self.read_symbols):
            # if there are multiple symbols then stack them
            read_symbol_offset_y = normal_offset[1] * (index + 1 * buffer)
            read_symbol_offset_x = normal_offset[0] * (index + 1 * buffer)
            # read_symbol_offset_x = normal_offset[0] * buffer
            # directional offset from the arrow line
            read_symbol_offset = [read_symbol_offset_x, read_symbol_offset_y]

            # apply offset to centre of line coordinates
            text_coordinates = [x + y for x, y in zip([c1, c2, 0], read_symbol_offset)]

            # apply offset coordinates to the mobject.
            read_symbol.set_x(text_coordinates[0])
            read_symbol.set_y(text_coordinates[1])

    def convert_straight_arrow_to_curved_arrow(self) -> None:
        """
        Converts a straight arrow transition to a curved arrow transition.
        This method is primarily used when there are two opposing transitions
        between two states.
        """
        # remove existing manim arrow
        self.remove(self.arrow)

        # remove manim read symbols
        for read_symbol in self.read_symbols:
            self.remove(read_symbol)

        # create new curved arrow and read symbols
        self.construct_curved_arrow()
        self.add(self.arrow, *self.read_symbols)

    def construct_curved_arrow(self, buffer: float = 0.5) -> None:
        # create a straight line and use the points locations to create curved arrow
        """Construct a curved arrow and position its read-symbol labels.

        Parameters
        ----------
        buffer
            Extra offset applied to stacked labels near the arc.
        """
        temp_arrow = Arrow(self.transition_from, self.transition_to)
        from_point = temp_arrow.start
        to_point = temp_arrow.end

        self.arrow = CurvedArrow(from_point, to_point)

        chord_center_x = (from_point[0] + to_point[0]) / 2
        chord_center_y = (from_point[1] + to_point[1]) / 2

        cx = self.arrow.get_arc_center()[0]
        cy = self.arrow.get_arc_center()[1]

        # get the point of curved arrow
        angle = math.atan2(chord_center_y - cy, chord_center_x - cx)
        temp_circle = Circle(self.arrow.radius, color=RED)
        temp_circle.move_arc_center_to(self.arrow.get_arc_center())
        center_point = temp_circle.point_at_angle(angle)

        normal_offset = self.calculate_direction_of_arrow_label()

        for index, read_symbol in enumerate(self.read_symbols):
            # if there are multiple symbols then stack them
            read_symbol_offset_y = normal_offset[1] * (index + 1 * buffer)

            # read_symbol_offset_x = normal_offset[0] * buffer
            read_symbol_offset_x = normal_offset[0] * (index + 1 * buffer)
            # directional offset from the arrow line
            read_symbol_offset = [read_symbol_offset_x, read_symbol_offset_y]

            # apply offset to centre of line coordinates
            text_coordinates = [
                x + y
                for x, y in zip(
                    [center_point[0], center_point[1], 0], read_symbol_offset
                )
            ]

            # apply offset coordinates to the mobject.
            read_symbol.set_x(text_coordinates[0])
            read_symbol.set_y(text_coordinates[1])

    def check_transition_read_symbols(self, token: MathTex) -> bool:
        """Return whether the transition contains a read symbol matching the provided token.

        Parameters
        ----------
        token
            Token whose LaTeX representation is compared against the transition labels.
        """
        for read_symbol in self.read_symbols:
            if read_symbol.tex_string == token.tex_string:
                return True  # There is a read_symbol that matches the given token
        return False  # There are no read_symbols that match the given token

    def rotate_symbols_parallel_to_arrow(self) -> None:
        """Rotate all read symbols so they are aligned parallel to the arrow."""
        for read_symbol in self.read_symbols:
            slope = self.calculate_slope_of_line()

            angle_between_slope_and_x_axis = math.atan(slope)
            read_symbol.rotate(angle_between_slope_and_x_axis)

    def calculate_slope_of_line(self) -> float:
        """Calculate the slope of the arrow line.

        Returns
        -------
        float
            The slope (``dy/dx``) of the arrow, or ``0`` if the arrow is
            degenerate (reflexive case).
        """
        start_point = self.arrow.get_start()
        end_point = self.arrow.get_end()
        x1 = start_point[0]
        x2 = end_point[0]
        y1 = start_point[1]
        y2 = end_point[1]

        if x1 == x2 and y2 == y1:  # reflexive arrow is parallel to x axis
            return 0

        return (y2 - y1) / (x2 - x1)


class ManimPushDownAutomatonTransition(ManimTransition):
    """Visual transition arrow for pushdown automata.

    Extends :class:`~manim_extensions.automata.mobjects.manim_transition.ManimTransition` to support stack-operation rules in
    addition to input symbols.  When the source and target states are
    identical, a reflexive loop is drawn; when a reverse transition already
    exists, both arrows are rendered as curved paths.

    Parameters
    ----------
    transition_from : ManimState
        Source state of the transition.
    transition_to : ManimState
        Target state of the transition.
    rules : list
        Pushdown automaton rules associated with this transition.
    parent_automaton : ManimAutomaton
        The owning automaton instance.
    animation_style : dict
        Animation configuration.
    font_size : int, optional
        Font size for the rule labels.
    buffer : int, optional
        Spacing buffer for label positioning.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: ManimPushDownAutomatonTransitionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_pushdown_automaton import ManimPushDownAutomaton

       class ManimPushDownAutomatonTransitionExample(Scene):
           def construct(self):
               pda = ManimPushDownAutomaton()
               self.add(pda)
    """

    def __init__(
        self,
        transition_from: ManimState,
        transition_to: ManimState,
        rules: list[object],
        parent_automaton: "ManimAutomaton",
        animation_style: dict[str, Any],
        font_size: int = 100,
        buffer: int = 1,
        **kwargs: Any,
    ) -> None:
        """Initialize the ManimPushDownAutomatonTransition instance."""
        Transition.__init__(self, transition_from, transition_to)
        self.circle = None
        # manim settings for animations and colors
        self.animation_style = animation_style
        # store tex mobjects of read_symbols for transitions
        self.read_symbols = []
        # list of PushDownAutomatonRule
        self.rules = rules

        self.buffer = buffer

        # create manim read symbols for transition
        for rule in rules:
            # Create mobjects of read_symbol
            self.read_symbols.append(MathTex(rule.__str__(), font_size=font_size))

        if (
            self.transition_from == self.transition_to
        ):  # create transition that points to itself
            position_1, position_2 = self.calculate_circle_vertices()
            self.create_reflexive_arrow(position_1, position_2)
        elif (
            self.transition_to.get_transition_by_transition_to_state_id(
                self.transition_from.id
            )
            is not None
        ):  # check if there already exists an arrow pointing the opposite way
            # pre-exising arrow transition converted to curved arrow
            opposite_transition = (
                self.transition_to.get_transition_by_transition_to_state_id(
                    self.transition_from.id
                )
            )
            opposite_transition.convert_straight_arrow_to_curved_arrow()

            # create this(self) arrow
            self.construct_curved_arrow()

        else:  # transition_from ----> transition_to
            self.arrow = Arrow(transition_from, transition_to, buff=0)
            self.position_text(self.buffer)  # - this is causing errors

        VGroup.__init__(self, self.arrow, *self.read_symbols, **kwargs)