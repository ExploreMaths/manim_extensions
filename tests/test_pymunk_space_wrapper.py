# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the pymunk space wrapper."""

import numpy as np
import pytest
from manim import Square

from manim_extensions.pymunk.space.VSpace import VSpace
from manim_extensions.pymunk.space.SpaceScene import SpaceScene


def test_gravity_and_sub_step():
    space = VSpace(gravity=(0, -5), sub_step=4)

    assert space.space.gravity.y == -5
    assert space.sub_step == 4


def test_default_updater_is_set_up():
    space = VSpace()

    assert space.space is not None


@pytest.fixture()
def scene():
    physics_scene = SpaceScene()
    physics_scene.construct()
    return physics_scene


def test_local_to_world_round_trip(scene):
    body = Square()
    scene.add_dynamic_body(body)

    world = VSpace.local_to_world(body, (0.0, 0.0, 0.0))

    assert len(world) == 3
    assert world[2] == 0


def test_world_to_local_round_trip(scene):
    body = Square()
    scene.add_dynamic_body(body)

    local = VSpace.world_to_local(body, (1.0, 1.0, 0.0))

    assert len(local) == 3


def test_impulse_and_force_helpers(scene):
    body = Square()
    scene.add_dynamic_body(body)
    space = scene.vspace

    space.apply_impulse_at_local_point(body, (1.0, 0.0))
    space.apply_force_at_world_point(body, (0.0, 1.0), (0.0, 0.0))

    assert np.allclose(body.body.velocity.y, 0.0, atol=1.0)
