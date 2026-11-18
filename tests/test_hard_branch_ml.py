# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for less common machine-learning branches."""

import numpy as np
import pytest
from manim import Create, Group, tempconfig


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_manim_ml_color_scheme_names_and_invalid_value():
    from manim_extensions.machine_learning import ManimMLConfig
    from manim_extensions.machine_learning.utils.colorschemes.colorschemes import (
        dark_mode,
        light_mode,
    )

    model_config = ManimMLConfig()

    model_config.color_scheme = "dark_mode"
    assert model_config.color_scheme is dark_mode

    model_config.color_scheme = "light_mode"
    assert model_config.color_scheme is light_mode

    with pytest.raises(ValueError, match="dark_mode"):
        model_config.color_scheme = "sepia"

    model_config.color_scheme = dark_mode
    assert model_config.color_scheme is dark_mode


def test_feature_map_padding_builds_exterior_and_interior_rectangles():
    from manim_extensions.machine_learning.neural_network.layers.convolutional_2d import (
        FeatureMap,
    )

    feature_map = FeatureMap(
        feature_map_size=(3, 2),
        cell_width=0.3,
        padding=(1, 2),
        padding_dashed=True,
    )

    assert feature_map.untransformed_width == pytest.approx((3 + 2) * 0.3)
    assert feature_map.untransformed_height == pytest.approx((2 + 4) * 0.3)
    assert len(feature_map.submobjects) == 2


def test_rotated_shift_vectors_can_be_normalized():
    from types import SimpleNamespace

    from manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_convolutional_2d import (
        get_rotated_shift_vectors,
    )

    layer = SimpleNamespace(cell_width=0.5)

    raw = get_rotated_shift_vectors(layer)
    unit = get_rotated_shift_vectors(layer, normalized=True)

    for vector in raw:
        assert np.linalg.norm(vector) == pytest.approx(0.5)
    for vector in unit:
        assert np.linalg.norm(vector) == pytest.approx(1.0)


def test_conv_connective_scale_and_empty_create_override():
    from manim_extensions.machine_learning.neural_network import (
        Convolutional2DLayer,
        FeedForwardLayer,
        NeuralNetwork,
    )

    network = NeuralNetwork(
        [
            Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
            Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
            FeedForwardLayer(2),
        ],
        layer_spacing=0.25,
    )
    connective = network.connective_layers[0]
    old_cell_width = connective.cell_width

    connective.scale(2)
    animation = connective._create_override()

    assert connective.cell_width == pytest.approx(old_cell_width * 2)
    assert animation is not None


def test_filters_create_override_adds_assets():
    from manim_extensions.machine_learning.neural_network import (
        Convolutional2DLayer,
        FeedForwardLayer,
        NeuralNetwork,
    )
    from manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_convolutional_2d import (
        Filters,
    )

    network = NeuralNetwork(
        [
            Convolutional2DLayer(1, 5, 3),
            Convolutional2DLayer(2, 3, 3),
            FeedForwardLayer(2),
        ]
    )
    connective = network.connective_layers[0]
    filters = Filters(connective.input_layer, connective.output_layer)

    assert len(filters.submobjects) == 0
    animation = filters._create_override()
    animation.function(filters)

    assert len(filters.submobjects) == 3


def test_convolve_all_filters_at_once_branch():
    from manim_extensions.machine_learning.neural_network import (
        Convolutional2DLayer,
        FeedForwardLayer,
        NeuralNetwork,
    )

    network = NeuralNetwork(
        [
            Convolutional2DLayer(1, 5, 3),
            Convolutional2DLayer(2, 3, 3),
            FeedForwardLayer(2),
        ]
    )
    connective = network.connective_layers[0]

    animation = connective.make_forward_pass_animation(all_filters_at_once=True)

    assert animation is not None


def test_mcmc_axes_create_override_and_transition_without_dots():
    from manim import Dot

    from manim_extensions.machine_learning.diffusion.mcmc import MCMCAxes

    axes = MCMCAxes()
    create_animation = axes._create_override()
    start = Dot(axes.axes.coords_to_point(-1.0, -1.0))
    end = Dot(axes.axes.coords_to_point(1.0, 1.0))
    candidate = Dot(axes.axes.coords_to_point(0.0, 0.5))

    animation, line = axes.make_transition_animation(
        start, end, candidate, show_dots=False
    )

    assert create_animation is not None
    assert animation is not None
    assert line is not None


def test_posterior_accepts_explicit_mu_and_variance():
    from manim_extensions.machine_learning.diffusion.mcmc import (
        MultidimensionalGaussianPosterior,
    )

    posterior = MultidimensionalGaussianPosterior(
        mu=np.array([1.0, 2.0]), var=np.array([3.0, 4.0])
    )

    assert np.array_equal(posterior.mu, np.array([1.0, 2.0]))
    assert np.array_equal(posterior.var, np.array([3.0, 4.0]))


def test_decision_tree_create_respects_traversal_order(tmp_path):
    pytest.importorskip("sklearn")
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
    paths = []
    for index in range(3):
        path = tmp_path / f"class_{index}.png"
        PILImage.new("RGB", (16, 16), (index * 60, 0, 0)).save(path)
        paths.append(str(path))
    diagram = DecisionTreeDiagram(
        tree.tree_,
        feature_names=["sepal length", "sepal width"],
        class_names=list(iris.target_names),
        class_images_paths=paths,
    )

    level_animation = diagram.create_decision_tree("level")
    bfs_animation = diagram.create_decision_tree("bfs")

    assert level_animation is not None
    assert bfs_animation is not None
    with pytest.raises(Exception, match="Uncrecognized traversal"):
        diagram.create_decision_tree("depth")


def test_decision_tree_container_rejects_more_than_three_classes():
    from manim_extensions.machine_learning.decision_tree.decision_tree import (
        DecisionTreeContainer,
    )

    points = np.zeros((4, 2))
    with pytest.raises(ValueError, match="At most 3 classes"):
        DecisionTreeContainer(
            object(), points, classes=np.arange(4)
        ).make_unfold_tree_animation()


def test_image_layer_loads_from_path_and_accessors(tmp_path):
    from PIL import Image as PILImage
    from manim_extensions.machine_learning.neural_network.layers.image import (
        ImageLayer,
    )

    path = tmp_path / "rgb.png"
    PILImage.new("RGB", (12, 8), (10, 20, 30)).save(path)
    layer = ImageLayer.from_path(str(path), image_height=1.0)
    layer.construct_layer(None, None)

    assert layer.num_channels == 3
    assert layer.get_right()[0] > 0
    old_width = layer.width
    layer.scale(0.5)
    assert layer.width == pytest.approx(old_width * 0.5)


def test_paired_query_and_triplet_load_paths_in_both_modes(tmp_path):
    from PIL import Image as PILImage
    from manim_extensions.machine_learning.neural_network.layers.paired_query import (
        PairedQueryLayer,
    )
    from manim_extensions.machine_learning.neural_network.layers.triplet import (
        TripletLayer,
    )

    path = tmp_path / "query.png"
    PILImage.new("L", (10, 10), 128).save(path)
    paths = [str(path)] * 2

    grayscale_query = PairedQueryLayer.from_paths(*paths, grayscale=True)
    color_query = PairedQueryLayer.from_paths(*paths, grayscale=False)
    grayscale_triplet = TripletLayer.from_paths(*paths, *paths[:1], grayscale=True)
    color_triplet = TripletLayer.from_paths(*paths, *paths[:1], grayscale=False)

    assert grayscale_query is not None
    assert color_query is not None
    assert grayscale_triplet is not None
    assert color_triplet is not None


def test_vae_triplet_rgb_and_bad_dimension():
    from manim_extensions.machine_learning.neural_network.architectures.variational_autoencoder import (
        VariationalAutoencoder,
    )

    vae = VariationalAutoencoder()
    rgb = np.zeros((8, 8, 3), dtype=np.uint8)

    animation = vae.make_triplet_forward_pass((rgb, rgb, rgb))
    assert animation is not None

    with pytest.raises(ValueError, match="2D grayscale or 3D RGB"):
        vae.make_triplet_forward_pass((np.zeros((2, 2, 3, 1)),) * 3)


def test_list_group_out_of_range_error():
    from manim_extensions.machine_learning.utils.mobjects.list_group import ListGroup

    group = ListGroup()
    with pytest.raises(Exception, match="index out of range"):
        group[0]


def test_probability_mobject_unknown_theme():
    from manim import Axes

    from manim_extensions.machine_learning.utils.mobjects.probability import (
        GaussianDistribution,
    )

    axes = Axes(x_range=(-3, 3), y_range=(-3, 3), x_length=2, y_length=2)
    with pytest.raises(Exception, match="Uncrecognized distribution theme"):
        GaussianDistribution(axes, dist_theme="nope")


def test_feed_forward_architecture_builds_layers():
    from manim_extensions.machine_learning.neural_network.architectures.feed_forward import (
        FeedForwardNeuralNetwork,
    )

    network = FeedForwardNeuralNetwork([3, 5, 3])

    assert network is not None
