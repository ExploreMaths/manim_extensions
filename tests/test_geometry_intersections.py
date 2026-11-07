# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the curve intersection and tangent helpers."""

import numpy as np
from manim import Circle, Square

from manim_extensions.geometry import TangentPoint, VMobjectInt


def test_vmobject_int_returns_mobject():
    result = VMobjectInt(Circle(), Square())

    assert isinstance(result, list)


def test_vmobject_int_circle_pair():
    first = Circle(radius=1).shift([-0.5, 0, 0])
    second = Circle(radius=1).shift([0.5, 0, 0])

    result = VMobjectInt(first, second)

    assert result is not None


def test_tangent_point_on_line():
    tangent = TangentPoint([0.5, 1.5, 0], [1.5, 0.5, 0], [-3, 0, 0], [3, 0, 0])

    assert np.allclose(tangent[1], 0.0, atol=1e-6)


def test_tangent_point_to_3d_conversion():
    tangent = TangentPoint([0, 2, 0], [2, 0, 0], [-3, 0, 0], [3, 0, 0])

    assert tangent.shape == (3,)
