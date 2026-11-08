# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for connectors of third-level nodes."""

import numpy as np
import pytest
from manim import Text

from manim_extensions.mindmap.algorithms.layout_config import LayoutDirection, LayoutType
from manim_extensions.mindmap.nodes import Node

LEFT_DIR = np.array([-1.0, 0.0, 0.0])


@pytest.fixture()
def deep_tree():
    root = Node(Text("root"))
    child = Node(Text("child"))
    grand = Node(Text("grand"))
    child.add_child(grand)
    root.add_child(child)
    return root, child, grand


@pytest.mark.parametrize("side", [LayoutDirection.BottomToTop, LayoutDirection.TopToBottom])
@pytest.mark.parametrize("layout_type", [LayoutType.TimeLine, LayoutType.Catalog])
def test_deep_node_connector(deep_tree, side, layout_type):
    _, _, grand = deep_tree
    grand.side = side

    line = grand.get_connector(layout_type, LEFT_DIR)

    assert len(line.points) >= 2


def test_deep_node_without_direction_falls_back(deep_tree):
    _, _, grand = deep_tree
    grand.side = LayoutDirection.LeftToRight

    line = grand.get_connector(LayoutType.TimeLine, LEFT_DIR)

    assert len(line.points) >= 2
