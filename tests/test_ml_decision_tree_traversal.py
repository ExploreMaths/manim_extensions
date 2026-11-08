# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for decision tree traversal helpers."""

import pytest

pytest.importorskip("sklearn")

from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier

from manim_extensions.machine_learning.decision_tree.helpers import (
    compute_node_depths,
    compute_node_to_parent_mapping,
)


@pytest.fixture(scope="module")
def tree():
    data = load_iris()
    return DecisionTreeClassifier(max_depth=3, random_state=0).fit(
        data.data, data.target
    ).tree_


def test_compute_node_depths_covers_all_nodes(tree):
    depths = compute_node_depths(tree)

    assert len(depths) == tree.node_count
    assert depths[0] == 0


def test_compute_node_to_parent_mapping(tree):
    mapping = compute_node_to_parent_mapping(tree)

    assert mapping[0] == -1
    assert len(mapping) >= 1
