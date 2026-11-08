# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the timeline layout algorithm on deeper trees."""

import pytest

from manim_extensions.mindmap.algorithms.alg_time_line import TimeLineLayout
from manim_extensions.mindmap.algorithms.layout_config import LayoutDirection


class StubNode:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.children = []
        self.side_dir = None


def _deep_tree(branching, depth):
    root = StubNode(1.6, 0.8)
    for i in range(branching):
        child = StubNode(1.4, 0.7)
        root.children.append(child)
        if depth > 1:
            for _ in range(2):
                child.children.append(StubNode(1.2, 0.6))
    return root


@pytest.mark.parametrize("branching", [2, 4, 5])
def test_two_sided_layout_assigns_coordinates(branching):
    root = _deep_tree(branching, 2)

    laid_out = TimeLineLayout(root).layout()

    assert laid_out.x is not None
    for child in laid_out.children:
        assert child.y is not None


def test_single_sided_layout():
    sides = (LayoutDirection.TopToBottom,)
    root = _deep_tree(3, 2)

    laid_out = TimeLineLayout(root, sides=sides).layout()

    assert laid_out.x is not None
