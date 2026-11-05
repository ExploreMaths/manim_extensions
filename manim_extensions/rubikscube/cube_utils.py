# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: implement the local state helpers get_cubie_colors_from_state and get_all_states

"""Utility functions for Rubik's Cube.

This module provides utility functions for Rubik's Cube operations.

"""

from typing import TYPE_CHECKING

import numpy as np
from manim.constants import DOWN, IN, LEFT, OUT, RIGHT, UP, X_AXIS, Y_AXIS, Z_AXIS
from manim.typing import Vector3D
from manim.utils.color import ManimColor

if TYPE_CHECKING:
    from .cube import RubiksCube  # noqa: F401


def get_axis_from_face(face: str) -> Vector3D:
    """Return the rotation axis corresponding to a Rubik's cube face.

    Parameters
    ----------
    face
        Face identifier. One of ``"F"`` (front), ``"B"`` (back), ``"U"`` (up),
        ``"D"`` (down), ``"L"`` (left), or ``"R"`` (right).

    Returns
    -------
        The axis vector (``X_AXIS``, ``Y_AXIS``, or ``Z_AXIS``) about which the
        specified face rotates.
    """
    if face == "F" or face == "B":
        return X_AXIS
    elif face == "U" or face == "D":
        return Z_AXIS
    else:
        return Y_AXIS


def get_direction_from_face(face: str) -> int:
    """Return the rotation direction for a given face.

    Parameters
    ----------
    face
        Face identifier (``"F"``, ``"B"``, ``"U"``, ``"D"``, ``"L"``, or ``"R"``).

    Returns
    -------
        ``1`` for clockwise, ``-1`` for counter-clockwise rotation
        when viewed from the face's perspective.
    """
    if face in ("F", "U", "L"):
        return 1
    return -1


def get_cubie_colors_from_state(state: str) -> list[list[str]]:
    """Split a facelet state string into one colour list per cube face.

    The state string uses the standard facelet notation accepted by
    :func:`~manim_extensions.rubikscube.cube.RubiksCube.set_state`: the
    faces appear in the order Up, Right, Front, Down, Left, Back, each
    contributing ``dim ** 2`` colour characters.

    Parameters
    ----------
    state
        Cube state string (e.g. from ``kociemba``).

    Returns
    -------
        Six lists of colour characters in Up, Right, Front, Down, Left,
        Back order.

    Raises
    ------
    ValueError
        Raised when the length of *state* is not a multiple of six or is
        empty.
    """
    if len(state) == 0 or len(state) % 6 != 0:
        raise ValueError(
            "A facelet state must contain the same number of colours per face."
        )
    face_size = len(state) // 6
    return [list(state[index * face_size : (index + 1) * face_size]) for index in range(6)]


def get_all_states(cube: "RubiksCube") -> str:
    """Return the current facelet state of the cube.

    The faces are read in the same order and orientation used by
    :meth:`~manim_extensions.rubikscube.cube.RubiksCube.set_state`, so the
    returned string round-trips through that method.

    Parameters
    ----------
    cube
        The cube whose state is queried.

    Returns
    -------
        Concatenated facelet string of all six faces.

    Raises
    ------
    ValueError
        Raised when a sticker colour does not match any of the cube colours.
    """
    face_tiles = {
        "U": np.rot90(cube.get_face("U", False), 2).flatten(),
        "R": np.rot90(np.flip(cube.get_face("R", False), (0, 1)), -1).flatten(),
        "F": np.rot90(np.flip(cube.get_face("F", False), 0)).flatten(),
        "D": np.rot90(np.flip(cube.get_face("D", False), 0), 2).flatten(),
        "L": np.rot90(np.flip(cube.get_face("L", False), 0)).flatten(),
        "B": np.rot90(np.flip(cube.get_face("B", False), (0, 1)), -1).flatten(),
    }
    color_to_letter = {
        ManimColor(color).to_hex(): letter
        for letter, color in zip("URFDLB", cube.colors)
    }

    state = ""
    for letter, tiles in face_tiles.items():
        for cubie in tiles:
            color = ManimColor(cubie.get_face(letter).get_fill_color()).to_hex()
            try:
                state += color_to_letter[color]
            except KeyError as exc:
                raise ValueError(
                    f"Sticker colour {color} does not match any cube colour."
                ) from exc

    return state


def get_type_of_cubie(dim: int, position: tuple[int, int, int]) -> str:
    """Classify a cubie by its position within the cube.

    Parameters
    ----------
    dim
        Size of the cube (e.g. ``3`` for a standard 3x3x3 cube).
    position
        :math:`(x, y, z)` Coordinates of the cubie.

    Returns
    -------
        One of ``"corner"``, ``"edge"``, or ``"center"`` depending on the
        cubie's location.
    """
    if (position[1] == 0 or position[1] == dim - 1) and (
        position[2] == 0 or position[2] == dim - 1
    ):
        return "corner"
    elif position[1] == 0 or position[1] == dim - 1:
        return "edge"
    else:
        return "center"


def get_faces_of_cubie(dim: int, position: tuple[int, int, int]) -> list:
    """Return the outward-facing directions for a cubie at a given position.

    Parameters
    ----------
    dim
        Size of the cube (e.g. ``3`` for a standard 3x3x3 cube).
    position
        :math:`(x, y, z)` Coordinates of the cubie.

    Returns
    -------
        A list of direction vectors (e.g. LEFT, RIGHT, UP, DOWN,
        ``IN``, ``OUT``) indicating which faces of the cubie are exposed on the
        cube's surface.
    """
    dim = dim - 1
    try:
        faces = {
            # Front corners
            (0, 0, 0): [LEFT, DOWN, IN],
            (0, 0, dim): [LEFT, DOWN, OUT],
            (0, dim, 0): [LEFT, UP, IN],
            (0, dim, dim): [LEFT, UP, OUT],
            # Back corners
            (dim, 0, 0): [RIGHT, DOWN, IN],
            (dim, 0, dim): [RIGHT, DOWN, OUT],
            (dim, dim, 0): [RIGHT, UP, IN],
            (dim, dim, dim): [RIGHT, UP, OUT],
        }
        return faces[position]
    except:
        x = position[0]
        y = position[1]
        z = position[2]

        if x == 0:
            if y == 0:
                return [DOWN, LEFT]
            elif y == dim:
                return [UP, LEFT]
            else:
                if z == 0:
                    return [IN, LEFT]
                elif z == dim:
                    return [OUT, LEFT]
                else:
                    return [LEFT]
        elif x == dim:
            if y == 0:
                return [DOWN, RIGHT]
            elif y == dim:
                return [UP, RIGHT]
            else:
                if z == 0:
                    return [IN, RIGHT]
                elif z == dim:
                    return [OUT, RIGHT]
                else:
                    return [RIGHT]
        else:
            if y == 0:
                if z == 0:
                    return [IN, DOWN]
                elif z == dim:
                    return [OUT, DOWN]
                else:
                    return [DOWN]
            elif y == dim:
                if z == 0:
                    return [IN, UP]
                elif z == dim:
                    return [OUT, UP]
                else:
                    return [UP]
            else:
                if z == 0:
                    return [IN]
                elif z == dim:
                    return [OUT]
                else:
                    return []
