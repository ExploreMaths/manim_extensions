# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for catalog layout on four-level trees and sibling helpers."""

import pytest
from manim import Text

from manim_extensions.mindmap.algorithms.alg_catalog import CatalogLayout
from manim_extensions.mindmap.nodes import Node


def build_four_level_tree():
    root = Node(Text("root"))
    for branch_index in range(2):
        branch = Node(Text(f"branch {branch_index}"))
        root.add_child(branch)
        for mid_index in range(2):
            mid = Node(Text(f"mid {branch_index}.{mid_index}"))
            branch.add_child(mid)
            mid.add_child(Node(Text(f"leaf {branch_index}.{mid_index}")))
    return root


def test_four_level_layout_runs():
    root = build_four_level_tree()

    laid_out = CatalogLayout(root).layout()

    assert laid_out is not None


def test_update_children_pro_accumulates_props():
    root = build_four_level_tree()
    layout = CatalogLayout(root)
    layout.layout()
    branch = layout.root.children[0]

    layout._update_children_pro(branch.children, {"top": 1.0})

    assert branch.children[0].top is not None


def test_update_brothers_top_shifts_younger_siblings():
    root = build_four_level_tree()
    layout = CatalogLayout(root)
    layout.layout()
    branch = layout.root.children[0]
    before = branch.children[1].top

    layout._update_brothers_top(branch.children[0], 1.0)

    assert branch.children[1].top != before


def test_margin_helpers_differ_by_layer():
    root = build_four_level_tree()
    layout = CatalogLayout(root, node_spacing=0.7, level_spacing=0.3)

    assert layout._get_margin_x(1) == pytest.approx(0.7)
    assert layout._get_margin_x(2) == pytest.approx(0.3)
    assert layout._get_margin_y(3) == pytest.approx(0.3)
