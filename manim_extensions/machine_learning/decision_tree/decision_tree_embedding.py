# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Embedding of a dataset in feature space together with a decision tree's areas."""

from manim import (
    AnimationGroup,
    Axes,
    BLUE,
    Create,
    Dot,
    FadeIn,
    GREEN,
    ORANGE,
    Uncreate,
    VGroup,
    override_animation,
)
from typing import TYPE_CHECKING
from types import SimpleNamespace

import numpy as np
from manim.typing import MatrixMN, VectorND

from .decision_tree_surface import DecisionTreeSurface

if TYPE_CHECKING:
    from sklearn.tree import DecisionTreeClassifier

    from .helpers import SklearnTree


class DecisionTreeEmbedding(VGroup):
    """Two-dimensional embedding of a dataset plus the decision areas of a fitted tree.

    The data points are drawn on a pair of axes and the feature space is
    painted with the classification areas produced by the tree, so a split
    can be read together with the region it carves out.

    Parameters
    ----------
    sklearn_tree
        Fitted tree, either a
        :class:`~sklearn.tree.DecisionTreeClassifier` or its ``tree_``
        attribute.
    points
        Data points of the embedding the tree is fitted on.
    classes
        Class label of each point in ``points``.
    axes
        Axes to place the embedding on. Axes sized to the data bounds are
        created when omitted.
    class_colors
        Color per class, used for both the points and the decision areas.
    point_radius
        Radius of the dot drawn for each data point.

    Raises
    ------
    ValueError
        Raised when ``points`` is empty or when there are more classes
        than colors.

    Examples
    --------
    .. manim:: DecisionTreeEmbeddingExample
       :save_last_frame:

       from manim import *
       from sklearn.datasets import load_iris
       from sklearn.tree import DecisionTreeClassifier
       from manim_extensions.machine_learning.decision_tree.decision_tree_embedding import DecisionTreeEmbedding

       class DecisionTreeEmbeddingExample(Scene):
           def construct(self):
               iris = load_iris()
               points = iris.data[:, :2]
               tree_clf = DecisionTreeClassifier(max_depth=2, random_state=0)
               tree_clf.fit(points, iris.target)
               embedding = DecisionTreeEmbedding(tree_clf, points, iris.target)
               self.add(embedding)
    """

    def __init__(
        self,
        sklearn_tree: "DecisionTreeClassifier | SklearnTree",
        points: MatrixMN,
        classes: VectorND,
        axes: Axes | None = None,
        class_colors: list | None = None,
        point_radius: float = 0.04,
    ):
        """Build the axes, the data points, and the decision areas of the tree."""
        super().__init__()
        self.tree = (
            sklearn_tree
            if hasattr(sklearn_tree, "tree_")
            else SimpleNamespace(tree_=sklearn_tree)
        )
        self.data_points = np.asarray(points, dtype=float)
        if not self.data_points.size:
            raise ValueError("points must not be empty.")
        self.classes = np.asarray(classes).reshape(-1)
        self.class_count = int(self.classes.max()) + 1 if self.classes.size else 1
        self.class_colors = (
            list(class_colors) if class_colors is not None else [BLUE, GREEN, ORANGE]
        )
        if len(self.class_colors) < self.class_count:
            raise ValueError(
                f"At most {len(self.class_colors)} classes are supported, "
                f"got {self.class_count}."
            )
        self.axes = axes if axes is not None else self._make_axes()
        self.surface = DecisionTreeSurface(
            self.tree, self.data_points, self.axes, self.class_colors
        )
        self.points_group = self._make_points(point_radius)
        self.add(self.axes)
        self.add(self.points_group)
        self.add(VGroup(*self.surface.surface_rectangles))

    def get_points_defining_boundary(self) -> np.ndarray:
        """Return every point of the embedding, used when computing its bounds.

        The default implementation stacks the boundary points of each
        submobject, which fails because the axes, the dots, and the decision
        areas have different point counts, so all points are returned instead.

        Returns
        -------
            All points of the embedding.
        """
        return self.get_all_points()

    def _make_axes(self) -> Axes:
        """Make axes covering the data bounds with a small margin.

        Returns
        -------
            Axes sized to the embedding.
        """
        x_min, x_max = float(self.data_points[:, 0].min()), float(self.data_points[:, 0].max())
        y_min, y_max = float(self.data_points[:, 1].min()), float(self.data_points[:, 1].max())
        x_span = max(x_max - x_min, 1.0)
        y_span = max(y_max - y_min, 1.0)

        return Axes(
            x_range=[x_min - 0.2, x_max + 0.2, x_span / 5],
            y_range=[y_min - 0.2, y_max + 0.2, y_span / 5],
            x_length=5.0,
            y_length=3.0,
            tips=False,
        )

    def _make_points(self, point_radius: float) -> VGroup:
        """Make one colored dot per data point.

        Parameters
        ----------
        point_radius
            Radius of each dot.

        Returns
        -------
            The dots of the embedding.
        """
        return VGroup(
            *[
                Dot(
                    self.axes.c2p(x, y),
                    radius=point_radius,
                    color=self.class_colors[int(label)],
                )
                for (x, y), label in zip(self.data_points, self.classes)
            ]
        )

    def make_split_to_animation_map(self) -> dict[int, AnimationGroup]:
        """Map each split node to the animation revealing the areas below it.

        Returns
        -------
            Mapping from split node index to the animation of its decision
            areas.
        """
        return self.surface.make_split_to_animation_map()

    @override_animation(Create)
    def create_override(self) -> AnimationGroup:
        """Reveal the axes, the data points, and every decision area at once.

        Returns
        -------
            The create animation of the whole embedding.
        """
        animations = [Create(self.axes), FadeIn(self.points_group)]
        animations.extend(
            Create(rectangle) for rectangle in self.surface.surface_rectangles
        )

        return AnimationGroup(*animations)

    @override_animation(Uncreate)
    def uncreate_override(self) -> AnimationGroup:
        """Remove the decision areas, the data points, and the axes.

        Returns
        -------
            The reverse of
            :meth:`~manim_extensions.machine_learning.decision_tree.decision_tree_embedding.DecisionTreeEmbedding.create_override`.
        """
        animations = [
            Uncreate(rectangle) for rectangle in self.surface.surface_rectangles
        ]
        animations.append(FadeIn(self.points_group, reverse=True))
        animations.append(Uncreate(self.axes))

        return AnimationGroup(*animations)
