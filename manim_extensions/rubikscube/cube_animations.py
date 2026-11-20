# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

from typing import cast, Any
from typing import Any

"""Rubik's Cube animations for Manim.

This module provides animations for Rubik's Cube manipulations.

"""

from manim import Animation, Mobject, PI, VGroup
from .cube import RubiksCube
from .cube_utils import get_axis_from_face


class CubeMove(Animation):
    """Animate a single face turn on a :class:`~manim_extensions.rubikscube.cube.RubiksCube`.

    :class:`~manim_extensions.rubikscube.cube_animations.CubeMove` is a :class:`~manim.animation.animation.Animation` subclass
    that rotates the cubies of one face around the appropriate axis by
    ``90°`` or ``180°``, clockwise or counter-clockwise depending on the
    face notation.

    Parameters
    ----------
    mobject
        The cube to animate.
    face
        Face notation (``R``, ``L``, ``U``, ``D``, ``F``, ``B``) with
        optional ``2`` for a double turn and/or ``'`` for counter-clockwise.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.animation.animation.Animation`.

    Examples
    --------
    .. manim:: CubeRotation

       from manim import *
       from manim_extensions.rubikscube import RubiksCube
       from manim_extensions.rubikscube.cube_animations import CubeMove

       class CubeRotation(ThreeDScene):
           def construct(self):
               cube = RubiksCube().scale(0.6)
               self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                                frame_center=cube.get_center())
               self.play(FadeIn(cube))
               # CubeMove() takes the cube and the face to rotate. The possible
               # faces are F, B, U, D, L, and R. An inverse move is preceded by a
               # single quote ('), a double move is followed by "2". If a move is
               # too fast or too slow, run_time can be provided (in seconds):
               self.play(CubeMove(cube, "F"))
               self.play(CubeMove(cube, "U2"), run_time=2)
               self.play(CubeMove(cube, "R'"))
               self.wait()
    """

    def __init__(self, mobject: Mobject, face: str, **kwargs: Any) -> None:
        self.axis = get_axis_from_face(face[0])
        self.face = face
        self.angle = PI / 2 if ("R" in face or "F" in face or "D" in face) else -PI / 2
        self.angle = self.angle if "2" not in face else self.angle * 2
        self.angle = -self.angle if "'" in face else self.angle
        super().__init__(mobject, **kwargs)

    def create_starting_mobject(self) -> RubiksCube:
        """Create a copy of the cube as the starting state for the animation.

        Returns
        -------
            A copy of the cube with indices initialised if needed.
        """
        starting_mobject = self.mobject.copy()
        if cast(Any, starting_mobject).indices == {}:
            cast(Any, starting_mobject).set_indices()
        return cast("RubiksCube", starting_mobject)

    def interpolate_mobject(self, alpha: float) -> Any:
        """Interpolate the cube rotation at progress ``alpha``.

        Parameters
        ----------
        alpha
            Animation progress between ``0`` and ``1``.
        """
        self.mobject.become(self.starting_mobject)

        VGroup(*cast(Any, self.mobject).get_face(self.face[0])).rotate(
            self.rate_func(alpha) * self.angle, self.axis
        )

    def finish(self) -> Any:
        """Finalise the cube move and update face indices after animation completes."""
        super().finish()
        cast(Any, self.mobject).adjust_indices(
            cast(Any, self.mobject).get_face(self.face[0], False)
        )
