# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the mind-map layout animation classes."""

import pytest
from manim import Scene, Text

from manim_extensions.mindmap.animations.animations import (
    AlterNode,
    InsertNode,
    LayoutAnimation,
    RemoveNode,
    ScaleNode,
)
from manim_extensions.mindmap.nodes.node import Node


@pytest.fixture
def tree():
    """A small two-level mind map."""
    root = Node(Text("Root"))
    left = Node(Text("Left"))
    right = Node(Text("Right"))
    root.add_child(left)
    root.add_child(right)
    return root, left, right


@pytest.fixture
def scene():
    """A bare scene; the animations are collected, not rendered."""
    return Scene()


def test_layout_animation_collects_animations(scene, tree):
    root, left, right = tree
    animation = LayoutAnimation(scene, root)

    collected = animation.collect_animations()

    assert len(collected) >= 1


def test_insert_node(scene, tree):
    root, left, right = tree
    root.remove_child(right)

    animation = InsertNode(scene, {root: [right]})
    collected = animation.collect_animations()

    assert len(collected) >= 1


def test_common_root_lookup(scene, tree):
    root, left, right = tree
    animation = LayoutAnimation(scene, root)

    assert animation.get_common_root([left, right]) is root


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_nested_tree_layout(scene, depth):
    root = Node(Text("Root"))
    cursor = root
    for level in range(depth):
        child = Node(Text("Level %d" % level))
        cursor.add_child(child)
        cursor = child

    animation = LayoutAnimation(scene, root)
    collected = animation.collect_animations()

    assert len(collected) >= 1
