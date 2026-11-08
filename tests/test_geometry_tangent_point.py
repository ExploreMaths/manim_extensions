# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the circle tangent-point solver."""

import numpy as np

from manim_extensions.geometry import TangentPoint


def test_degenerate_line_returns_the_endpoint():
    point = TangentPoint([0, 0], [2, 0], [1, 1], [1, 1])

    assert point is not None
    assert np.allclose(point, [1, 1, 0])


def test_coincident_circle_points_have_no_solution():
    assert TangentPoint([1, 1], [1, 1], [0, 0], [2, 2]) is None


def test_3d_inputs_are_projected_onto_the_line():
    point = TangentPoint([0, 0, 1], [2, 0, 1], [1, 3, 0], [1, -3, 0])

    assert point is not None
    assert np.allclose(point[2], 0)


def test_collinear_geometry_has_no_tangent():
    assert TangentPoint([0, 0], [1, 0], [2, 0], [3, 0]) is None
