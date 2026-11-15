# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Smoke tests for the vendored ``manim-straightedge-compass`` package."""

import numpy as np
import pytest

from manim_extensions.straightedge_compass import (
    Compass,
    CompassDrawArc,
    EuclidScene,
    MarkedPoint,
    PencilTip,
    P,
    RulerDraw,
    Straightedge,
    circle_circle_intersection,
    distance,
    midpoint,
    other,
)


def test_point_helpers():
    assert np.allclose(P(1, 2), [1.0, 2.0, 0.0])
    assert distance(P(0, 0), P(3, 4)) == pytest.approx(5.0)
    assert np.allclose(midpoint(P(0, 0), P(2, 4)), [1.0, 2.0, 0.0])


def test_other_selects_the_other_point():
    a, b = P(1, 2), P(3, 4)
    result = other([a, b], a)
    assert np.allclose(result, b)


def test_circle_intersection_returns_two_points():
    points = circle_circle_intersection(P(0, 0), 1.0, P(0, 0), 1.0)
    assert points == []
    points = circle_circle_intersection(P(0, 0), 1.0, P(1, 0), 1.0)
    assert len(points) == 2


def test_public_classes_are_importable():
    for cls in (
        Compass,
        CompassDrawArc,
        Straightedge,
        PencilTip,
        RulerDraw,
        MarkedPoint,
        EuclidScene,
    ):
        assert isinstance(cls, type)
