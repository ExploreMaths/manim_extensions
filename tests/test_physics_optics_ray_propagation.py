# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for ray propagation through lenses."""

import pytest
from manim import LEFT, RIGHT, UP, tempconfig

from manim_extensions.physics.optics.lenses import Lens
from manim_extensions.physics.optics.rays import Ray


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.mark.parametrize("focal", [3, -3])
def test_ray_propagates_through_lens(focal):
    lens = Lens(focal, 2)

    ray = Ray(LEFT * 6 + UP * 0.5, RIGHT, 8, [lens])

    assert ray.propagated is True


def test_ray_propagates_through_two_lenses():
    first = Lens(3, 2)
    second = Lens(-4, 2)
    second.shift([2, 0, 0])

    ray = Ray(LEFT * 8, RIGHT, 10, [first, second])

    assert ray.propagated is True


def test_ray_missing_lens_keeps_geometry():
    lens = Lens(3, 0.5)
    lens.shift([0, 6, 0])

    ray = Ray(LEFT * 6, RIGHT, 4, [lens])

    assert ray.propagated is False


def test_propagate_can_be_invoked_after_construction():
    lens = Lens(3, 2)

    ray = Ray(LEFT * 6 + UP * 0.5, RIGHT, 8)
    ray.propagate(lens)

    assert ray.propagated is True


def test_lens_sorting_and_intersection_helpers():
    near = Lens(3, 2)
    far = Lens(3, 2)
    far.shift([10, 0, 0])

    ray = Ray(LEFT * 6, RIGHT, 8)

    assert ray._sort_lens([far, near]) is not None
