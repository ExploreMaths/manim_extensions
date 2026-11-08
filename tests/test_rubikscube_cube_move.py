# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for cube rotation animations."""

import pytest
from manim import Scene, tempconfig

from manim_extensions.rubikscube import RubiksCube
from manim_extensions.rubikscube.cube_animations import CubeMove


@pytest.fixture()
def cube():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield RubiksCube().scale(0.6)


@pytest.mark.parametrize("face", ["F", "B", "U", "D", "L", "R", "U2", "R'"])
def test_cube_move_builds_animation(cube, face):
    animation = CubeMove(cube, face)

    assert animation.face == face
