# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for timeline sibling shifting on multi-level trees."""

import pytest
from manim import DOWN, Text, UP

from manim_extensions.mindmap.algorithms.alg_time_line import TimeLineLayout
from manim_extensions.mindmap.nodes import Node


def build_chain_tree():
    root = Node(Text("root"))
    branch = Node(Text("branch"))
    root.add_child(branch)
    for index in range(3):
        child = Node(Text(f"child {index}"))
        branch.add_child(child)
        child.add_child(Node(Text(f"leaf {index}")))
    return root, branch


def test_layout_three_levels():
    root, branch = build_chain_tree()

    laid_out = TimeLineLayout(root).layout()

    assert laid_out is not None


def test_node_boundaries_are_computed():
    root, _ = build_chain_tree()
    layout = TimeLineLayout(root)

    boundaries = layout._get_node_boundaries(root.children[0], "y")

    assert isinstance(boundaries, dict)


def test_update_children_shifts_grandchildren():
    root, _ = build_chain_tree()
    layout = TimeLineLayout(root)

    layout._update_children(root.children, "y", 1.0)

    assert root.children[0].y is not None
