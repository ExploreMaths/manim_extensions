# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for tidy-tree connector computation in every direction."""

import pytest

from manim_extensions.mindmap.algorithms.alg_tidy_tree import TidyTreeLayout
from manim_extensions.mindmap.algorithms.layout_config import LayoutDirection


class StubNode:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.children = []
        self.parent = None
        self.level = 0
        self.x = 0.0
        self.y = 0.0


def _tree():
    root = StubNode(1.6, 0.8)
    for _ in range(3):
        child = StubNode(1.4, 0.7)
        child.parent = root
        for _ in range(2):
            grand = StubNode(1.2, 0.6)
            grand.parent = child
            child.children.append(grand)
        root.children.append(child)
    return root


@pytest.mark.parametrize(
    "direction",
    [
        LayoutDirection.TopToBottom,
        LayoutDirection.BottomToTop,
        LayoutDirection.LeftToRight,
        LayoutDirection.RightToLeft,
    ],
)
def test_connectors_are_computed_for_each_direction(direction):
    root = _tree()
    layout = TidyTreeLayout(root, direction=direction)
    layout.layout()

    layout.compute_connectors()

    assert len(layout.root.children[0].connector_points) == 4


def test_nested_children_receive_connectors():
    root = _tree()
    layout = TidyTreeLayout(root)
    layout.layout()

    layout.compute_connectors()

    assert layout.root.children[0].children[0].connector_points is not None
