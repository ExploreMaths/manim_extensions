# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the mind-map layout animation node-state handling."""

import pytest
from manim import Scene, Text

from manim_extensions.mindmap.animations import LayoutAnimation
from manim_extensions.mindmap.nodes import Node, NodeState


def build_tree():
    root = Node(Text("root"))
    child = Node(Text("child"))
    root.add_child(child)
    scene = Scene()
    scene.add(root.vmobject, child.vmobject)
    return scene, root, child


def test_layout_animation_collects_animations():
    scene, root, _ = build_tree()

    animation = LayoutAnimation(scene, root)

    assert len(animation.animations) >= 1


def test_removed_node_present_in_scene_is_collected():
    scene, root, child = build_tree()
    child.node_state = NodeState.REMOVE

    animation = LayoutAnimation(scene, root)

    assert len(animation.animations) >= 1


@pytest.mark.parametrize("state", [NodeState.REMOVE, NodeState.SCALE])
def test_missing_node_states_raise(state):
    scene = Scene()
    node = Node(Text("floating"))
    node.node_state = state

    with pytest.raises(Exception):
        LayoutAnimation(scene, node)
