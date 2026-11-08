# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the three mind-map layout algorithms."""

import pytest
from manim import Text

from manim_extensions.mindmap.algorithms.alg_catalog import CatalogLayout, CatalogNode
from manim_extensions.mindmap.algorithms.alg_time_line import TimeLineLayout, TimelineNode
from manim_extensions.mindmap.algorithms.alg_tidy_tree import TidyTreeLayout, WrappedTree
from manim_extensions.mindmap.algorithms.layout_config import LayoutDirection
from manim_extensions.mindmap.nodes import Node


def build_tree():
    root = Node(Text("root"))
    first = Node(Text("first"))
    second = Node(Text("second"))
    root.add_child(first)
    root.add_child(second)
    first.add_child(Node(Text("leaf")))
    return root


def test_timeline_layout_two_sides():
    root = build_tree()

    laid_out = TimeLineLayout(root).layout()

    assert isinstance(laid_out, Node)


def test_timeline_layout_single_side():
    root = build_tree()

    laid_out = TimeLineLayout(root, sides=(LayoutDirection.TopToBottom,)).layout()

    assert isinstance(laid_out, Node)


@pytest.mark.parametrize(
    "direction",
    [LayoutDirection.LeftToRight, LayoutDirection.TopToBottom],
)
def test_tidy_tree_layout(direction):
    root = build_tree()

    laid_out = TidyTreeLayout(root, direction=direction).layout()

    assert isinstance(laid_out, Node)


def test_catalog_layout():
    root = build_tree()

    laid_out = CatalogLayout(root).layout()

    assert isinstance(laid_out, Node)


def test_node_wrappers_round_trip():
    root = build_tree()

    assert TimelineNode.from_node(root) is not None
    assert CatalogNode.from_data(root) is not None
    assert WrappedTree.from_node(root, is_horizontal=True, level=0) is not None
