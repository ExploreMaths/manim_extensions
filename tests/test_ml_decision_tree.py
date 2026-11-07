# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the decision tree visualisation helpers."""

import numpy as np
import pytest

pytest.importorskip("sklearn")

from sklearn.datasets import load_iris

from manim_extensions.machine_learning.decision_tree.decision_tree_surface import (
    AABB,
    IrisDatasetPlot,
)


def test_aabb_starts_unbounded():
    box = AABB(3)

    assert box.limits.shape == (3, 2)
    assert np.isneginf(box.limits[0][0])
    assert np.isposinf(box.limits[0][1])


@pytest.mark.parametrize("feature", [0, 1])
def test_split_sets_left_and_right_limits(feature):
    box = AABB(2)

    left, right = box.split(feature, 0.5)

    assert left.limits[feature][1] == 0.5
    assert right.limits[feature][0] == 0.5
    assert left.limits[1 - feature].tolist() == box.limits[1 - feature].tolist()


def test_iris_plot_builds_groups():
    iris = load_iris()

    plot = IrisDatasetPlot(iris)

    assert plot.point_group is not None
    assert plot.axes_group is not None
    assert plot.legend_group is not None
    assert plot.all_group is not None


def test_iris_plot_animation():
    iris = load_iris()

    animation = IrisDatasetPlot(iris).create_animation()

    assert animation is not None
