# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the mind map node model."""

from manim import Text

from manim_extensions.mindmap.nodes.node import (
    Node,
    NodeSate,
    NodeStyle,
    bfs_walker,
    dfs_walker,
)


def make_tree():
    root = Node(Text("root"))
    first = Node(Text("first"))
    second = Node(Text("second"))
    grandchild = Node(Text("grandchild"))
    root.add_child(first)
    root.add_child(second)
    first.add_child(grandchild)
    return root, first, second, grandchild


def test_node_geometry_and_defaults():
    node = Node(Text("label"), buff=0.3)

    assert node.width > node.vmobject.width
    assert node.node_state is NodeSate.INSERT
    assert node.parent is None
    assert node.children == []


def test_add_child_links_parent_and_neighbour():
    root, first, second, _ = make_tree()

    assert first.parent is root
    assert second.parent is root
    assert second.neighbor is first
    assert root.children == [first, second]


def test_scale_updates_dimensions():
    node = Node(Text("label"))
    width = node.width

    node.scale(2)

    assert node.width == width * 2
    assert node.node_state is NodeSate.SCALE


def test_remove_child_marks_state():
    root, first, _, _ = make_tree()

    root.remove_child(first)

    assert first.node_state is NodeSate.REMOVE


def test_dfs_walker_pre_order():
    root, first, second, grandchild = make_tree()

    visited = list(dfs_walker(root))

    assert visited[0] is root
    assert grandchild in visited
    assert len(visited) == 4


def test_bfs_walker_level_order():
    root, first, second, grandchild = make_tree()

    visited = list(bfs_walker(root))

    assert visited[:3] == [root, first, second]
    assert visited[3] is grandchild


def test_walker_handles_empty_root():
    assert list(dfs_walker(None)) == []
    assert list(bfs_walker(None)) == []


def test_node_style_levels():
    style = NodeStyle()

    assert isinstance(style.get_node_style(0), dict)
    assert isinstance(style.get_line_style(1), dict)
    assert isinstance(style.get_text_style(2), dict)
