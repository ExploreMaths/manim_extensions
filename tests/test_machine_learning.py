# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Regression tests for the machine_learning neural network port.

The bugs fixed in ``91fb3fe`` (empty AnimationGroup/Succession played by
manim >= 0.21) are guarded here: the network forward pass and the Create
override must never contain empty animation groups, for every supported
layer topology.
"""

from manim import AnimationGroup, Axes, BLUE, Create, GREEN, RED, Succession, Text
import numpy as np
import pytest

from manim_extensions.machine_learning.neural_network import (
    Convolutional2DLayer,
    EmbeddingLayer,
    FeedForwardLayer,
    ImageLayer,
    MathOperationLayer,
    NeuralNetwork,
    PairedQueryLayer,
    VectorLayer,
)
from manim_extensions.machine_learning.neural_network.architectures import (
    VariationalAutoencoder,
)


def _assert_no_empty_group(animation, path="root"):
    """Walk an animation tree; every AnimationGroup must have subanimations."""
    animations = getattr(animation, "animations", None)
    if animations is not None:
        assert len(animations) > 0, f"empty {type(animation).__name__} at {path}"
        for index, sub in enumerate(animations):
            _assert_no_empty_group(sub, f"{path}/{type(sub).__name__}[{index}]")


def _assert_playable(animation):
    """manim >= 0.21 refuses to begin() an empty group composition."""
    _assert_no_empty_group(animation)


class TestForwardPassAnimation:
    def test_feed_forward_network(self):
        nn = NeuralNetwork(
            [
                FeedForwardLayer(3),
                FeedForwardLayer(5, activation_function="Sigmoid"),
                FeedForwardLayer(3),
            ]
        )
        _assert_playable(nn.make_forward_pass_animation())

    def test_cnn_network_with_inactive_conv_layers(self):
        # Convolutional2DLayer without activation returns an empty group
        # upstream; the network must skip it instead of playing it.
        nn = NeuralNetwork(
            [
                Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
                Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
                Convolutional2DLayer(5, 3, 3, filter_spacing=0.18),
                FeedForwardLayer(3),
                FeedForwardLayer(3),
            ],
            layer_spacing=0.25,
        )
        _assert_playable(nn.make_forward_pass_animation())

    def test_embedding_network(self):
        nn = NeuralNetwork(
            [
                FeedForwardLayer(3),
                EmbeddingLayer(dist_theme="ellipse"),
                FeedForwardLayer(3),
            ]
        )
        _assert_playable(nn.make_forward_pass_animation())

    def test_vector_output_network(self):
        nn = NeuralNetwork([FeedForwardLayer(3), VectorLayer(4)])
        _assert_playable(nn.make_forward_pass_animation())

    def test_image_network(self):
        yy, xx = np.mgrid[0:28, 0:28]
        image = np.where((yy - 14) ** 2 + (xx - 14) ** 2 < 81, 200, 0).astype(
            np.uint8
        )
        nn = NeuralNetwork(
            [
                ImageLayer(image, height=1.5),
                Convolutional2DLayer(1, 7, filter_spacing=0.32),
                FeedForwardLayer(3),
            ],
            layer_spacing=0.25,
        )
        _assert_playable(nn.make_forward_pass_animation())

    def test_paired_query_network(self):
        from manim_extensions.machine_learning.utils.mobjects.image import (
            GrayscaleImageMobject,
        )

        yy, xx = np.mgrid[0:28, 0:28]
        positive = np.where((yy - 14) ** 2 + (xx - 14) ** 2 < 81, 200, 0).astype(
            np.uint8
        )
        negative = np.where((yy - 20) ** 2 + (xx - 20) ** 2 < 81, 200, 0).astype(
            np.uint8
        )
        query = PairedQueryLayer(
            GrayscaleImageMobject(positive, height=0.6),
            GrayscaleImageMobject(negative, height=0.6),
        )
        nn = NeuralNetwork([query, FeedForwardLayer(3)])
        _assert_playable(nn.make_forward_pass_animation())

    def test_math_operation_network(self):
        nn = NeuralNetwork(
            {
                "feed_forward_1": FeedForwardLayer(3),
                "feed_forward_2": FeedForwardLayer(3, activation_function="ReLU"),
                "sum": MathOperationLayer("+", activation_function="ReLU"),
            },
            layer_spacing=0.38,
        )
        nn.add_connection("feed_forward_1", "sum")
        nn.add_connection("feed_forward_2", "sum")
        _assert_playable(nn.make_forward_pass_animation())

    def test_per_layer_animation_map_has_no_empty_groups(self):
        nn = NeuralNetwork([FeedForwardLayer(2), FeedForwardLayer(2)])
        per_layer = nn.make_forward_pass_animation(per_layer_animations=True)
        assert len(per_layer) == len(nn.all_layers)
        for animation in per_layer.values():
            _assert_no_empty_group(animation)


class TestCreateOverride:
    @pytest.mark.parametrize(
        "layers",
        [
            [FeedForwardLayer(3), FeedForwardLayer(3)],
            [FeedForwardLayer(3), VectorLayer(4)],
            [FeedForwardLayer(3), EmbeddingLayer(dist_theme="ellipse"), FeedForwardLayer(3)],
            [
                Convolutional2DLayer(1, 5, 3),
                FeedForwardLayer(3),
            ],
        ],
    )
    def test_create_animation_is_playable(self, layers):

        nn = NeuralNetwork(layers)
        _assert_playable(Create(nn))

    def test_create_twice_returns_playable_animation(self):

        nn = NeuralNetwork([FeedForwardLayer(2), FeedForwardLayer(2)])
        _assert_playable(Create(nn))
        _assert_playable(Create(nn))


class TestLayerValidation:
    def test_vector_layer_cannot_be_input(self):
        # There is no Vector->FeedForward connective layer upstream.
        with pytest.raises(TypeError):
            NeuralNetwork([VectorLayer(4), FeedForwardLayer(3)])

    def test_invalid_math_operation_rejected(self):
        with pytest.raises(AssertionError):
            MathOperationLayer("SUM")


class TestVariationalAutoencoder:
    def test_constructs(self):
        vae = VariationalAutoencoder()
        # The VAE is a thin wrapper around its inner network.
        assert vae.neural_network is not None
        assert vae.embedding_layer is not None

    def test_create_is_playable(self):

        vae = VariationalAutoencoder()
        _assert_playable(Create(vae))


class TestOtherMLModules:
    def test_mcmc_axes_construct(self):
        from manim_extensions.machine_learning.diffusion.mcmc import MCMCAxes

        axes = MCMCAxes()
        assert axes is not None

    def test_decision_tree_diagram_construct(self, tmp_path):
        pytest.importorskip("sklearn", exc_type=ImportError)
        from PIL import Image as PILImage
        from sklearn.datasets import load_iris
        from sklearn.tree import DecisionTreeClassifier

        from manim_extensions.machine_learning.decision_tree.decision_tree import (
            DecisionTreeDiagram,
        )

        iris = load_iris()
        tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(
            iris.data[:, :2], iris.target
        )
        image_paths = []
        for index in range(3):
            path = tmp_path / f"class_{index}.png"
            PILImage.new("RGB", (32, 32), (255, 0, 0)).save(path)
            image_paths.append(str(path))
        diagram = DecisionTreeDiagram(
            tree.tree_,
            feature_names=["sepal length", "sepal width"],
            class_names=list(iris.target_names),
            class_images_paths=image_paths,
        )
        assert len(diagram.submobjects) > 0


class TestDecisionTreeHelpers:
    class FakeTree:
        """Minimal sklearn-tree stand-in for traversal tests."""

        node_count = 5
        children_left = [1, 3, -1, -1, -1]
        children_right = [2, 4, -1, -1, -1]
        impurity = [0.5, 0.25, 0.4, 0.0, 0.0]

    def test_best_first_orders_by_impurity(self):
        from manim_extensions.machine_learning.decision_tree import helpers

        traversal = helpers.compute_best_first_traversal(self.FakeTree())
        # Root (0.5) -> right child (0.4) -> left child (0.25) -> leaves (0.0)
        assert traversal == [0, 2, 1, 3, 4]

    def test_best_first_visits_every_node_once(self):
        from manim_extensions.machine_learning.decision_tree import helpers

        traversal = helpers.compute_best_first_traversal(self.FakeTree())
        assert sorted(traversal) == list(range(self.FakeTree.node_count))


class TestLeafNode:
    def test_text_node_uses_class_name(self):
        from manim_extensions.machine_learning.decision_tree.decision_tree import (
            LeafNode,
        )

        leaf = LeafNode(
            class_index=1,
            display_type="text",
            class_colors=[BLUE, GREEN, RED],
            class_names=["setosa", "versicolor", "virginica"],
        )
        texts = [mobject for mobject in leaf.submobjects if isinstance(mobject, Text)]
        assert len(texts) == 1
        assert texts[0].text == "versicolor"

    def test_text_node_falls_back_to_class_index(self):
        from manim_extensions.machine_learning.decision_tree.decision_tree import (
            LeafNode,
        )

        leaf = LeafNode(class_index=2, display_type="text", class_colors=[BLUE, GREEN, RED])
        texts = [mobject for mobject in leaf.submobjects if isinstance(mobject, Text)]
        assert len(texts) == 1
        assert texts[0].text == "2"


class TestDecisionTreeDiagramExpansion:
    def _make_diagram(self, tmp_path):
        pytest.importorskip("sklearn", exc_type=ImportError)
        from PIL import Image as PILImage
        from sklearn.datasets import load_iris
        from sklearn.tree import DecisionTreeClassifier

        from manim_extensions.machine_learning.decision_tree.decision_tree import (
            DecisionTreeDiagram,
        )

        iris = load_iris()
        self.tree = DecisionTreeClassifier(max_depth=2, random_state=0).fit(
            iris.data[:, :2], iris.target
        )
        image_paths = []
        for index in range(3):
            path = tmp_path / f"class_{index}.png"
            PILImage.new("RGB", (32, 32), (255, 0, 0)).save(path)
            image_paths.append(str(path))
        diagram = DecisionTreeDiagram(
            self.tree.tree_,
            feature_names=["sepal length", "sepal width"],
            class_names=list(iris.target_names),
            class_images_paths=image_paths,
        )

        return diagram

    def test_bfs_expansion_returns_animation_and_split_map(self, tmp_path):
        diagram = self._make_diagram(tmp_path)
        expansion, split_node_animations = (
            diagram.create_bfs_expansion_decision_tree(diagram.tree)
        )
        _assert_playable(expansion)
        split_indices = {
            node_index
            for node_index in range(self.tree.tree_.node_count)
            if self.tree.tree_.children_left[node_index]
            != self.tree.tree_.children_right[node_index]
        }
        assert set(split_node_animations) == split_indices
        for animation in split_node_animations.values():
            _assert_playable(animation)

    def test_level_order_expansion_is_playable(self, tmp_path):
        diagram = self._make_diagram(tmp_path)
        expansion = diagram.create_level_order_expansion_decision_tree(diagram.tree)
        _assert_playable(expansion)

    def test_best_first_expansion_is_playable(self, tmp_path):
        from manim_extensions.machine_learning.decision_tree import helpers

        diagram = self._make_diagram(tmp_path)
        order = helpers.compute_best_first_traversal(diagram.tree)
        expansion = diagram.make_expand_tree_animation(order)
        _assert_playable(expansion)


class TestDecisionTreeSurface:
    def test_split_to_animation_map_covers_split_nodes(self):
        pytest.importorskip("sklearn", exc_type=ImportError)
        from sklearn.datasets import load_iris
        from sklearn.tree import DecisionTreeClassifier

        from manim_extensions.machine_learning.decision_tree.decision_tree_surface import (
            DecisionTreeSurface,
        )

        iris = load_iris()
        points = iris.data[:, :2]
        tree_clf = DecisionTreeClassifier(max_depth=2, random_state=0).fit(
            points, iris.target
        )
        axes = Axes(x_range=[3, 9, 1], y_range=[1, 5, 1], x_length=5, y_length=4)
        surface = DecisionTreeSurface(tree_clf, points, axes)
        split_to_animation = surface.make_split_to_animation_map()
        split_indices = {
            node_index
            for node_index in range(tree_clf.tree_.node_count)
            if tree_clf.tree_.children_left[node_index]
            != tree_clf.tree_.children_right[node_index]
        }
        assert set(split_to_animation) == split_indices
        for animation in split_to_animation.values():
            assert isinstance(animation, AnimationGroup)
            assert len(animation.animations) > 0


class TestActivationEvaluation:
    def test_evaluate_animation_highlights_a_point(self):
        from manim_extensions.machine_learning.neural_network.activation_functions import (
            SigmoidFunction,
        )

        animation = SigmoidFunction().make_evaluate_animation(x_val=0.5)
        assert isinstance(animation, Succession)
        _assert_playable(animation)

    def test_evaluate_animation_uses_random_x_when_omitted(self):
        from manim_extensions.machine_learning.neural_network.activation_functions import (
            SigmoidFunction,
        )

        animation = SigmoidFunction().make_evaluate_animation()
        _assert_playable(animation)


class TestEdgeColorModification:
    def _make_connective_layer(self):
        nn = NeuralNetwork([FeedForwardLayer(2), FeedForwardLayer(2)])
        return nn.connective_layers[0]

    def test_explicit_colors(self):
        connective = self._make_connective_layer()
        colors = [BLUE for _ in connective.edges]
        connective.modify_edge_colors(colors=colors)
        for edge in connective.edges:
            assert edge.get_color() == BLUE

    def test_magnitudes_mapped_through_colormap(self):
        pytest.importorskip("matplotlib", exc_type=ImportError)
        connective = self._make_connective_layer()
        magnitudes = np.linspace(0.0, 1.0, len(connective.edges))
        connective.modify_edge_colors(magnitudes=magnitudes)
        assert len({edge.get_color().to_hex() for edge in connective.edges}) > 1

    def test_requires_colors_or_magnitudes(self):
        connective = self._make_connective_layer()
        with pytest.raises(ValueError):
            connective.modify_edge_colors()


class TestReplaceLayer:
    def test_replace_layer_swaps_the_layer(self):
        nn = NeuralNetwork(
            [FeedForwardLayer(3), FeedForwardLayer(4), FeedForwardLayer(3)]
        )
        old_layer = nn.input_layers[1]
        new_layer = FeedForwardLayer(5)
        animation = nn.replace_layer(old_layer, new_layer)
        assert isinstance(animation, Succession)
        # The structure swap happens while the UpdateFromFunc animation plays.
        animation.animations[1].update_function(nn)
        assert nn.input_layers[1] is new_layer
        assert all(layer is not old_layer for layer in nn.input_layers.items)
        _assert_playable(nn.make_forward_pass_animation())

    def test_replace_unknown_layer_raises(self):
        nn = NeuralNetwork([FeedForwardLayer(3), FeedForwardLayer(3)])
        with pytest.raises(Exception):
            nn.replace_layer(FeedForwardLayer(3), FeedForwardLayer(3))


class TestTripletForwardPass:
    def test_triplet_forward_pass_is_playable(self):
        vae = VariationalAutoencoder()
        image = np.zeros((8, 8), dtype=np.uint8)
        animation = vae.make_triplet_forward_pass((image, image, image))
        assert isinstance(animation, AnimationGroup)
        _assert_playable(animation)

    def test_triplet_requires_three_images(self):
        vae = VariationalAutoencoder()
        image = np.zeros((8, 8), dtype=np.uint8)
        with pytest.raises(ValueError):
            vae.make_triplet_forward_pass((image, image))


class TestThreeChannelImageForwardPass:
    def test_rgb_image_network_is_playable(self):
        rgb_image = np.zeros((16, 16, 3), dtype=np.uint8)
        nn = NeuralNetwork(
            [
                ImageLayer(rgb_image, height=1.2),
                Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
            ],
            layer_spacing=0.25,
        )
        _assert_playable(nn.make_forward_pass_animation())
