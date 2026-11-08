# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for meshing a gear to another gear or to a rack."""

import numpy as np

from manim_extensions.gearbox.gear_mobjects.gear_mobject import Gear, Rack


def test_mesh_gear_to_gear():
    driver = Gear(10)
    driven = Gear(12).shift([3, 0, 0])

    driver.mesh_to(driven)

    assert np.linalg.norm(driver.get_center() - driven.get_center()) > 0


def test_mesh_with_offset_and_bias():
    driver = Gear(10)
    driven = Gear(12).shift([3, 0, 0])

    driver.mesh_to(driven, offset=0.2, bias=0)
    driver.mesh_to(driven, offset=0.1, bias=1)

    assert driver.get_center() is not None


def test_mesh_gear_to_rack():
    driver = Gear(10)
    rack = Rack(10).shift([0, 4, 0])

    driver.mesh_to(rack)

    assert driver.get_center() is not None


def test_mesh_inner_teeth_gear():
    inner = Gear(24, inner_teeth=True)
    outer = Gear(10)

    outer.mesh_to(inner)

    assert len(outer.get_points()) > 0
