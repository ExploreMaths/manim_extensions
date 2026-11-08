# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for mind-map node-state bookkeeping during layout animation."""

import pytest
from manim import Scene, Text

from manim_extensions.mindmap.animations import LayoutAnimation
from manim_extensions.mindmap.nodes import Node, NodeSate


def build_tree():
    root = Node(Text("root"))
    children = [Node(Text(f"child-{index}")) for index in range(3)]
    for child in children:
        root.add_child(child)

    scene = Scene()
    scene.add(root.vmobject, *[child.vmobject for child in children])

    return scene, root, children


def test_insert_state_is_promoted_to_display():
    scene, root, children = build_tree()
    children[0].node_state = NodeSate.INSERT

    animation = LayoutAnimation(scene, root)

    assert children[0].node_state == NodeSate.DISPLAY
    assert len(animation.animations) >= 1


@pytest.mark.parametrize("victim", [0, 1])
def test_remove_state_unlinks_node_from_parent(victim):
    scene, root, children = build_tree()
    removed = children[victim]
    removed.node_state = NodeSate.REMOVE

    animation = LayoutAnimation(scene, root)

    assert removed not in root.children
    assert len(animation.animations) >= 1


def test_display_state_is_kept():
    scene, root, children = build_tree()
    children[0].node_state = NodeSate.DISPLAY

    animation = LayoutAnimation(scene, root)

    assert children[0].node_state == NodeSate.DISPLAY
    assert len(animation.animations) >= 0
