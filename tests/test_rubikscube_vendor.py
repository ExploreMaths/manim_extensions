# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


import pytest

from manim_extensions.rubikscube import RubiksCube
from manim_extensions.rubikscube.cube_utils import (
    get_all_states,
    get_cubie_colors_from_state,
)


def test_rubikscube_constructor_and_fields():
    cube = RubiksCube(dim=2)

    assert cube.dimensions == 2
    assert cube.cubies.shape == (2, 2, 2)
    assert len(cube.colors) == 6
    assert cube.x_offset is not None
    assert cube.y_offset is not None
    assert cube.z_offset is not None

    cubie = cube.cubies[0, 0, 0]
    assert cubie.position.shape == (3,)
    assert hasattr(cubie, "faces")
    assert len(cubie.faces) > 0


def test_rubikscube_set_state():
    cube = RubiksCube(dim=2)
    state = "U" * 4 + "R" * 4 + "F" * 4 + "D" * 4 + "L" * 4 + "B" * 4

    cube.set_state(state)

    assert cube.get_face("U").shape[0] == 4
    assert cube.get_face("R").shape[0] == 4
    assert cube.get_face("F").shape[0] == 4
    assert cube.get_face("D").shape[0] == 4
    assert cube.get_face("L").shape[0] == 4
    assert cube.get_face("B").shape[0] == 4


def test_rubikscube_solve_by_kociemba():
    cube = RubiksCube()
    solved_state = "U" * 9 + "R" * 9 + "F" * 9 + "D" * 9 + "L" * 9 + "B" * 9
    solved = cube.solve_by_kociemba(solved_state)

    assert isinstance(solved, list)
    assert all(isinstance(move, str) for move in solved)


def test_get_cubie_colors_from_state_splits_faces():
    state = "U" * 9 + "R" * 9 + "F" * 9 + "D" * 9 + "L" * 9 + "B" * 9

    faces = get_cubie_colors_from_state(state)

    assert len(faces) == 6
    assert [len(face) for face in faces] == [9] * 6
    assert faces[0] == ["U"] * 9
    assert faces[5] == ["B"] * 9


def test_get_cubie_colors_from_state_rejects_invalid_length():
    with pytest.raises(ValueError):
        get_cubie_colors_from_state("U" * 53)


def test_get_all_states_round_trips_through_set_state():
    state = "BBFBUBUDFDDUURDDURLLLDFRBFRLLFFDLUFBDUBBLFFUDLRRRBLURR"
    cube = RubiksCube()
    cube.set_state(state)

    assert get_all_states(cube) == state


def test_get_all_states_round_trips_for_two_dimensional_cube():
    state = "U" * 4 + "R" * 4 + "F" * 4 + "D" * 4 + "L" * 4 + "B" * 4
    cube = RubiksCube(dim=2)
    cube.set_state(state)

    assert get_all_states(cube) == state
