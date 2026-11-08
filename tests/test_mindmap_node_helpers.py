# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for node style lookup and connector switching."""

import pytest
from manim import Text

from manim_extensions.mindmap.algorithms.layout_config import LayoutType
from manim_extensions.mindmap.nodes import Node, NodeStyle


@pytest.fixture()
def tree():
    root = Node(Text("root"))
    first = Node(Text("first"))
    second = Node(Text("second"))
    first.add_child(Node(Text("leaf")))
    root.add_child(first)
    root.add_child(second)
    return root, second


def test_style_lookups_for_levels():
    style = NodeStyle()

    assert isinstance(style.get_node_style(0), dict)
    assert isinstance(style.get_line_style(0), dict)
    assert isinstance(style.get_text_style(0), dict)


def test_children_helpers(tree):
    root, _ = tree

    assert len(root.get_children()) == 2
    assert root.get_children_mobjects() is not None


def test_remove_child_and_alter_content(tree):
    root, second = tree

    root.remove_child(second)
    root.alter_content(Text("renamed"))

    assert root.get_children_mobjects() is not None


def test_node_and_line_without_updater(tree):
    root, _ = tree

    assert root.get_node_and_line_without_updater() is not None


@pytest.mark.parametrize(
    "change_dir, change_layout, layout_type",
    [
        (False, False, LayoutType.Standard),
        (True, False, LayoutType.TimeLine),
        (False, True, LayoutType.Catalog),
    ],
)
def test_change_connector_for_each_layout(tree, change_dir, change_layout, layout_type):
    root, _ = tree

    root.change_connector(change_dir, change_layout, layout_type)

    assert root is not None
