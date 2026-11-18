# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Exercise VSpace internals that do not need a full simulation."""

from types import SimpleNamespace

import numpy as np
from manim import Square

from manim_extensions.pymunk.space.VSpace import VSpace


def test_simulate_updater_copies_body_transform():
    space = VSpace()
    mob = Square()

    mob.body = SimpleNamespace(position=(1.5, -2.0), angle=0.4)
    mob.angle = 0.0

    getattr(space, "_VSpace__simulate_updater")(mob)

    assert np.allclose(mob.get_center()[:2], [1.5, -2.0])
    assert mob.angle == 0.4


def test_add_body2space_static_body_branch():
    space = VSpace()
    mob = Square()
    mob.body = space.space.static_body
    mob.shapes = []

    space._add_body2space(mob)

    assert mob.body is space.space.static_body


def test_position_and_velocity_callback_setters():
    space = VSpace()
    mob = Square()
    mob.body = SimpleNamespace()

    position = lambda body, dt: None
    velocity = lambda body, gravity, damping, dt: None

    space.set_position_func(mob, position)
    space.set_velocity_func(mob, velocity)

    assert mob.body.position_func is position
    assert mob.body.velocity_func is velocity


def test_solid_shape_skips_too_few_points():
    space = VSpace()
    mob = Square()
    mob.body = SimpleNamespace()
    mob.shapes = []
    mob.family_members_with_points = lambda: []

    getattr(space, "_VSpace__calculate_solid_shape")(mob)

    assert mob.shapes == []


def test_solid_shape_builds_convex_polygon():
    import pymunk
    from manim import Triangle

    space = VSpace()
    mob = Triangle()
    mob.body = pymunk.Body(body_type=pymunk.Body.STATIC)
    mob.shapes = []

    getattr(space, "_VSpace__calculate_solid_shape")(mob)

    assert mob.shapes


def test_hollow_shape_skips_too_few_points():
    space = VSpace()
    mob = Square()
    mob.body = SimpleNamespace()
    mob.shapes = []
    mob.family_members_with_points = lambda: []

    getattr(space, "_VSpace__calculate_hollow_shape")(mob)

    assert mob.shapes == []


def test_refined_points_skips_empty_and_short_curves():
    space = VSpace()
    mob = Square()
    empty = SimpleNamespace(points=np.empty((0, 3)))
    short = SimpleNamespace(points=np.array([[0.0, 0.0, 0.0]]))
    mob.family_members_with_points = lambda: [empty, short]

    points = getattr(space, "_VSpace__get_refined_points")(mob, 2)

    assert points == []


def test_concave_shape_returns_empty_for_too_few_points():
    space = VSpace()
    mob = Square()
    mob.body = SimpleNamespace()
    mob.family_members_with_points = lambda: []

    hulls = getattr(space, "_VSpace__concave2convex_refined")(mob, 2, 0.01)

    assert hulls == []


def test_concave_shape_falls_back_to_hull_on_error(monkeypatch):
    import pymunk.autogeometry

    import pymunk

    space = VSpace()
    mob = Square()
    mob.body = pymunk.Body(body_type=pymunk.Body.STATIC)

    def raise_error(points, tolerance):
        raise RuntimeError("bad winding")

    monkeypatch.setattr(pymunk.autogeometry, "convex_decomposition", raise_error)

    hulls = getattr(space, "_VSpace__concave2convex_refined")(mob, 2, 0.01)

    assert hulls


def test_solid_shape_convex_append(monkeypatch):
    import pymunk.autogeometry
    from manim import Triangle

    space = VSpace()
    mob = Triangle()
    mob.body = pymunk.Body(body_type=pymunk.Body.STATIC)
    mob.shapes = []

    original = pymunk.autogeometry.to_convex_hull
    monkeypatch.setattr(
        pymunk.autogeometry,
        "to_convex_hull",
        lambda points, tolerance: list(points),
    )

    getattr(space, "_VSpace__calculate_solid_shape")(mob)

    assert mob.shapes
    assert original is not None


def test_image_shape_falls_back_to_box():
    import pymunk

    space = VSpace()
    mob = SimpleNamespace(
        pixel_array=np.zeros((8, 8, 4), dtype=np.uint8),
        width=1.0,
        height=1.0,
        body=pymunk.Body(body_type=pymunk.Body.STATIC),
        shapes=[],
    )

    getattr(space, "_VSpace__calculate_img_shape")(mob)

    assert mob.shapes
