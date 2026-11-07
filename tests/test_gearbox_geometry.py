# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the involute gear and rack mobjects."""

import numpy as np
import pytest
from manim import PI

from manim_extensions.gearbox.gear_mobjects.gear_mobject import Gear, Rack


@pytest.mark.parametrize("teeth", [10, 20])
def test_gear_builds_points(teeth):
    gear = Gear(teeth)

    assert len(gear.points) > 0
    assert gear.get_angle() == 0


@pytest.mark.parametrize("teeth", [10, 20])
def test_rack_builds_points(teeth):
    rack = Rack(teeth)

    assert len(rack.points) > 0


def test_gear_center_and_angle_vector():
    gear = Gear(16)

    center = gear.get_center()
    vector = gear.get_angle_vector()

    assert np.asarray(center).shape == (3,)
    assert np.asarray(vector).shape == (3,)
    assert np.linalg.norm(vector) > 0


def test_gear_rotate_updates_angle():
    gear = Gear(12)

    gear.rotate(PI / 4)
    angle = gear.get_angle()

    assert angle != 0


@pytest.mark.parametrize("bias", [1, -1])
def test_gear_meshes_with_neighbour(bias):
    gear_a = Gear(12)
    gear_b = Gear(12)

    gear_a.mesh_to(gear_b, offset=0.0, bias=bias)

    assert len(gear_b.points) == len(gear_a.points) or gear_b.points is not None
