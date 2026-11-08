# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the chemistry helper classes and mobject utilities."""

import numpy as np
import pytest
from manim import LEFT, RIGHT, Circle, Dot, Square, VGroup, tempconfig

from manim_extensions.chemistry.future_classes.future_classes import (
    add_over_rectangular_surface,
    concat_mobjects,
    duplicate_and_rearrange,
    get_element_by_data,
    make_subpaths,
    randomly_distributed_in_2D,
)


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_duplicate_and_rearrange_group():
    group = duplicate_and_rearrange(VGroup(Dot(), Square()))

    assert len(group) == 4


def test_duplicate_and_rearrange_single_mobject():
    group = duplicate_and_rearrange(Dot())

    assert len(group) >= 1


def test_add_over_rectangular_surface_returns_group():
    group = add_over_rectangular_surface(Dot(), amount=3, height=2, width=2)

    assert len(group) == 3


def test_get_element_by_data_builds_element():
    element = get_element_by_data(
        {"symbol": "Si", "color": "blue", "electrons": 2, "holes": 1}
    )

    assert element is not None


def test_randomly_distributed_in_2d_shifts_mobs():
    mobs = VGroup(Dot(), Dot())
    before = mobs.copy()

    randomly_distributed_in_2D(mobs, left=1, right=1, down=1, up=1)

    assert not np.allclose(mobs.get_center(), before.get_center())


def test_make_subpaths_adds_points():
    group = VGroup(Circle(), Circle())

    make_subpaths(group)

    assert len(group.points) > 0


def test_concat_mobjects_alternates_sides():
    group = concat_mobjects(Square(), concats=3, buff=0.1)

    assert len(group) == 4


def test_concat_mobjects_zero_copies():
    group = concat_mobjects(Square(), concats=0)

    assert len(group) == 1
