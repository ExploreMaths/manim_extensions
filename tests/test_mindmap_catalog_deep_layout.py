# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for deeply nested catalog layouts."""

from manim import Text

from manim_extensions.mindmap.algorithms.alg_catalog import CatalogLayout
from manim_extensions.mindmap.nodes import Node


def build_tree():
    root = Node(Text("root"))
    for index in range(3):
        child = Node(Text(f"child {index}"))
        root.add_child(child)
        for leaf_index in range(3):
            child.add_child(Node(Text(f"leaf {leaf_index}")))
    return root


def test_catalog_layout_handles_three_levels():
    root = build_tree()

    laid_out = CatalogLayout(root).layout()

    assert isinstance(laid_out, Node)
    assert len(laid_out.children) == 3


def test_catalog_layout_child_height_accounts_for_grandchildren():
    root = build_tree()
    layout = CatalogLayout(root)

    for child in root.children:
        child.layer_index = 2
    height = layout._get_node_area_height(root.children[0])

    assert height >= root.children[0].height
