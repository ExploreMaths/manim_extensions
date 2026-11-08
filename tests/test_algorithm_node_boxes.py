# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for node box validation, slot lookup and overwrite animations."""

import pytest
from manim import DOWN, LEFT, RIGHT, UP, Circle, Square, tempconfig

from manim_extensions.algorithm.node import Node


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_set_box_accepts_square_and_circle():
    node = Node()
    node.set_box(Square, 1.0, "white")
    node.set_box(Circle, 1.0, "white")

    assert node.box is not None


def test_set_box_rejects_unknown_shape():
    node = Node()

    with pytest.raises(ValueError):
        node.set_box(object, 1.0, "white")


def test_get_slot_for_all_directions():
    node = Node()
    node.set_box(Square, 1.0, "white")

    for direction in (RIGHT, LEFT, UP, DOWN):
        assert node.get_slot(direction, 0) is not None


def test_get_slot_circle_adjusts_proportion():
    node = Node()
    node.set_box(Circle, 1.0, "white")

    assert node.get_slot(RIGHT, 0) is not None


def test_get_slot_rejects_diagonal_direction():
    node = Node()

    with pytest.raises(ValueError):
        node.get_slot(RIGHT + UP, 0)


def test_move_and_overwrite_with_select_color():
    node = Node()
    node.set_box(Square, 1.0, "white")
    target = Node()
    target.set_box(Square, 1.0, "white")

    animation = Node.MoveAndOverWrite(node, target, select_color="red")

    assert len(animation.animations) >= 1


def test_copy_and_overwrite_builds_succession():
    node = Node()
    node.set_box(Square, 1.0, "white")
    target = Node()
    target.set_box(Square, 1.0, "white")

    animation = Node.CopyAndOverWrite(node, target)

    assert len(animation.animations) >= 1


def test_swap_and_overwrite_with_select_color():
    node1 = Node()
    node1.set_box(Square, 1.0, "white")
    node2 = Node()
    node2.set_box(Square, 1.0, "white")

    animation = Node.SwapAndOverWrite(node1, node2, select_color="blue")

    assert len(animation.animations) >= 1
