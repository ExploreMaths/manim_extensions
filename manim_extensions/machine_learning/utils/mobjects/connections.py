# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Network connection visualization utilities."""


import numpy as np
from manim import (
    Animation,
    AnimationGroup,
    Arrow,
    DOWN,
    LEFT,
    Line,
    ManimColor,
    Mobject,
    ORANGE,
    RIGHT,
    ShowPassingFlash,
    UP,
    VGroup,
    WHITE,
    override_animation,
)
from numpy.typing import NDArray


class NetworkConnection(VGroup):
    """
    This class allows for creating connections
    between locations in a network.

    Parameters
    ----------
    start_mobject : Mobject
        Mobject where the start of the connection is from.
    end_mobject : Mobject
        Mobject where the end of the connection goes to.
    arc_direction : str, optional
        Direction that the connection arcs; one of "straight", "up", "down",
        "left", "right", by default "straight".
    buffer : float, optional
        Amount of space between the connection and the mobjects at the ends,
        by default 0.0.
    arc_distance : float, optional
        Distance from start and end mobject that the arc bends, by default 0.2.
    stroke_width : float, optional
        Stroke width of the connection, by default 2.0.
    color : ManimColor, optional
        Color of the connection, by default WHITE.
    active_color : ManimColor, optional
        Color of active animations for this mobject, by default ORANGE.

    Examples
    --------
    .. manim:: NetworkConnectionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.utils.mobjects.connections import NetworkConnection

       class NetworkConnectionExample(Scene):
           def construct(self):
               start = Dot(LEFT * 2).scale(1.5)
               end = Dot(RIGHT * 2).scale(1.5)
               connection = NetworkConnection(start, end)
               content = VGroup(start, end, connection)
               content.scale_to_fit_width(10).move_to(ORIGIN)
               self.add(content)
    """

    direction_vector_map: dict[str, NDArray[np.float64]] = {
        "up": UP,
        "down": DOWN,
        "left": LEFT,
        "right": RIGHT,
    }

    def __init__(
        self,
        start_mobject: Mobject,
        end_mobject: Mobject,
        arc_direction: str = "straight",
        buffer: float = 0.0,
        arc_distance: float = 0.2,
        stroke_width: float = 2.0,
        color: ManimColor = WHITE,
        active_color: ManimColor = ORANGE,
    ) -> None:
        """Initialize the NetworkConnection instance."""
        super().__init__()
        assert arc_direction in ["straight", "up", "down", "left", "right"]
        self.start_mobject = start_mobject
        self.end_mobject = end_mobject
        self.arc_direction = arc_direction
        self.buffer = buffer
        self.arc_distance = arc_distance
        self.stroke_width = stroke_width
        self.color = color
        self.active_color = active_color

        self.make_mobjects()

    def make_mobjects(self) -> None:
        """Makes the submobjects."""
        if self.start_mobject.get_center()[0] < self.end_mobject.get_center()[0]:
            left_mobject = self.start_mobject
            right_mobject = self.end_mobject
        else:
            right_mobject = self.start_mobject
            left_mobject = self.end_mobject
        if self.arc_direction == "straight":
            # Make an arrow
            self.straight_arrow = Arrow(
                start=left_mobject.get_right() + np.array([self.buffer, 0.0, 0.0]),
                end=right_mobject.get_left() + np.array([-1 * self.buffer, 0.0, 0.0]),
                color=WHITE,
                fill_color=WHITE,
                stroke_opacity=1.0,
                buff=0.0,
            )
            self.add(self.straight_arrow)
        else:
            # Figure out the direction of the arc
            direction_vector = NetworkConnection.direction_vector_map[
                self.arc_direction
            ]
            # Based on the position of the start and end layer, and direction
            # figure out how large to make each line
            # Whichever mobject has a critical point the farthest
            # distance in the direction_vector direction we will use that end
            left_mobject_critical_point = left_mobject.get_critical_point(direction_vector)
            right_mobject_critical_point = right_mobject.get_critical_point(direction_vector)
            # Take the dot product of each
            # These dot products correspond to the orthogonal projection
            # onto the direction vectors
            left_dot_product = np.dot(
                left_mobject_critical_point, 
                direction_vector
            )
            right_dot_product = np.dot(
                right_mobject_critical_point, 
                direction_vector
            )
            extra_distance = abs(left_dot_product - right_dot_product)
            # The difference between the dot products 
            if left_dot_product < right_dot_product:
                right_is_farthest = False
            else:
                right_is_farthest = True
            # Make the start arc piece
            start_line_start = left_mobject.get_critical_point(direction_vector)
            start_line_start += direction_vector * self.buffer
            start_line_end = start_line_start + direction_vector * self.arc_distance
            if not right_is_farthest:
                start_line_end = start_line_end + direction_vector * extra_distance
            self.start_line = Line(
                start_line_start,
                start_line_end,
                color=self.color,
                stroke_width=self.stroke_width,
            )
            # Make the end arc piece with an arrow
            end_line_end = right_mobject.get_critical_point(direction_vector)
            end_line_end += direction_vector * self.buffer
            end_line_start = end_line_end + direction_vector * self.arc_distance
            if right_is_farthest:
                end_line_start = end_line_start + direction_vector * extra_distance

            self.end_arrow = Arrow(
                start=end_line_start,
                end=end_line_end,
                color=WHITE,
                fill_color=WHITE,
                stroke_opacity=1.0,
                buff=0.0,
            )
            # Make the middle arc piece
            self.middle_line = Line(
                start_line_end,
                end_line_start,
                color=self.color,
                stroke_width=self.stroke_width,
            )
            # Add the mobjects
            self.add(
                self.start_line,
                self.middle_line,
                self.end_arrow,
            )

    @override_animation(ShowPassingFlash)
    def _override_passing_flash(
        self, run_time: float = 1.0, time_width: float = 0.2
    ) -> Animation:
        """Passing flash animation."""
        if self.arc_direction == "straight":
            return ShowPassingFlash(
                self.straight_arrow.copy().set_color(self.active_color),
                time_width=time_width,
            )
        else:
            # Animate the start line
            start_line_animation = ShowPassingFlash(
                self.start_line.copy().set_color(self.active_color),
                time_width=time_width,
            )
            # Animate the middle line
            middle_line_animation = ShowPassingFlash(
                self.middle_line.copy().set_color(self.active_color),
                time_width=time_width,
            )
            # Animate the end line
            end_line_animation = ShowPassingFlash(
                self.end_arrow.copy().set_color(self.active_color),
                time_width=time_width,
            )

            return AnimationGroup(
                start_line_animation,
                middle_line_animation,
                end_line_animation,
                lag_ratio=1.0,
                run_time=run_time,
            )
