# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for mind-map tree copying, syncing and direction helpers."""

import pytest

from manim_extensions.mindmap.algorithms.alg_standard import (
    StandardLayout,
    TreeNode,
    copy_node,
    split_integer,
    sync_copy_bfs,
)
from manim_extensions.mindmap.algorithms.layout_config import LayoutDirection


def build_tree(child_counts=(2, 0, 0)):
    root = TreeNode(1.0, 2.0)
    for count in child_counts:
        node = TreeNode(0.5, 1.0)
        for _ in range(count):
            node.add_child(TreeNode(0.2, 0.4))
        root.add_child(node)
    return root


def test_copy_node_handles_none_and_deep_copies():
    assert copy_node(None) is None

    source = build_tree()
    copied = copy_node(source)

    assert copied is not source
    assert len(copied.children) == len(source.children)
    assert all(a is not b for a, b in zip(copied.children, source.children))


def test_sync_copy_bfs_copies_layout_fields():
    source = build_tree()
    destination = build_tree()
    source.x, source.y, source.level = 3.0, 4.0, 1
    source.is_flip = True

    sync_copy_bfs(source, destination)

    assert destination.x == 3.0
    assert destination.y == 4.0
    assert destination.level == 1
    assert destination.is_flip is True


def test_sync_copy_bfs_rejects_mismatched_structures():
    source = build_tree()
    destination = build_tree()
    destination.children.pop()
    with pytest.raises(ValueError, match="Child node counts do not match"):
        sync_copy_bfs(source, destination)

    with pytest.raises(ValueError, match="Tree structures do not match"):
        sync_copy_bfs(None, TreeNode(0.0, 0.0))


def test_split_integer_odd_and_even():
    assert split_integer(5) == (3, 2)
    assert split_integer(4) == (2, 2)


def test_flip_direction_round_trips():
    layout = object.__new__(StandardLayout)

    assert (
        layout._flip_direction(LayoutDirection.LeftToRight)
        is LayoutDirection.RightToLeft
    )
    assert (
        layout._flip_direction(LayoutDirection.RightToLeft)
        is LayoutDirection.LeftToRight
    )
    assert (
        layout._flip_direction(LayoutDirection.TopToBottom)
        is LayoutDirection.BottomToTop
    )
    assert (
        layout._flip_direction(LayoutDirection.BottomToTop)
        is LayoutDirection.TopToBottom
    )
