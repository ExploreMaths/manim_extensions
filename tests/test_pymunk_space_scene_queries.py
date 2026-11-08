# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the SpaceScene position, velocity and query wrappers."""

import numpy as np
import pytest
from manim import Circle

from manim_extensions.pymunk.space.SpaceScene import SpaceScene


@pytest.fixture(scope="module")
def physics():
    scene = SpaceScene()
    scene.construct()
    body = Circle()
    scene.add_dynamic_body(body)
    return scene, body


def test_local_to_world_and_back(physics):
    scene, body = physics

    scene.local_to_world(body, (0, 0, 0))
    scene.world_to_local(body, (0, 0, 0))

    assert body.body is not None


def test_set_position_and_velocity_func(physics):
    scene, body = physics

    scene.set_position_func(body, lambda p, dt: None)
    scene.set_velocity_func(body, lambda p, g, d, dt: None)

    assert body.body is not None


def test_velocity_at_local_point(physics):
    scene, body = physics

    velocity = scene.get_velocity_at_local_point(body, (0, 0, 0))

    assert len(velocity) == 3


def test_point_query_returns_list(physics):
    scene, body = physics

    info = scene.get_point_query_info(body, (0, 0, 0))

    assert isinstance(info, list)


def test_line_query_returns_list(physics):
    scene, body = physics

    hits = scene.get_line_query(body, (0, -10, 0), (0, 10, 0), 1.0)

    assert isinstance(hits, list)
