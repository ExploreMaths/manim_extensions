# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for gear-to-rack meshing and default rotation centre."""

import numpy as np
import pytest
from manim import tempconfig

from manim_extensions.gearbox.gear_mobjects.gear_mobject import Gear, Rack


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_gear_meshes_with_rack():
    gear = Gear(18, module=0.2)
    rack = Rack(20, module=0.2)

    gear.mesh_to(rack)

    assert gear.get_center() is not None


def test_gear_rotate_without_about_point():
    gear = Gear(18, module=0.2)

    result = gear.rotate(np.pi / 6)

    assert result is gear


def test_gear_rotate_with_about_point():
    gear = Gear(18, module=0.2).shift([2, 0, 0])

    result = gear.rotate(np.pi / 6, about_point=[0, 0, 0])

    assert result is gear
