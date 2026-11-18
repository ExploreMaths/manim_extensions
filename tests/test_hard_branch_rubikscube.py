# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for Rubik's cube geometry and animation branches."""

import numpy as np
import pytest
from manim import tempconfig


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_cube_rejects_too_small_dimension():
    from manim_extensions.rubikscube import RubiksCube

    with pytest.raises(Exception, match="Dimension must be >= 2"):
        RubiksCube(dim=1)


def test_cubie_position_and_rounded_center():
    from manim_extensions.rubikscube import RubiksCube

    cube = RubiksCube(dim=2)
    cubie = cube.cubies[0, 0, 0]

    assert np.array_equal(cubie.get_position(), np.array([0, 0, 0]))
    assert isinstance(cubie.get_rounded_center(), tuple)
    assert len(cubie.get_rounded_center()) == 3


def test_cubie_type_classification():
    from manim_extensions.rubikscube.cube_utils import get_type_of_cubie

    assert get_type_of_cubie(3, (0, 0, 0)) == "corner"
    assert get_type_of_cubie(3, (1, 0, 1)) == "edge"
    assert get_type_of_cubie(3, (1, 1, 1)) == "center"


def test_face_direction_and_axis_mapping():
    from manim_extensions.rubikscube.cube_utils import (
        get_axis_from_face,
        get_direction_from_face,
    )

    assert get_direction_from_face("F") == 1
    assert get_direction_from_face("U") == 1
    assert get_direction_from_face("L") == 1
    assert get_direction_from_face("R") == -1
    assert get_axis_from_face("F") is get_axis_from_face("B")
    assert get_axis_from_face("U") is get_axis_from_face("D")
    assert get_axis_from_face("R") is get_axis_from_face("L")


def test_cube_move_lifecycle():
    from manim_extensions.rubikscube import CubeMove, RubiksCube

    cube = RubiksCube(dim=3)
    animation = CubeMove(cube, "R")
    starting = animation.create_starting_mobject()

    assert starting is not None
    initial = cube.copy()
    animation.begin()
    animation.interpolate_mobject(0.5)
    animation.finish()
    assert cube.indices
    assert initial is not cube


def test_cube_move_clockwise_double_and_prime_variants():
    from manim_extensions.rubikscube import CubeMove, RubiksCube

    cube = RubiksCube(dim=3)

    for face in ("F", "U", "L", "R", "D", "B", "R2", "R'"):
        animation = CubeMove(cube, face)
        assert animation.angle != 0


def test_grouped_depth_sorting_can_be_installed_again():
    from manim_extensions.rubikscube import _install_grouped_depth_sorting
    from manim.camera.three_d_camera import ThreeDCamera

    if hasattr(ThreeDCamera, "_manim_extensions_grouped_z_key"):
        del ThreeDCamera._manim_extensions_grouped_z_key
    _install_grouped_depth_sorting()

    assert ThreeDCamera._manim_extensions_grouped_z_key is True
    assert getattr(ThreeDCamera.get_mobjects_to_display, "__name__") == "_grouped"
