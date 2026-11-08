# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for node connector variants and descendant traversal."""

import pytest
from manim import DOWN, LEFT, RIGHT, UP, Text

from manim_extensions.mindmap.algorithms.layout_config import LayoutType
from manim_extensions.mindmap.nodes import Node


@pytest.fixture()
def tree():
    root = Node(Text("root"))
    child = Node(Text("child"))
    grand = Node(Text("grand"))
    child.add_child(grand)
    root.add_child(child)
    return root, child, grand


def test_descendants_are_collected(tree):
    root, child, grand = tree

    assert len(root.get_descendants()) == 2
    assert grand in root.get_descendants()


def test_descendant_mobjects_are_collected(tree):
    root, _, _ = tree

    assert root.get_descendants_mobjects() is not None


@pytest.mark.parametrize(
    "layout_type",
    [LayoutType.MindMap, LayoutType.TimeLine, LayoutType.Standard, LayoutType.Catalog],
)
def test_connector_for_each_layout(tree, layout_type):
    _, child, _ = tree

    child.change_connector(True, True, layout_type)

    assert child is not None


@pytest.mark.parametrize("direction", [RIGHT, LEFT, UP, DOWN])
def test_connector_for_each_direction(tree, direction):
    _, child, _ = tree

    child.change_connector(True, True, LayoutType.MindMap, direction)

    assert child.get_connector(LayoutType.MindMap, direction) is not None
