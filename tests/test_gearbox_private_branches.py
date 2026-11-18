# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

import numpy as np
import pytest

import manim_extensions.gearbox.gear_mobjects.gear_mobject as gear_module
from manim_extensions.gearbox.gear_mobjects.gear_mobject import (
    Gear,
    Rack,
    involute_deriv_func,
)


def test_involute_deriv_scalar_returns_point():
    result = involute_deriv_func(0.4, 1.0)
    assert result.shape == (3,)


def test_mesh_inner_drive_uses_shifted_pitch_radius():
    driver = Gear(30, inner_teeth=True, profile_shift=1)
    driven = Gear(20, profile_shift=1)
    driver.mesh_to(driven, offset=0.2)


def test_mesh_inner_driven_uses_shifted_pitch_radius():
    driver = Gear(20, profile_shift=1)
    driven = Gear(30, inner_teeth=True, profile_shift=1)
    driver.mesh_to(driven, offset=0.2)


def test_mesh_survives_fsolve_failure_for_inner_drive(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("no solution")

    monkeypatch.setattr(gear_module, "fsolve", boom)
    driver = Gear(30, inner_teeth=True, profile_shift=1)
    driven = Gear(20, profile_shift=1)
    driver.mesh_to(driven, offset=0.2)


def test_mesh_survives_fsolve_failure_for_normal_drive(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("no solution")

    monkeypatch.setattr(gear_module, "fsolve", boom)
    driver = Gear(20, profile_shift=1)
    driven = Gear(20, profile_shift=1)
    driver.mesh_to(driven, offset=0.2)


def test_rack_rotate_with_default_and_explicit_point():
    rack = Rack(12)
    rack.rotate(0.2)
    rack.rotate(0.2, about_point=np.array([1.0, 0.0, 0.0]))


def test_mesh_survives_fsolve_failure_for_inner_driven(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("no solution")

    monkeypatch.setattr(gear_module, "fsolve", boom)
    driver = Gear(20, profile_shift=1)
    driven = Gear(30, inner_teeth=True, profile_shift=1)
    driver.mesh_to(driven, offset=0.2)
