# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for perpendicular signs and shortened lines."""

import pytest
from manim import AnimationGroup, DOWN, LEFT, RIGHT, UP, Line

from manim_extensions.mobjects import PerpendicularLine, PerpendicularSign, ShortenedLine


@pytest.fixture()
def base_line():
    return Line(LEFT * 3, RIGHT * 3)


def test_sign_with_default_corner_direction(base_line):
    perp = PerpendicularLine(UP * 1.5, base_line)

    sign = PerpendicularSign(base_line, perp)

    assert len(sign.submobjects) == 2


def test_sign_with_explicit_corner_direction(base_line):
    perp = PerpendicularLine(UP * 1.5, base_line)

    sign = PerpendicularSign(base_line, perp, corner_direction=DOWN)

    assert len(sign.submobjects) == 2


def test_sign_with_non_intersecting_lines_returns_empty():
    first = Line(LEFT * 2 + UP, RIGHT * 2 + UP)
    second = Line(LEFT * 2 + DOWN * 3, RIGHT * 2 + DOWN * 3)

    sign = PerpendicularSign(first, second)

    assert len(sign.submobjects) == 0


def test_shortened_line_degenerate_to_point():
    tiny = Line([0.0, 0.0, 0.0], [0.01, 0.0, 0.0])

    shortened = ShortenedLine(tiny, 0.1)

    assert shortened.get_length() == pytest.approx(0.0, abs=1e-6)


def test_shortened_line_trims_both_ends():
    full = Line(LEFT * 2, RIGHT * 2)

    shortened = ShortenedLine(full, 0.5)

    assert shortened.get_length() < full.get_length()
