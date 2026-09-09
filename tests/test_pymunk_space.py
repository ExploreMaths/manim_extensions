# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the pymunk (VSpace/SpaceScene) physics integration."""

import pymunk
import pytest
from manim import Dot

from manim_extensions.pymunk.space.VSpace import VSpace


@pytest.fixture
def vspace():
    return VSpace()


class TestVSpaceCollisionHandlers:
    """Regression: pymunk 7 removed add_collision_handler APIs (9a12ddc)."""

    def test_collision_detection_handler_registers(self, vspace):
        called = {}

        def begin(arbiter, space, data):
            called["begin"] = True
            return True

        result = vspace._collision_detection_handler(1, 2, begin=begin)
        if not hasattr(pymunk.Space, "on_collision"):
            assert result is not None

    def test_wildcard_collision_handler_registers(self, vspace):
        result = vspace._wildcard_collision_handler(1)
        if not hasattr(pymunk.Space, "on_collision"):
            assert result is not None

    def test_wildcard_handler_fires_on_collision(self, vspace):
        """Registered callbacks must actually run during stepping."""
        events = []

        def begin(arbiter, space, data):
            events.append("hit")
            return True

        vspace._wildcard_collision_handler(1, begin=begin)

        body_a = pymunk.Body(1, 100)
        body_a.position = (0, 0)
        shape_a = pymunk.Circle(body_a, 1)
        shape_a.collision_type = 1
        body_b = pymunk.Body(1, 100)
        body_b.position = (0.5, 0)
        shape_b = pymunk.Circle(body_b, 1)
        shape_b.collision_type = 2
        vspace.space.add(body_a, shape_a, body_b, shape_b)

        for _ in range(5):
            vspace.space.step(1 / 60)

        assert events, "collision begin callback never fired"


class TestVSpaceBodiesAndShapes:
    def test_add_and_remove_dynamic_body(self, vspace):
        dot = Dot()
        vspace.set_body_and_shapes(
            dot,
            pymunk.Body.DYNAMIC,
            True,
            0.5,
            0.5,
            1.0,
            False,
            (0, 0),
            (0, 0),
            (0, 0),
            0.0,
        )
        assert dot.body is not None
        assert len(dot.shapes) > 0
        vspace.remove_body_shapes_constraints(dot.body, *dot.shapes)
        assert dot.body not in vspace.space.bodies

    def test_gravity_default(self):
        space = VSpace()
        assert space.space.gravity.y != 0


class TestSpaceScene:
    def test_scene_has_vspace(self):
        from manim_extensions.pymunk import SpaceScene

        scene = SpaceScene()
        assert scene.vspace is not None
        assert isinstance(scene.vspace, VSpace)

    def test_add_dynamic_body_via_scene(self):
        from manim_extensions.pymunk import SpaceScene

        scene = SpaceScene()
        dot = Dot()
        scene.add_dynamic_body(dot, density=1)
        assert SpaceScene.get_body(dot) is not None
        assert SpaceScene.get_shapes(dot)
        scene.vspace.remove_body_shapes_constraints(
            SpaceScene.get_body(dot), *SpaceScene.get_shapes(dot)
        )
        assert SpaceScene.get_body(dot) not in scene.vspace.space.bodies
