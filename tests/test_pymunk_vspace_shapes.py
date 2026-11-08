# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for body/shape registration and spatial queries on a VSpace."""

import numpy as np
import pymunk
import pytest
from PIL import Image
from manim import Circle, ImageMobject

from manim_extensions.pymunk.space.VSpace import VSpace

BODY_DEFAULTS = dict(
    elasticity=0.8,
    friction=0.8,
    density=1.0,
    sensor=False,
    surface_velocity=(0.0, 0.0),
    center_of_gravity=(0.0, 0.0),
    velocity=(0.0, 0.0),
    angular_velocity=0.0,
)


@pytest.fixture()
def image_path(tmp_path):
    path = str(tmp_path / "ball.png")
    array = np.zeros((32, 32, 4), dtype=np.uint8)
    array[8:24, 8:24] = 255
    Image.fromarray(array).save(path)
    return path


@pytest.fixture()
def space():
    return VSpace()


def test_solid_mobject_gets_a_body(space):
    mob = Circle()

    space.set_body_and_shapes(mob, pymunk.Body.DYNAMIC, is_solid=True, **BODY_DEFAULTS)

    assert getattr(mob, "body", None) is not None
    assert len(mob.shapes) == 1


def test_hollow_mobject_gets_a_body(space):
    mob = Circle()

    space.set_body_and_shapes(mob, pymunk.Body.DYNAMIC, is_solid=False, **BODY_DEFAULTS)

    assert len(mob.shapes) >= 1


def test_image_mobject_shape(space, image_path):
    mob = ImageMobject(image_path)

    space.set_body_and_shapes(mob, pymunk.Body.DYNAMIC, is_solid=True, **BODY_DEFAULTS)

    assert len(mob.shapes) >= 1


def test_point_and_line_queries(space):
    mob = Circle()
    space.set_body_and_shapes(mob, pymunk.Body.DYNAMIC, is_solid=True, **BODY_DEFAULTS)

    point_info = space.get_point_query_info(mob, (0.0, 0.0, 0.0))
    line_info = space.get_line_query(mob, (-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), 2.0)

    assert isinstance(point_info, list)
    assert isinstance(line_info, list)


def test_shape_filter_can_be_applied(space):
    mob = Circle()
    space.set_body_and_shapes(mob, pymunk.Body.DYNAMIC, is_solid=True, **BODY_DEFAULTS)

    assert space._add_shape_filter(mob) is None
