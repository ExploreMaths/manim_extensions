# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: implement text leaf nodes and the tree expansion animations

"""
Module for visualizing decision trees in Manim.
It parses a decision tree classifier from sklearn.
"""

# unlinked-class-ok: Node

from typing import Literal

from manim import (
    Animation,
    AnimationGroup,
    BLUE,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    GREEN,
    Group,
    ImageMobject,
    Line,
    Mobject,
    ORIGIN,
    RED,
    Rectangle,
    Succession,
    SurroundingRectangle,
    Text,
    UP,
    VGroup,
    WHITE,
    override_animation,
)

from . import helpers
from .decision_tree_embedding import DecisionTreeEmbedding

from types import SimpleNamespace

import numpy as np
from PIL import Image
from manim.typing import Point2D_Array, VectorND


class LeafNode(Group):
    """Leaf node in tree.

    Parameters
    ----------
    class_index
        Index of the predicted class, used to look up the class image and color.
    display_type
        How to display the leaf content; ``"image"`` shows the class image,
        ``"text"`` shows the class name.
    class_image_paths
        List of image file paths, one per class.
    class_colors
        List of colors, one per class, used for the border rectangle.
    class_names
        List of class names, one per class, used by the ``"text"`` display
        type. The class index is displayed when omitted.

    Examples
    --------
    .. manim:: LeafNodeScene
       :save_last_frame:

       import matplotlib.pyplot as plt
       import numpy as np
       from manim import *
       from manim_extensions.machine_learning.decision_tree.decision_tree import LeafNode

       class LeafNodeScene(Scene):
           def construct(self):
               plt.imsave("leaf_class_0.png", np.ones((16, 16, 3)))
               leaf = LeafNode(
                   class_index=0,
                   class_image_paths=["leaf_class_0.png"],
                   class_colors=[BLUE],
               )
               leaf.scale(10)
               self.add(leaf)

    .. manim:: LeafNodeText
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.decision_tree.decision_tree import LeafNode

       class LeafNodeText(Scene):
           def construct(self):
               leaf = LeafNode(
                   class_index=1,
                   display_type="text",
                   class_colors=[BLUE, GREEN, RED],
                   class_names=["setosa", "versicolor", "virginica"],
               )
               leaf.scale(1.5)
               self.add(leaf)
    """

    def __init__(
        self,
        class_index: int,
        display_type: str = "image",
        class_image_paths: list = [],
        class_colors: list = [],
        class_names: list[str] | None = None,
    ):
        super().__init__()
        self.display_type = display_type
        self.class_image_paths = class_image_paths
        self.class_colors = class_colors
        self.class_names = class_names
        assert self.display_type in ["image", "text"]
        if self.display_type == "image":
            self._construct_image_node(class_index)
        else:
            self._construct_text_node(class_index)

    def _construct_text_node(self, class_index: int):
        """Make a text node."""
        if self.class_names is None:
            label = str(class_index)
        else:
            label = self.class_names[class_index]
        color = self.class_colors[class_index] if self.class_colors else WHITE
        node = Text(label, color=WHITE)
        rectangle = SurroundingRectangle(node, buff=0.3, color=color, stroke_width=6)
        self.add(rectangle)
        self.add(node)

    def _construct_image_node(self, class_index: int):
        """Make an image node."""
        # Get image
        image_path = self.class_image_paths[class_index]
        pil_image = Image.open(image_path)
        node = ImageMobject(pil_image)
        node.scale(1.5)
        rectangle = Rectangle(
            width=node.width + 0.05,
            height=node.height + 0.05,
            color=self.class_colors[class_index],
            stroke_width=6,
        )
        rectangle.move_to(node.get_center())
        rectangle.shift([-0.02, 0.02, 0])
        self.add(rectangle)
        self.add(node)


class SplitNode(VGroup):
    """Node for splitting decision in tree.

    Parameters
    ----------
    feature
        Name of the feature used for the split.
    threshold
        Threshold value of the split; the node text shows ``feature <= threshold``.

    Examples
    --------
    .. manim:: SplitNodeScene
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.decision_tree.decision_tree import SplitNode

       class SplitNodeScene(Scene):
           def construct(self):
               self.add(SplitNode(feature=0, threshold=0.5).scale(2))
    """

    def __init__(self, feature: int | str, threshold: float):
        super().__init__()
        node_text = f"{feature}\n<=  {threshold:.2f}"
        # Draw decision text
        decision_text = Text(node_text, color=WHITE)
        # Draw the surrounding box
        bounding_box = SurroundingRectangle(decision_text, buff=0.3, color=WHITE)
        self.add(bounding_box)
        self.add(decision_text)


class DecisionTreeDiagram(Group):
    """Decision Tree Diagram Class for Manim.

    Parameters
    ----------
    sklearn_tree
        Fitted scikit-learn decision tree classifier to visualize.
    feature_names
        Names of the features, used to label the split nodes.
    class_names
        Names of the classes.
    class_images_paths
        Image file paths, one per class, used for the leaf nodes.
    class_colors
        Colors, one per class, used for the leaf node borders.


    Examples
    --------
    .. manim:: DecisionTreeDiagramScene
       :save_last_frame:

       from manim import *
       import tempfile
       from pathlib import Path
       import numpy as np
       from PIL import Image as PILImage
       from sklearn.datasets import load_iris
       from sklearn.tree import DecisionTreeClassifier
       from manim_extensions.machine_learning.decision_tree.decision_tree import (
           DecisionTreeDiagram,
       )

       class DecisionTreeDiagramScene(Scene):
           def construct(self):
               iris = load_iris()
               tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(
                   iris.data[:, :2], iris.target
               )
               tmp_dir = Path(tempfile.mkdtemp())
               image_paths = []
               for i, color in enumerate([RED, GREEN, BLUE]):
                   path = tmp_dir / f"class_{i}.png"
                   rgb = tuple(int(c * 255) for c in color_to_rgb(color))
                   PILImage.new("RGB", (32, 32), rgb).save(path)
                   image_paths.append(str(path))
               diagram = DecisionTreeDiagram(
                   tree.tree_,
                   feature_names=["sepal length", "sepal width"],
                   class_names=list(iris.target_names),
                   class_images_paths=image_paths,
               )
               diagram.scale_to_fit_width(6)
               if diagram.height > 6:
                   diagram.scale_to_fit_height(6)
               diagram.move_to(ORIGIN)
               self.add(diagram)
    """

    def __init__(
        self,
        sklearn_tree: helpers.SklearnTree,
        feature_names: list[str] | None = None,
        class_names: list[str] | None = None,
        class_images_paths: list[str] | None = None,
        class_colors: list = [RED, GREEN, BLUE],
    ):
        super().__init__()
        self.tree = sklearn_tree
        self.feature_names = feature_names
        self.class_names = class_names
        self.class_image_paths = class_images_paths
        self.class_colors = class_colors
        # Make graph container for the tree
        self.tree_group, self.nodes_map, self.edge_map = self._make_tree()
        self.add(self.tree_group)

    def _make_node(
        self,
        node_index: int,
    ):
        """Create a split or leaf node mobject for the given tree node index."""
        is_split_node = (
            self.tree.children_left[node_index] != self.tree.children_right[node_index]
        )
        if is_split_node:
            node_feature = self.tree.feature[node_index]
            node_threshold = self.tree.threshold[node_index]
            node = SplitNode(self.feature_names[node_feature], node_threshold)
        else:
            # Get the most abundant class for the given leaf node
            # Make the leaf node object
            tree_class_index = np.argmax(self.tree.value[node_index])
            node = LeafNode(
                class_index=tree_class_index,
                class_colors=self.class_colors,
                class_image_paths=self.class_image_paths,
                class_names=self.class_names,
                display_type="image" if self.class_image_paths else "text",
            )
        return node

    def _make_connection(self, top: Mobject, bottom: Mobject, is_leaf: bool = False):
        """Make a connection from top to bottom."""
        top_node_bottom_location = top.get_center()
        top_node_bottom_location[1] -= top.height / 2
        bottom_node_top_location = bottom.get_center()
        bottom_node_top_location[1] += bottom.height / 2

        line = Line(top_node_bottom_location, bottom_node_top_location, color=WHITE)

        return line

    def _make_tree(self):
        """Construct the tree diagram."""
        tree_group = Group()
        max_depth = self.tree.max_depth
        # Make the root node
        nodes_map = {}
        root_node = self._make_node(
            node_index=0,
        )
        nodes_map[0] = root_node
        tree_group.add(root_node)
        # Save some information
        node_width = root_node.width
        scale_factor = 1.0
        edge_map = {}
        tree_width = scale_factor * 2**max_depth * node_width

        # traverse tree
        def recurse(
            node_index: int,
            depth: int,
            direction: str,
            parent_object: Mobject,
            parent_node: int,
        ):
            """Recursively build tree nodes and connections at the given depth."""
            # make the node object
            is_leaf = (
                self.tree.children_left[node_index]
                == self.tree.children_right[node_index]
            )
            node_object = self._make_node(node_index=node_index)
            nodes_map[node_index] = node_object
            node_height = node_object.height
            # set the node position
            direction_factor = -1 if direction == "left" else 1
            shift_right_amount = (
                0.9 * direction_factor * scale_factor * tree_width / (2**depth) / 2
            )
            shift_down_amount = (
                -((parent_object.height + node_height) / 2 + 0.3) * scale_factor
            )
            node_object.match_x(parent_object).match_y(parent_object).shift(
                [shift_right_amount, shift_down_amount, 0]
            )
            tree_group.add(node_object)
            # make a connection
            connection = self._make_connection(
                parent_object, node_object, is_leaf=is_leaf
            )
            edge_name = str(parent_node) + "," + str(node_index)
            edge_map[edge_name] = connection
            tree_group.add(connection)
            # recurse
            if not is_leaf:
                recurse(
                    self.tree.children_left[node_index],
                    depth + 1,
                    "left",
                    node_object,
                    node_index,
                )
                recurse(
                    self.tree.children_right[node_index],
                    depth + 1,
                    "right",
                    node_object,
                    node_index,
                )

        recurse(self.tree.children_left[0], 1, "left", root_node, 0)
        recurse(self.tree.children_right[0], 1, "right", root_node, 0)

        tree_group.scale(0.35)
        return tree_group, nodes_map, edge_map

    def _make_placeholder_leaf(self, class_index: int) -> LeafNode:
        """Make a leaf node showing the dominant class of a tree node.

        Parameters
        ----------
        class_index
            Index of the dominant class of the tree node.

        Returns
        -------
            A leaf node displaying the dominant class.
        """
        if not self.class_image_paths:
            return LeafNode(
                class_index=class_index,
                display_type="text",
                class_colors=self.class_colors,
                class_names=self.class_names,
            )
        return LeafNode(
            class_index=class_index,
            class_colors=self.class_colors,
            class_image_paths=self.class_image_paths,
        )

    def _make_expansion_animations(
        self, node_expand_order: list[int]
    ) -> tuple[list, dict]:
        """Build the animations that expand the tree in the given node order.

        Every split node starts as a placeholder leaf node showing its
        dominant class; when the node is expanded the placeholder is replaced
        by the split node and the two children are created.

        Parameters
        ----------
        node_expand_order
            Node indices in the order they should be expanded.

        Returns
        -------
            ``(animations, split_node_animations)`` — the list of animations
            and a mapping from each split node index to its split animation.
        """
        animations = []
        split_node_animations = {}
        placeholder_class_nodes = {}
        # Show the root node as its dominant class first.
        root_class_index = int(np.argmax(self.tree.value[0]))
        root_placeholder_node = self._make_placeholder_leaf(root_class_index)
        root_placeholder_node.move_to(self.nodes_map[0])
        root_placeholder_node.scale_to_fit_height(self.nodes_map[0].height)
        placeholder_class_nodes[0] = root_placeholder_node
        animations.append(AnimationGroup(FadeIn(root_placeholder_node), lag_ratio=0.0))
        for node_index in node_expand_order:
            left_child_index = self.tree.children_left[node_index]
            right_child_index = self.tree.children_right[node_index]
            is_leaf_node = left_child_index == right_child_index
            if is_leaf_node:
                # Leaf nodes are revealed when their parent split expands.
                continue
            # Replace the placeholder class node with the split node.
            split_animations = []
            placeholder_node = placeholder_class_nodes.pop(node_index, None)
            if placeholder_node is not None:
                split_animations.append(FadeOut(placeholder_node))
            split_animations.append(FadeIn(self.nodes_map[node_index]))
            # Create the children and connect them to the split node.
            children_animations = []
            for child_index in (left_child_index, right_child_index):
                edge = self.edge_map[f"{node_index},{child_index}"]
                child_left_index = self.tree.children_left[child_index]
                child_right_index = self.tree.children_right[child_index]
                if child_left_index == child_right_index:
                    child_animation = AnimationGroup(
                        FadeIn(self.nodes_map[child_index]),
                        Create(edge),
                        lag_ratio=0.0,
                    )
                else:
                    child_class_index = int(np.argmax(self.tree.value[child_index]))
                    placeholder_child = self._make_placeholder_leaf(child_class_index)
                    placeholder_child.move_to(self.nodes_map[child_index])
                    placeholder_child.scale_to_fit_height(
                        self.nodes_map[child_index].height
                    )
                    placeholder_class_nodes[child_index] = placeholder_child
                    child_animation = AnimationGroup(
                        FadeIn(placeholder_child),
                        Create(edge),
                        lag_ratio=0.0,
                    )
                children_animations.append(child_animation)
            split_animations.append(AnimationGroup(*children_animations, lag_ratio=0.0))
            split_animation = AnimationGroup(*split_animations, lag_ratio=0.0)
            animations.append(split_animation)
            split_node_animations[node_index] = split_animation

        return animations, split_node_animations

    def create_level_order_expansion_decision_tree(self, tree: Mobject) -> Succession:
        """Expands the decision tree in level order.

        Parameters
        ----------
        tree
            The sklearn tree structure (``tree_`` attribute of a fitted
            :class:`~sklearn.tree.DecisionTreeClassifier`).

        Returns
        -------
            The expansion animation.
        """
        node_expand_order = helpers.compute_level_order_traversal(self.tree)
        animations, _ = self._make_expansion_animations(node_expand_order)

        return Succession(*animations, lag_ratio=1.0)

    def create_bfs_expansion_decision_tree(self, tree: Mobject) -> tuple:
        """Expands the tree using BFS.

        Parameters
        ----------
        tree
            The sklearn tree structure (``tree_`` attribute of a fitted
            :class:`~sklearn.tree.DecisionTreeClassifier`).

        Returns
        -------
            ``(Succession, dict)`` — the expansion animation and a mapping
            from each split node index to its split animation.
        """
        node_expand_order = helpers.compute_bfs_traversal(self.tree)
        animations, split_node_animations = self._make_expansion_animations(
            node_expand_order
        )

        return Succession(*animations, lag_ratio=1.0), split_node_animations

    def make_expand_tree_animation(
        self, node_expand_order: list[int]
    ) -> AnimationGroup:
        """Make an animation for expanding the decision tree.

        Shows each split node as a leaf node initially, and then when it
        comes up shows it as a split node. The reason for this is for
        purposes of animating each of the splits in a decision surface.

        Parameters
        ----------
        node_expand_order
            Node indices in the order they should be expanded, as returned
            by the traversal helpers in
            `helpers` module.

        Returns
        -------
            The tree expansion animation.
        """
        animations, _ = self._make_expansion_animations(node_expand_order)

        return AnimationGroup(*animations, lag_ratio=1.0)

    @override_animation(Create)
    def create_decision_tree(
        self, traversal_order: Literal["bfs", "level", "best"] = "bfs"
    ) -> Animation | None:
        """Makes a create animation for the decision tree.

        Parameters
        ----------
        traversal_order
            Order in which the nodes are expanded: ``"bfs"`` (breadth-first)
            or ``"level"`` (level order).

        Returns
        -------
            The computed result.

        Raises
        ------
        Exception
            Raised when ``traversal_order`` is not recognized.
        """
        # Compute the node expand order
        if traversal_order == "level":
            node_expand_order = helpers.compute_level_order_traversal(self.tree)
        elif traversal_order == "bfs":
            node_expand_order = helpers.compute_bfs_traversal(self.tree)
        else:
            raise Exception(f"Uncrecognized traversal: {traversal_order}")
        # Make the animation
        expand_tree_animation = self.make_expand_tree_animation(node_expand_order)
        return expand_tree_animation


class DecisionTreeContainer:
    """Couples the tree diagram with the decision surface built from the same fitted tree.

    Parameters
    ----------
    sklearn_tree
        Fitted scikit-learn decision tree classifier to visualize.
    points
        Data points of the embedding the tree is fitted on.
    classes
        Class label of each point in ``points``.
    """

    def __init__(
        self,
        sklearn_tree: helpers.SklearnTree,
        points: Point2D_Array,
        classes: VectorND,
    ):
        self.sklearn_tree = sklearn_tree
        self.points = points
        self.classes = classes

    def make_unfold_tree_animation(
        self, traversal_order: Literal["bfs", "level", "best"] = "bfs"
    ) -> Succession:
        """Unfold the tree through the given traversal while the decision surface splits.

        The diagram expands one split at a time, and the region that split
        carves out of the feature space is drawn underneath it, so every split
        can be read together with the decision area it produces.

        Parameters
        ----------
        traversal_order
            Order in which the split nodes expand: ``"bfs"`` (breadth first),
            ``"level"`` (level order) or ``"best"`` (most informative split
            first).

        Returns
        -------
            The animation unfolding the tree together with its decision
            surface.

        Raises
        ------
        Exception
            Raised when ``traversal_order`` is not recognized.
        ValueError
            Raised when more than three classes are present.

        Examples
        --------
        .. code-block:: python

           container = DecisionTreeContainer(clf.tree_, points, classes)
           self.play(container.make_unfold_tree_animation())
        """
        tree = (
            self.sklearn_tree
            if hasattr(self.sklearn_tree, "tree_")
            else SimpleNamespace(tree_=self.sklearn_tree)
        )
        points = np.asarray(self.points, dtype=float)
        class_labels = np.asarray(self.classes).reshape(-1)
        class_count = int(class_labels.max()) + 1 if class_labels.size else 1
        class_colors = [BLUE, GREEN, RED][:class_count]
        if len(class_colors) < class_count:
            raise ValueError(f"At most 3 classes are supported, got {class_count}.")
        class_names = [f"class {index}" for index in range(class_count)]

        diagram = DecisionTreeDiagram(
            tree.tree_,
            feature_names=[f"x{index}" for index in range(tree.tree_.n_features)],
            class_names=class_names,
            class_colors=class_colors,
        )
        diagram.to_edge(UP, buff=0.4)

        embedding = DecisionTreeEmbedding(
            tree, points, class_labels, class_colors=class_colors
        )
        embedding.next_to(diagram, DOWN, buff=0.6)
        Group(diagram, embedding).move_to(ORIGIN)

        if traversal_order == "level":
            node_expand_order = helpers.compute_level_order_traversal(tree.tree_)
        elif traversal_order == "bfs":
            node_expand_order = helpers.compute_bfs_traversal(tree.tree_)
        elif traversal_order == "best":
            node_expand_order = helpers.compute_best_first_traversal(tree.tree_)
        else:
            raise Exception(f"Uncrecognized traversal: {traversal_order}")

        tree_animations, split_animations = diagram._make_expansion_animations(
            node_expand_order
        )
        split_animations = {int(key): value for key, value in split_animations.items()}
        surface_animations = embedding.make_split_to_animation_map()

        steps = [
            Create(embedding.axes, run_time=1.0),
            FadeIn(embedding.points_group, run_time=1.0),
        ]
        steps.append(tree_animations[0])
        for node_index in (int(index) for index in node_expand_order):
            if node_index not in split_animations:
                continue
            animations = [split_animations[node_index]]
            if node_index in surface_animations:
                animations.append(surface_animations[node_index])
            steps.append(AnimationGroup(*animations, lag_ratio=1.0))

        return Succession(*steps, lag_ratio=1.0)
