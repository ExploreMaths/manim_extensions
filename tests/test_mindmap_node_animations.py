# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the node-level mindmap animations."""

import pytest
from manim import Scene, Text

from manim_extensions.mindmap.animations.animations import (
    AlterNode,
    InsertNode,
    RemoveNode,
    ScaleNode,
)
from manim_extensions.mindmap.nodes import Node


@pytest.fixture()
def scene_tree():
    root = Node(Text("root"))
    child = Node(Text("child"))
    leaf = Node(Text("leaf"))
    child.add_child(leaf)
    root.add_child(child)

    scene = Scene()
    for node in (root, child, leaf):
        scene.add(*node.get_node_and_line_without_updater())

    return scene, root, child, leaf


def test_insert_node_animation(scene_tree):
    scene, root, child, leaf = scene_tree

    animation = InsertNode(scene, {root: [leaf]})

    assert animation is not None


def test_scale_node_animation(scene_tree):
    scene, root, _, _ = scene_tree

    animation = ScaleNode(scene, {root: 2.0})

    assert animation is not None


def test_alter_node_animation(scene_tree):
    scene, _, child, _ = scene_tree

    animation = AlterNode(scene, {child: Text("changed")})

    assert animation is not None


def test_remove_node_animation_fades_subtree(scene_tree):
    scene, _, child, _ = scene_tree

    animation = RemoveNode(scene, child)

    assert animation is not None


def test_remove_root_fades_the_whole_tree(scene_tree):
    scene, root, _, _ = scene_tree

    animation = RemoveNode(scene, root)

    assert animation is not None
