# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Smoke tests for the vendored ``manim-3d`` package."""

import pytest

from manim_extensions.three_d import (
    GaussianSurface,
    SaddleSurface,
    SaddleSurfaceScene,
    plan_timeline,
)


def test_gaussian_surface_resolves_to_callable():
    surface = GaussianSurface()
    func, tex = surface.resolve()
    assert callable(func)
    assert func(0, 0) == pytest.approx(1.0)
    assert tex == r"z = e^{-x^{2}-y^{2}}"


def test_saddle_surface_domain_and_geometry():
    surface = SaddleSurface()
    assert surface.domain == (-2.2, 2.2)
    func = SaddleSurfaceScene()._geometry(surface)[0]
    assert func(1, 1) == pytest.approx(0.0, abs=1e-9)


def test_plan_timeline_returns_beats_and_order():
    timeline = plan_timeline(
        20.0,
        {
            "title",
            "axes",
            "flat",
            "rise",
            "rings",
            "orbit",
            "flip",
            "annotate",
            "outro",
        },
    )
    beats, order = timeline
    assert beats
    assert isinstance(beats, dict)
    assert isinstance(order, list)
