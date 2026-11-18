import numpy as np
import pytest
from manim import Circle, RIGHT

from manim_extensions.pymunk.constraints import VPivotJoint
from manim_extensions.pymunk.space.SpaceScene import SpaceScene


@pytest.fixture()
def physics():
    scene = SpaceScene()
    scene.construct()
    body_a = Circle()
    body_b = Circle()
    scene.add_dynamic_body(body_a, body_b)
    body_a.move_to([2, 0, 0])
    body_b.move_to([-2, 0, 0])
    return scene, body_a, body_b


def test_pivot_world_updater_moves_lines(physics):
    scene, body_a, body_b = physics
    joint = VPivotJoint(body_a, body_b, pivot_world=[0.0, 0.0, 0.0])
    joint.install(scene.vspace.space)

    joint.mob_updater(body_a, 0.01)

    assert joint.pivot_connect_line_a is not None


def test_pivot_local_updater_moves_anchors(physics):
    scene, body_a, body_b = physics
    joint = VPivotJoint(
        body_a,
        body_b,
        anchor_a_local=[0.0, 0.0, 0.0],
        anchor_b_local=[1.0, 1.0, 0.0],
    )
    joint.install(scene.vspace.space)

    joint.mob_updater(body_a, 0.01)

    assert joint.anchor_connect_line is not None


def test_pivot_updater_without_constraint_is_noop():
    joint = VPivotJoint(Circle(), Circle())
    joint.mob_updater(Circle(), 0.01)


def test_pivot_requires_one_anchor_configuration(physics):
    scene, body_a, body_b = physics
    joint = VPivotJoint(
        body_a,
        body_b,
        anchor_a_local=None,
        anchor_b_local=None,
    )

    with pytest.raises(TypeError):
        joint.install(scene.vspace.space)
