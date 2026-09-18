# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
"""Gear joint constraint for Pymunk.

This module provides the VGearJoint class for creating gear joint constraints.

"""

from __future__ import annotations

from manim import Arrow, BLUE, Line, Mobject, UP, np
from typing import Optional, TYPE_CHECKING
from . import VConstraint

from ...utils.deps import require

if TYPE_CHECKING:
    from pymunk import Space
    from pymunk.constraints import GearJoint


class VGearJoint(VConstraint):
    """A gear joint constrains the rotational speeds of two rigid bodies.
    It ensures that the two bodies rotate relative to each other at a fixed ratio,
    simulating the mechanical link of a gear system or a belt drive.

    Parameters
    ----------
    a_mob
        The first Mobject to be connected. Typically represents the driving
        or reference gear.
    b_mob
        The second Mobject to be connected. Its rotation is linked to `a_mob`
        based on the defined `ratio`.
    phase
        The angular offset (in radians) between the two bodies. Adjusts the
        initial relative orientation alignment.
    ratio
        The gear ratio. Defines how the angular velocity of `b_mob` relates to
        `a_mob`. For example, a ratio of 2.0 means `b_mob` rotates twice as
        fast as `a_mob`.
    indicator_line_class
        The class used to visualize the rotational direction or connection
        (defaults to `Arrow`). If set to `None`, no indicator will be rendered.
    indicator_line_config
        A dictionary defining the visual style of the indicator line,
        including `color` and `stroke_width`.
    indicator_length
        The visual length of the indicator arrows drawn on each Mobject.
    **kwargs
        Forwarded to the parent :class:`~manim_extensions.pymunk.constraints.constraint.VConstraint`.

    Examples
    --------
    .. manim:: VGearJointExample

        from manim import *
        from manim_extensions.pymunk import *

        class VGearJointExample(SpaceScene):
            def construct(self):
                # gear_2 (with the indicator arrow) spins 4x as fast as gear_1
                pivot_1 = Dot(LEFT * 2 + UP)
                pivot_2 = Dot(RIGHT * 2 + UP)
                gear_1 = Square().move_to(pivot_1)
                gear_2 = Square().move_to(pivot_2).scale(0.5)

                constraints = [
                    VPinJoint(pivot_1, gear_1),
                    VPinJoint(pivot_2, gear_2),
                    VGearJoint(gear_1, gear_2, ratio=4),
                ]

                self.play(FadeIn(pivot_1), FadeIn(pivot_2), FadeIn(gear_1), FadeIn(gear_2))
                self.add_static_body(pivot_1, pivot_2)
                self.add_dynamic_body(gear_1, angular_velocity=PI / 2)
                self.add_dynamic_body(gear_2)
                self.add_shapes_filter(pivot_1, pivot_2, gear_1, gear_2, group=2)
                self.add_constraints(*constraints)
                self.wait(5)

    """

    def __init__(
        self,
        a_mob: Mobject,
        b_mob: Mobject,
        phase: float = 0.0,
        ratio: float = 1.0,
        indicator_line_class: Optional[Line] = Arrow,
        indicator_line_config: dict = {
            "color": BLUE,
            "stroke_width": 2,
        },
        indicator_length: float = 0.4,
        **kwargs,
    ):
        """Initialize a gear joint constraint with two bodies, phase/ratio
        parameters, and optional rotational indicator arrows.
        """

        super().__init__(a_mob=a_mob, b_mob=b_mob, **kwargs)
        self.phase = phase
        self.ratio = ratio
        self.indicator_a = None
        self.indicator_b = None
        self.constraint: Optional[GearJoint] = None
        self.indicator_line_class = indicator_line_class
        self.indicator_line_config = indicator_line_config
        self.indicator_length = indicator_length

    def install(self, space: Space):
        """Verify the validity of constraint parameters."""

        GearJoint = require("physics", "pymunk").constraints.GearJoint

        a_body, b_body = self._get_bodies(
            "VGearJoint connected objects must have a Pymunk body."
        )

        self.constraint = GearJoint(a_body, b_body, self.phase, self.ratio)

        if self.indicator_line_class:
            self.indicator_a = self.indicator_line_class(
                self.a_mob.get_center(),
                self.a_mob.get_center() + UP * self.indicator_length,
                **self.indicator_line_config,
            )
            self.indicator_b = self.indicator_line_class(
                self.b_mob.get_center(),
                self.b_mob.get_center() + UP * self.indicator_length,
                **self.indicator_line_config,
            )
            self.add(self.indicator_a, self.indicator_b)

        self._finalize_install(space)

    def mob_updater(self, mob: Mobject, dt: float):
        """Visual control updater"""
        if not self.constraint:
            return

        a_body = self.constraint.a
        b_body = self.constraint.b

        if isinstance(self.indicator_a, Line):
            end_a = (
                self.a_mob.get_center()
                + np.array([np.cos(a_body.angle), np.sin(a_body.angle), 0])
                * self.indicator_length
            )

            self.indicator_a.put_start_and_end_on(self.a_mob.get_center(), end_a)

        if isinstance(self.indicator_b, Line):
            end_b = (
                self.b_mob.get_center()
                + np.array([np.cos(b_body.angle), np.sin(b_body.angle), 0])
                * self.indicator_length
            )

            self.indicator_b.put_start_and_end_on(self.b_mob.get_center(), end_b)