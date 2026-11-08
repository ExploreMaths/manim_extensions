# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for gear undercut handling and solver fallbacks."""

import pytest

from manim_extensions.gearbox.gear_mobjects import gear_mobject
from manim_extensions.gearbox.gear_mobjects.gear_mobject import Gear


@pytest.mark.parametrize(
    "teeth, kwargs",
    [
        (5, {}),
        (6, {}),
        (7, {"profile_shift": -0.2}),
        (8, {"profile_shift": 0.1}),
        (9, {"h_a": 1.5, "h_f": 1.6}),
    ],
)
def test_small_gears_build_undercut_profiles(teeth, kwargs):
    gear = Gear(teeth, **kwargs)

    assert len(gear.points) > 0


def test_generate_points_falls_back_when_solver_fails(monkeypatch):
    def _raise(*args, **kwargs):
        raise RuntimeError("solver unavailable")

    monkeypatch.setattr(gear_mobject, "fsolve", _raise)
    monkeypatch.setattr(gear_mobject, "least_squares", _raise)

    gear = Gear(6)

    assert len(gear.points) > 0
