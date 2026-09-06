# SPDX-FileCopyrightText: 2024 Matheart
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

r"""Pendulums.

:class:`~manim_extensions.physics.rigid_mechanics.pendulum.MultiPendulum` and :class:`~manim_extensions.physics.rigid_mechanics.pendulum.Pendulum` both stem from the
:py:mod:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics` feature.

"""

from __future__ import annotations

from manim import *
from typing import Iterable

import numpy as np
import pymunk

from .rigid_mechanics import SpaceScene

__all__ = [
    "Pendulum",
    "MultiPendulum",
    "SpaceScene",
]


class MultiPendulum(VGroup):
    """A multi-segment pendulum driven by pymunk physics.

    The pendulum is constructed from one or more bobs connected by rigid
    rods to a fixed pivot point.  When :meth:`~manim_extensions.physics.rigid_mechanics.pendulum.Pendulum.start_swinging` is called the
    bobs are turned into pymunk rigid bodies and the scene's simulation
    updater drives the motion.

    Parameters
    ----------
    bobs : iterable of numpy.ndarray
        Positions of the pendulum bobs from the pivot outward.
    pivot_point : numpy.ndarray, optional
        Position of the fixed pivot.  Defaults to ``UP * 2``.
    rod_style : dict, optional
        Keyword arguments forwarded to the :class:`~manim.mobject.geometry.line.Line`
        constructor used for each rod.
    bob_style : dict, optional
        Keyword arguments forwarded to the :class:`~manim.mobject.geometry.arc.Circle`
        constructor used for each bob.
    **kwargs
        Additional parameters for :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: MultiPendulumExample

       from manim import *
       from manim_extensions.physics.rigid_mechanics.pendulum import (
           MultiPendulum, SpaceScene,
       )

       class MultiPendulumExample(SpaceScene):
           def construct(self):
               pendulum = MultiPendulum(RIGHT, LEFT)
               self.play(FadeIn(pendulum))
               self.make_rigid_body(*pendulum.bobs)
               pendulum.start_swinging()
               self.add(
                   TracedPath(
                       pendulum.bobs[-1].get_center,
                       stroke_color=BLUE,
                   )
               )
               self.wait(5)
    """

    def __init__(
        self,
        *bobs: Iterable[np.ndarray],
        pivot_point: np.ndarray = UP * 2,
        rod_style: dict = {},
        bob_style: dict = {
            "radius": 0.1,
            "color": ORANGE,
            "fill_opacity": 1,
        },
        **kwargs,
    ) -> None:
        """Initialize MultiPendulum."""
        self.pivot_point = pivot_point
        self.bobs = VGroup(*[Circle(**bob_style).move_to(i) for i in bobs])
        self.pins = [pivot_point]
        self.pins += bobs
        self.rods = VGroup()
        self.rods += Line(self.pivot_point, self.bobs[0].get_center(), **rod_style)
        self.rods.add(
            *(
                Line(
                    self.bobs[i].get_center(),
                    self.bobs[i + 1].get_center(),
                    **rod_style,
                )
                for i in range(len(bobs) - 1)
            )
        )

        super().__init__(**kwargs)
        self.add(self.rods, self.bobs)

    def _make_joints(
        self, mob1: Mobject, mob2: Mobject, spacescene: SpaceScene
    ) -> None:
        """Create a pymont pin joint between two bodies (or a body and a fixed point).

        Parameters
        ----------
        mob1 : Mobject
            First body mobject (must have a ``body`` attribute).
        mob2 : Mobject or numpy.ndarray
            Second body mobject, or a fixed point in space.
        spacescene : SpaceScene
            The physics scene to which the joint is added.
        """
        a = mob1.body
        if type(mob2) == np.ndarray:
            b = pymunk.Body(body_type=pymunk.Body.STATIC)
            b.position = mob2[0], mob2[1]
        else:
            b = mob2.body
        joint = pymunk.PinJoint(a, b)
        spacescene.space.space.add(joint)

    def _redraw_rods(self, mob: Line, pins, i):
        """Update a rod line to connect the positions of two consecutive pins.

        Parameters
        ----------
        mob : Line
            The rod line mobject to update.
        pins : list
            List of pin joints or positions.
        i : int
            Index of the first pin; the rod connects ``pins[i]`` to ``pins[i+1]``.
        """
        try:
            x, y, _ = pins[i]
        except:
            x, y = pins[i].body.position
        x1, y1 = pins[i + 1].body.position
        mob.put_start_and_end_on(
            RIGHT * x + UP * y,
            RIGHT * x1 + UP * y1,
        )

    def start_swinging(self) -> None:
        """Start swinging."""
        spacescene: SpaceScene = self.bobs[0].spacescene
        pins = [self.pivot_point]
        pins += self.bobs

        for i in range(len(pins) - 1):
            self._make_joints(pins[i + 1], pins[i], spacescene)
            self.rods[i].add_updater(lambda mob, i=i: self._redraw_rods(mob, pins, i))

    def end_swinging(self) -> None:
        """Stop swinging."""
        spacescene = self.bobs[0].spacescene
        spacescene.stop_rigidity(self.bobs)


class Pendulum(MultiPendulum):
    """A simple single-bob pendulum driven by pymunk physics.

    This is a convenience subclass of :class:`~manim_extensions.physics.rigid_mechanics.pendulum.MultiPendulum` that creates a
    single-bob pendulum from a length and initial deflection angle.

    Parameters
    ----------
    length : float, optional
        Length of the pendulum rod.  Defaults to ``3.5``.
    initial_theta : float, optional
        Initial angle of deviation from the vertical, in radians.
        Defaults to ``0.3``.
    pivot_point : numpy.ndarray, optional
        Position of the fixed pivot.  Defaults to ``UP * 2``.
    rod_style : dict, optional
        Forwarded to the :class:`~manim.mobject.geometry.line.Line` constructor.
    bob_style : dict, optional
        Forwarded to the :class:`~manim.mobject.geometry.arc.Circle` constructor.
    **kwargs
        Additional parameters for :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: PendulumExample

       from manim import *
       from manim_extensions.physics.rigid_mechanics.pendulum import (
           Pendulum, SpaceScene,
       )

       class PendulumExample(SpaceScene):
           def construct(self):
               pendulums = VGroup(
                   *[Pendulum(i) for i in np.linspace(1, 5, 7)]
               )
               self.play(FadeIn(pendulums))
               for pendulum in pendulums:
                   self.make_rigid_body(*pendulum.bobs)
                   pendulum.start_swinging()
               self.wait(5)
    """

    def __init__(
        self,
        length=3.5,
        initial_theta=0.3,
        pivot_point=UP * 2,
        rod_style={},
        bob_style={
            "radius": 0.25,
            "color": ORANGE,
            "fill_opacity": 1,
        },
        **kwargs,
    ):
        """Initialize Pendulum."""
        self.length = length
        self.pivot_point = pivot_point

        point = self.pivot_point + (
            RIGHT * np.sin(initial_theta) * length
            + DOWN * np.cos(initial_theta) * length
        )
        super().__init__(
            point,
            pivot_point=self.pivot_point,
            rod_style=rod_style,
            bob_style=bob_style,
            **kwargs,
        )
