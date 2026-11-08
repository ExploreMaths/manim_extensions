# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the interpolation steps of custom animations."""

import pytest
from manim import Rectangle, Text, VMobject, tempconfig

from manim_extensions.animations import LaggedCreation, PassingRectangle, TypeWriter


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_typewriter_reveals_characters():
    animation = TypeWriter(Text("abcd"))

    animation.interpolate_mobject(1.0)

    assert all(char.get_fill_opacity() == 1 for char in animation.mobject.submobjects)


def test_passing_rectangle_sweeps():
    animation = PassingRectangle(Rectangle(width=2.0, height=1.0))

    animation.interpolate_mobject(0.5)

    assert animation.mobject.width > 0


def test_lagged_creation_bounds():
    animation = LaggedCreation(VMobject())

    start, end = animation.get_bounds(0.5)

    assert start <= end


def test_lagged_creation_interpolates_submobject():
    target = VMobject()
    target.set_points_as_corners([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]])
    animation = LaggedCreation(VMobject())

    result = animation.interpolate_submobject(target, target.copy(), 0.75)

    assert result is animation
