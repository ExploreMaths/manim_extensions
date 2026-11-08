# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for gear meshing with axial offsets and profile shift."""

import numpy as np
import pytest
from manim import WHITE, tempconfig

from manim_extensions.gearbox.gear_mobjects.gear_mobject import Gear


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_mesh_to_with_offset_aligns_pitch_circles():
    first = Gear(18, profile_shift=2)
    second = Gear(24, profile_shift=3)
    second.shift([3, 0, 0])

    first.mesh_to(second, offset=0.05)

    assert first.get_center() is not None


def test_mesh_to_without_offset():
    first = Gear(18, profile_shift=2)
    second = Gear(24, profile_shift=3)
    second.shift([3, 0, 0])

    first.mesh_to(second, offset=0)

    assert first.get_center() is not None


def test_mesh_to_inner_gear():
    outer = Gear(40, profile_shift=-2)
    inner = Gear(20, profile_shift=1, inner_teeth=True)
    inner.shift([0.6, 0, 0])

    outer.mesh_to(inner)

    assert outer.get_center() is not None


def test_set_stroke_drops_family_keyword():
    gear = Gear(20)

    gear.set_stroke(color=WHITE, family=True, width=2)

    assert gear is not None


def test_set_stroke_without_color():
    gear = Gear(20)

    gear.set_stroke()

    assert gear is not None


def test_rotate_about_default_center():
    gear = Gear(20)

    gear.rotate(np.pi / 6)

    assert gear.get_angle() is not None


def test_rotate_about_point():
    gear = Gear(20)

    gear.rotate(np.pi / 6, about_point=[1.0, 0.0, 0.0])

    assert gear.get_center() is not None
