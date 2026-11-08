# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the pymunk-backed space scene body helpers."""

import pytest
from manim import Circle, Square

from manim_extensions.pymunk.space.SpaceScene import SpaceScene


@pytest.fixture()
def scene():
    space_scene = SpaceScene()
    space_scene.setup()
    return space_scene


def test_static_body_is_registered(scene):
    square = Square()

    scene.add_static_body(square)

    assert getattr(square, "body", None) is not None


def test_dynamic_body_is_registered(scene):
    circle = Circle()

    scene.add_dynamic_body(circle)

    assert getattr(circle, "body", None) is not None


def test_kinematic_body_is_registered(scene):
    circle = Circle()

    scene.add_kinematic_body(circle)

    assert getattr(circle, "body", None) is not None


def test_active_and_sleeping_bodies(scene):
    circle = Circle()
    scene.add_dynamic_body(circle)

    assert scene.active_body(circle) is None
    assert scene.sleep_body(circle) is None


def test_shape_filter_can_be_applied(scene):
    circle = Circle()
    scene.add_dynamic_body(circle)

    assert scene.add_shapes_filter(circle) is None
