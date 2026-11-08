# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the OpenGL 3D cylinder, line and bonding geometry."""

import numpy as np
import pytest
from manim import BLUE, RIGHT, UP, tempconfig

from manim_extensions.chemistry.threeD.threedbond import ThreeDCylinder, ThreeDLine


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "opengl"}):
        yield


def test_cylinder_add_bases_creates_caps():
    cylinder = ThreeDCylinder(radius=0.2, height=1.0)

    cylinder.add_bases()

    assert cylinder.base_top is not None
    assert cylinder.base_bottom is not None


@pytest.mark.parametrize(
    "direction",
    [RIGHT, UP, [1.0, 1.0, 1.0], [0.0, 0.0, 1.0], [-1.0, -1.0, 0.0]],
)
def test_cylinder_direction_rotation(direction):
    cylinder = ThreeDCylinder(radius=0.2, height=1.0, direction=direction)

    assert cylinder.get_direction() is not None


def test_pointify_with_mobject_and_direction():
    line = ThreeDLine(start=[0, 0, 0], end=[1, 0, 0])

    assert line.pointify(line, direction=RIGHT) is not None


def test_pointify_with_mobject_without_direction():
    line = ThreeDLine(start=[0, 0, 0], end=[1, 0, 0])

    assert np.array_equal(line.pointify(line), line.get_center())


def test_pointify_with_raw_point():
    line = ThreeDLine(start=[0, 0, 0], end=[1, 0, 0])

    assert np.array_equal(line.pointify([0.0, 0.0, 0.0]), np.zeros(3))


def test_line_start_and_end():
    line = ThreeDLine(start=[0, 0, 0], end=[1, 0, 0])

    assert line.get_start() is not None
    assert line.get_end() is not None


def test_line_parallel_to_with_point():
    line = ThreeDLine(start=[0, 0, 0], end=[1, 0, 0])

    parallel = ThreeDLine.parallel_to(line, point=UP, color=BLUE)

    assert parallel.get_start() is not None


def test_line_perpendicular_to_with_point():
    line = ThreeDLine(start=[0, 0, 0], end=[1, 0, 0])

    perpendicular = ThreeDLine.perpendicular_to(line, point=UP, color=BLUE)

    assert perpendicular.get_start() is not None
