# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Regression tests for the machine_learning neural network port.

The bugs fixed in ``91fb3fe`` (empty AnimationGroup/Succession played by
manim >= 0.21) are guarded here: the network forward pass and the Create
override must never contain empty animation groups, for every supported
layer topology.
"""

from manim import Create
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
