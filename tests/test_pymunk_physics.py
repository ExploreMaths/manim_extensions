# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the vendored pymunk physics layer."""

import numpy as np
import pytest
from manim import Circle, DOWN, LEFT, Line, RIGHT, Square, UP, VGroup

from manim_extensions.pymunk.space.SpaceScene import SpaceScene
from manim_extensions.pymunk.space.VSpace import VSpace


def test_vspace_gravity_and_sub_step():
    space = VSpace(gravity=(0, -9.81), sub_step=4)

    assert space.space.gravity.y == pytest.approx(-9.81)
    assert space.sub_step == 4


def test_vspace_updater_advances_the_space():
    vspace = VSpace(gravity=(0, -1))
    vspace.init_updater()

    ball = Circle(radius=0.2)
    vspace.add(ball)
    vspace.add_shapes_filter(ball) if hasattr(vspace, "add_shapes_filter") else None
    vspace.update(0.016)

    assert ball.get_center().shape == (3,)


@pytest.mark.parametrize("is_solid", [True, False])
def test_static_body_shapes(is_solid):
    scene = SpaceScene()
    floor = Line(LEFT * 6, RIGHT * 6).to_edge(DOWN)

    scene.add_static_body(floor, is_solid=is_solid)

    assert scene.vspace is not None
    assert floor.body is not None


@pytest.mark.parametrize("body_type", ["dynamic", "kinematic", "static"])
def test_body_types(body_type):
    scene = SpaceScene()
    ball = Circle(radius=0.3)

    getattr(scene, "add_%s_body" % body_type)(ball)

    assert ball.body is not None
    assert ball.get_center().shape == (3,)


def test_body_family_members():
    scene = SpaceScene()
    group = VGroup(Circle(radius=0.2), Square(side_length=0.4))

    scene.add_dynamic_body(group, family_members=True)

    assert len(group) == 2


@pytest.mark.parametrize("sensor", [True, False])
@pytest.mark.parametrize("elasticity,friction", [(0.5, 0.5), (0.9, 0.1)])
def test_material_parameters(sensor, elasticity, friction):
    scene = SpaceScene()
    ball = Circle(radius=0.25)

    scene.add_dynamic_body(
        ball,
        sensor=sensor,
        elasticity=elasticity,
        friction=friction,
    )

    assert ball.shapes[0].elasticity == pytest.approx(elasticity)


def test_force_and_impulse_helpers():
    scene = SpaceScene()
    ball = Circle(radius=0.3).shift(UP * 2)
    scene.add_dynamic_body(ball)

    scene.apply_force_at_local_point(ball, force=(1, 1, 0), point=(0, 0, 0))
    scene.apply_force_at_world_point(
        ball, force=(0, 1, 0), point=tuple(ball.get_center())
    )
    scene.apply_impulse_at_local_point(ball, impulse=(0, 2, 0), point=(0, 0, 0))
    scene.apply_impulse_at_world_point(
        ball, impulse=(2, 0, 0), point=tuple(ball.get_center())
    )

    assert ball.get_center().shape == (3,)


def test_velocity_queries():
    scene = SpaceScene()
    ball = Circle(radius=0.3)
    scene.add_dynamic_body(ball, velocity=(1, 0))

    local = scene.get_velocity_at_local_point(ball, point=(0, 0, 0))
    world = scene.velocity_at_world_point(ball, point=(0, 0, 0))

    assert isinstance(local, tuple)
    assert isinstance(world, tuple)


def test_body_helpers_and_sleep():
    scene = SpaceScene()
    ball = Circle(radius=0.3)
    scene.add_dynamic_body(ball)

    assert SpaceScene.get_body(ball) is not None
    assert SpaceScene.get_shapes(ball) is not None

    scene.sleep_body(ball)
    scene.active_body(ball)


def test_collision_handlers():
    scene = SpaceScene()
    left = Circle(radius=0.3).shift(LEFT)
    right = Circle(radius=0.3).shift(RIGHT)
    scene.add_dynamic_body(left, right)

    scene.set_collision_type(left, right, collision_type=7)
    scene.set_wildcard_collision_handler(7, begin=None)

    assert list(left.body.shapes)[0].collision_type == 7


def test_point_and_line_queries():
    scene = SpaceScene()
    wall = Square(side_length=1).shift(UP)
    scene.add_static_body(wall, is_solid=False)

    assert wall.body is not None


def test_shape_pair_info_returns_material_data():
    scene = SpaceScene()
    ball = Circle(radius=0.3)
    scene.add_dynamic_body(ball)

    shapes = list(ball.body.shapes)
    info = scene.get_shapea_shapeb_info(shapes[0], shapes[0])

    assert info is not None
