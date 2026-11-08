# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for curve-curve intersection detection."""

from manim import Circle, Line, LEFT, RIGHT

from manim_extensions.geometry import VMobjectInt


def test_line_through_circle_has_two_intersections():
    points = VMobjectInt(Circle(radius=1), Line(LEFT * 2, RIGHT * 2))

    assert len(points) == 2


def test_overlapping_circles_have_two_intersections():
    points = VMobjectInt(Circle(radius=1), Circle(radius=1).shift([0.5, 0, 0]))

    assert len(points) == 2


def test_disjoint_shapes_have_no_intersections():
    points = VMobjectInt(Circle(radius=1), Circle(radius=1).shift([5, 0, 0]))

    assert points == []
