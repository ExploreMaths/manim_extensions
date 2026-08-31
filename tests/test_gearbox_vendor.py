# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


import numpy as np

from manim_extensions.gearbox import Gear
from manim_extensions.gearbox import Rack


def test_gear_constructor_and_fields():
    gear = Gear(12, module=0.25, alpha=20)

    assert gear.z == 12
    assert gear.m == 0.25
    assert gear.alpha == 20
    assert gear.h > 0
    assert gear.rp > 0
    assert gear.rb > 0
    assert gear.ra > 0
    assert gear.rf > 0
    assert gear.pitch > 0
    assert gear.pitch_angle > 0
    assert gear.nppc == 5
    assert hasattr(gear, "submobjects")
    assert gear.get_center().shape == (3,)
    assert np.isfinite(gear.get_angle())


def test_gear_meshing():
    gear1 = Gear(12, module=0.25, alpha=20)
    gear2 = Gear(18, module=0.25, alpha=20)

    gear1.mesh_to(gear2)
    assert gear1.get_center().shape == (3,)
    assert gear2.get_center().shape == (3,)


def test_rack_constructor_and_fields():
    rack = Rack(8, module=0.3, alpha=22)

    assert rack.z == 8
    assert rack.m == 0.3
    assert rack.alpha == 22
    assert rack.h > 0
    assert rack.pitch > 0
    assert hasattr(rack, "submobjects")
    assert rack.get_center().shape == (3,)
    assert np.isfinite(rack.get_angle())