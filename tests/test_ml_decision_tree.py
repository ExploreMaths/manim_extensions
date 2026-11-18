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


def test_node_bounding_boxes_infers_feature_count():
    from sklearn.tree import DecisionTreeClassifier

    from manim_extensions.machine_learning.decision_tree.decision_tree_surface import (
        tree_bounds,
    )

    data = load_iris()
    tree = (
        DecisionTreeClassifier(max_depth=2, random_state=0)
        .fit(data.data, data.target)
        .tree_
    )

    boxes = tree_bounds(tree)

    assert len(boxes) == tree.node_count


def test_plot_areas_adds_artists():
    from manim_extensions.machine_learning.decision_tree.decision_tree_surface import (
        plot_areas,
    )

    import manim_extensions.machine_learning.decision_tree.decision_tree_surface as module

    class DummyRectangle:
        def __init__(self, *args, **kwargs):
            self.args = args

    class DummyAxes:
        def add_artist(self, artist):
            self.artist = artist

    class DummyPyplot:
        def gca(self):
            return DummyAxes()

    module.Rectangle = DummyRectangle
    module.require = lambda group, name: DummyPyplot()
    rectangles = np.array([[0.0, 1.0, 0.0, 1.0, 0.0]])
    plot_areas(rectangles)


def test_surface_override_animations():
    from manim import Circle

    from manim_extensions.machine_learning.decision_tree.decision_tree_surface import (
        DecisionTreeSurface,
    )

    surface = DecisionTreeSurface.__new__(DecisionTreeSurface)
    surface.surface_rectangles = [Circle(), Circle()]

    assert surface.create_override() is not None
    assert surface.uncreate_override() is not None
