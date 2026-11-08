# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for straight-line intersection helpers."""

import pytest
from manim import DOWN, LEFT, ORIGIN, RIGHT, UP, Line

from manim_extensions.geometry import VMobjectInt


def test_crossing_lines():
    assert len(VMobjectInt(Line(LEFT * 2, RIGHT * 2), Line(UP * 2, DOWN * 2))) == 1


def test_lines_touching_at_an_endpoint():
    left = Line([-2.0, 0.0, 0.0], [0.0, 0.0, 0.0])
    right = Line([0.0, 0.0, 0.0], [2.0, 0.0, 0.0])

    assert len(VMobjectInt(left, right)) == 1


def test_collinear_overlapping_lines():
    first = Line(LEFT * 2, ORIGIN)
    second = Line(ORIGIN, RIGHT * 2)

    assert len(VMobjectInt(first, second)) == 1


def test_parallel_lines_never_meet():
    first = Line(LEFT * 2 + UP, RIGHT * 2 + UP)
    second = Line(LEFT * 2 + DOWN, RIGHT * 2 + DOWN)

    assert VMobjectInt(first, second) == []
