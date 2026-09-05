# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Ratchet joint constraint for Pymunk.

This module provides the VRatchetJoint class for creating ratchet joint constraints.

"""

from manim import *
from . import VConstraint
from pymunk.constraints import RatchetJoint
from pymunk import Space
from typing import Optional


class VRatchetJoint(VConstraint):
    """Initializes a Ratchet Joint constraint between two Mobjects.

    A Ratchet Joint acts like a rotary pawl, allowing relative rotation
    only in discrete increments and in one direction. It is perfect for
    simulating winding mechanisms, clockwork, or unidirectional gears.

    Parameters
    ----------
    a_mob
        The first Mobject (the base or reference body).
    b_mob
        The second Mobject (the body subject to the ratchet effect).
    phase
        The initial angular offset of the ratchet teeth.
    ratchet
        The angular distance between each "tooth" (in radians). For example,
        PI/2 means the joint locks at every 90-degree interval.
    indicator_line_class
        The Manim class used to visualize the current rotation or ratchet direction.
    indicator_line_config
        Configuration dictionary for the styling of the indicator arrow.
    indicator_line_length
        The visual length of the indicator line.
    connect_line_class
        The Manim class used to draw a line between the centers of the two
        objects. Set to None to disable.
    connect_line_config
        Configuration dictionary for the styling of the connection line.
    **kwargs
        Forwarded to the parent :class:`~manim_extensions.pymunk.constraints.constraint.VConstraint`.
        
    Examples
    --------
    .. manim:: VRatchetJointExample

        from manim import *
        from manim_extensions.pymunk import *

        class VRatchetJointExample(SpaceScene):
            def construct(self):
                # the driven square can only advance in PI-sized ratchet steps
                pivot_1 = Dot(UP * 2)
                pivot_2 = Dot(UP * 2 + RIGHT * 4)
                wheel_1 = Square().move_to(pivot_1)
                wheel_2 = Square().move_to(pivot_2)

                constraints = [
                    VPinJoint(pivot_1, wheel_1),
                    VPinJoint(pivot_2, wheel_2),
                    VRatchetJoint(wheel_1, wheel_2, phase=0, ratchet=PI),
                ]

                self.play(FadeIn(pivot_1), FadeIn(pivot_2), FadeIn(wheel_1), FadeIn(wheel_2))
                self.add_static_body(pivot_1, pivot_2)
                self.add_dynamic_body(wheel_1, angular_velocity=PI * 2)
                self.add_dynamic_body(wheel_2)
                self.add_shapes_filter(pivot_1, pivot_2, wheel_1, wheel_2, group=2)
                self.add_constraints(*constraints)
                self.wait(5)

    """

    def __init__(
        self,
        a_mob: Mobject,
        b_mob: Mobject,
        phase: float = 0.0,
        ratchet: float = PI / 2,
        indicator_line_class: Optional[Line] = Arrow,
        indicator_line_config: dict = {
            "color": BLUE,
            "stroke_width": 2,
        },
        indicator_line_length=0.4,
        connect_line_class: Optional[Line] = None,
        connect_line_config: dict = {"color": YELLOW, "stroke_width": 2},
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.a_mob = a_mob
        self.b_mob = b_mob

        self.phase = phase
        self.ratchet = ratchet

        self.indicator_line_class = indicator_line_class
        self.indicator_line_config = indicator_line_config
        self.indicator_line_length = indicator_line_length
        self.connect_line_class = connect_line_class
        self.connect_line_config = connect_line_config
        self.indicator_a = None
        self.indicator_b = None

        self.connect_line: Optional[VMobject] = None
        self.constraint: Optional[RatchetJoint] = None
        self.__check_data()

    def __check_data(self):
        """Verify the validity of constraint parameters."""
        if self.a_mob is None or self.b_mob is None:
            raise ValueError(
                "Constraints cannot be created without both a_mob and b_mob."
            )

        dist = np.linalg.norm(self.a_mob.get_center() - self.b_mob.get_center())

        if dist < 0.000001:
            if self.connect_line_class is not None:
                raise ValueError(
                    f"Points {self.a_mob} and {self.b_mob} are at the same location ({dist:.8f}). "
                    "Connecting them with a line makes no sense."
                )

    def install(self, space: Space):
        a_body = getattr(self.a_mob, "body", None)
        b_body = getattr(self.b_mob, "body", None)

        if not a_body or not b_body:
            raise ValueError("VRatchetJoint connected objects must have Pymunk bodies.")

        self.constraint = RatchetJoint(a_body, b_body, self.phase, self.ratchet)

        if self.connect_line_class:
            self.connect_line = self.connect_line_class(
                self.a_mob.get_center(),
                self.b_mob.get_center(),
                **self.connect_line_config,
            )
            self.add(self.connect_line)

        if self.indicator_line_class:
            self.indicator_a = self.indicator_line_class(
                self.a_mob.get_center(),
                self.a_mob.get_center() + UP * self.indicator_line_length,
                **self.indicator_line_config,
            )
            self.indicator_b = self.indicator_line_class(
                self.b_mob.get_center(),
                self.b_mob.get_center() + UP * self.indicator_line_length,
                **self.indicator_line_config,
            )
            self.add(self.indicator_a, self.indicator_b)

        space.add(self.constraint)

        self.add_updater(self.mob_updater)

    def mob_updater(self, mob, dt):
        """Visual control updater"""
        if not self.constraint:
            return
        a_body = self.constraint.a
        b_body = self.constraint.b

        if isinstance(self.connect_line, Line):
            self.connect_line.put_start_and_end_on(
                self.a_mob.get_center(), self.b_mob.get_center()
            )

        if isinstance(self.indicator_a, Line):
            end_a = (
                self.a_mob.get_center()
                + np.array([np.cos(a_body.angle), np.sin(a_body.angle), 0])
                * self.indicator_line_length
            )
            self.indicator_a.put_start_and_end_on(self.a_mob.get_center(), end_a)

        if isinstance(self.indicator_b, Line):
            end_b = (
                self.b_mob.get_center()
                + np.array([np.cos(b_body.angle), np.sin(b_body.angle), 0])
                * self.indicator_line_length
            )
            self.indicator_b.put_start_and_end_on(self.b_mob.get_center(), end_b)