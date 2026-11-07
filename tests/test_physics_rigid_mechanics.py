# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the rigid-mechanics physics space."""

import pytest
from manim import Square, VGroup

from manim_extensions.physics.rigid_mechanics.rigid_mechanics import SpaceScene


@pytest.fixture(scope="module")
def scene():
    physics_scene = SpaceScene()
    physics_scene.setup()
    return physics_scene


def test_setup_creates_space(scene):
    assert scene.space is not None


def test_make_rigid_body(scene):
    body = Square()

    scene.make_rigid_body(body)

    assert hasattr(body, "body")
    assert hasattr(body, "shape")


def test_make_static_body(scene):
    body = Square()

    scene.make_static_body(body)

    assert hasattr(body, "body")


def test_make_static_body_recurses_into_group(scene):
    group = VGroup(Square(), Square())

    scene.make_static_body(group)

    assert scene.space is not None


def test_stop_rigidity(scene):
    body = Square()
    scene.make_rigid_body(body)

    scene.stop_rigidity(body)

    assert hasattr(body, "body")
