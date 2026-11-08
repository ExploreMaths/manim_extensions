# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests that cover the optional gear construction branches."""

import pytest

from manim_extensions.gearbox.gear_mobjects.gear_mobject import Gear, Rack


@pytest.mark.parametrize(
    "teeth, kwargs",
    [
        (10, {}),
        (10, {"inner_teeth": True}),
        (10, {"profile_shift": 0.5}),
        (10, {"cutout_teeth_num": 3}),
        (10, {"nppc": 12}),
        (6, {"alpha": 25}),
        (10, {"h_a": 2, "h_f": 2.4}),
        (10, {"module": 0.4}),
    ],
)
def test_gear_optional_geometry(teeth, kwargs):
    gear = Gear(teeth, **kwargs)

    assert len(gear.points) > 0


def test_rack_builds_points():
    rack = Rack(10)

    assert len(rack.points) > 0
