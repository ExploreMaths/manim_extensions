# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Cover the SpaceScene accessors and collision-handler wrapper."""

import pytest
from manim import Square

from manim_extensions.pymunk.space.SpaceScene import SpaceScene


@pytest.fixture()
def scene():
    space_scene = SpaceScene()
    space_scene.setup()
    return space_scene


def test_get_body_rejects_unregistered_mobject(scene):
    with pytest.raises(RuntimeError):
        scene.get_body(Square())


def test_get_shapes_rejects_unregistered_mobject(scene):
    with pytest.raises(RuntimeError):
        scene.get_shapes(Square())


def test_get_body_and_shapes_return_registered_values(scene):
    square = Square()
    scene.add_static_body(square)

    assert scene.get_body(square) is square.body
    assert scene.get_shapes(square) == square.shapes


def test_collision_detection_handler_wrapper(scene):
    result = scene.set_collision_detection_handler(
        7,
        8,
        begin=lambda arbiter, space, data: True,
    )

    assert result is None


def test_add_constraints_delegates_to_install(scene):
    calls = []

    class Constraint:
        def install(self, space):
            calls.append(space)

    mob = Square()
    mob.install = Constraint().install

    scene.add_constraints(mob)

    assert calls == [scene.vspace.space]
