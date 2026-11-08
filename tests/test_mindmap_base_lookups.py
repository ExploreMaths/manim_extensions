# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the mindmap tree-building and lookup helpers."""

import pytest
from manim import MathTex

from manim_extensions.mindmap.mindmap.mindmap import MindMap

DATA = {
    "node": MathTex("Limits"),
    "child": [
        {"node": MathTex("Derivatives")},
        {
            "node": MathTex("Integrals"),
            "child": [
                {"node": MathTex("int x dx")},
                {"node": MathTex("int x2 dx")},
            ],
        },
    ],
}


@pytest.fixture()
def mindmap():
    return MindMap(DATA)


def test_map_is_built_from_nested_data(mindmap):
    assert len(mindmap.submobjects) >= 1


def test_node_lookup(mindmap):
    assert mindmap.get_node((0, 0)) is not None
    assert mindmap.get_text((0, 0)) is None
    assert mindmap._get_origin_node((0, 1)) is not None


def test_connector_lookup(mindmap):
    assert mindmap.get_connector((0, 1)) is not None


def test_group_and_subtree_queries(mindmap):
    assert mindmap.get_children((0, 0)) is not None
    assert mindmap.get_submindmap((0, 0)) is not None
    assert mindmap.get_descendants((0, 0)) is not None
    assert mindmap.get_all_mindmap() is not None


def test_walkers(mindmap):
    assert len(list(mindmap.bfs_walker())) >= 1
    assert len(list(mindmap.dfs_walker())) >= 1
