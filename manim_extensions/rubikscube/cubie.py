# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Individual cubie used by the Rubik's Cube mobject."""

from manim.constants import *
from manim.utils.color import *
from manim import *
from .cube_utils import get_faces_of_cubie

import numpy as np


class Cubie(VGroup):
    """One small cube element composing a larger Rubik's Cube.

    Each cubie carries the six face tiles used to represent the cube state and
    owns its own 3D orientation within the parent :class:`~manim_extensions.rubikscube.cube.RubiksCube`.

    Parameters
    ----------
    x : int
        X coordinate of the cubie within the cube grid.
    y : int
        Y coordinate of the cubie within the cube grid.
    z : int
        Z coordinate of the cubie within the cube grid.
    dim : int
        Dimension of the parent cube (e.g. 3 for a 3x3x3 cube).
    colors : list
        Face colours in the order Up, Right, Front, Down, Left, Back.

    Examples
    --------
    .. manim:: CubieDocExample

       from manim import *
       from manim_extensions.rubikscube import RubiksCube

       class CubieDocExample(ThreeDScene):
           def construct(self):
               cube = RubiksCube().scale(0.6)
               self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                                frame_center=cube.get_center())
               self.play(FadeIn(cube))
               self.wait()
               self.play(Indicate(cube.cubies[0, 0, 0]))
               self.wait()
    """

    def __init__(self, x, y, z, dim, colors):
        """Initialize the Cubie instance."""
        self.dimensions = dim
        self.colors = colors
        self.position = np.array([x, y, z])
        self.faces = {}
        super().__init__()

    def get_position(self):
        """Return the cubie's current position in 3-D space.

        Returns
        -------
        numpy.ndarray
            The (x, y, z) position of the cubie.
        """
        return self.position

    def get_rounded_center(self):
        """Return the cubie's position with coordinates rounded to 3 decimal places.

        Returns
        -------
        tuple of float
            The rounded (x, y, z) coordinates.
        """
        return tuple(
            [round(self.get_x(), 3), round(self.get_y(), 3), round(self.get_z(), 3)]
        )

    def generate_points(self):
        """Construct the six square faces that correspond to this cubie."""
        faces = np.array(
            get_faces_of_cubie(
                self.dimensions, (self.position[0], self.position[1], self.position[2])
            )
        ).tolist()
        i = 0
        for vect in OUT, DOWN, LEFT, IN, UP, RIGHT:
            face = Square(side_length=2, shade_in_3d=True, stroke_width=3)
            if vect.tolist() in faces:
                face.set_fill(self.colors[i], 1)
            else:
                face.set_fill(BLACK, 1)

            face.flip()
            face.shift(2 * OUT / 2.0)
            face.apply_matrix(z_to_vector(vect))

            self.faces[tuple(vect)] = face
            self.add(face)
            i += 1

    def get_face(self, face):
        """Return the face tile corresponding to a cube label.

        Parameters
        ----------
        face
            Single-character face label: ``'F'`` (front), ``'B'`` (back),
            ``'R'`` (right), ``'L'`` (left), ``'U'`` (up), ``'D'`` (down).

        Returns
        -------
        Mobject
            The face tile mobject for the given label.
        """
        if face == "F":
            return self.faces[tuple(LEFT)]
        elif face == "B":
            return self.faces[tuple(RIGHT)]
        elif face == "R":
            return self.faces[tuple(DOWN)]
        elif face == "L":
            return self.faces[tuple(UP)]
        elif face == "U":
            return self.faces[tuple(OUT)]
        elif face == "D":
            return self.faces[tuple(IN)]

    def init_colors(self):
        """Apply fill, stroke, and background-stroke colours to the cubie."""
        self.set_fill(
            color=self.fill_color or self.color, opacity=self.fill_opacity, family=False
        )
        self.set_stroke(
            color=self.stroke_color or self.color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
            family=False,
        )
        self.set_background_stroke(
            color=self.background_stroke_color,
            width=self.background_stroke_width,
            opacity=self.background_stroke_opacity,
            family=False,
        )
