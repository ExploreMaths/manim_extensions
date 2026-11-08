# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the embedding layer's animation and distribution helpers."""

import numpy as np
import pytest
from manim import Axes

from manim_extensions.machine_learning.neural_network import (
    EmbeddingLayer,
    FeedForwardLayer,
    NeuralNetwork,
)
from manim_extensions.machine_learning.utils.mobjects.probability import (
    GaussianDistribution,
)


@pytest.fixture()
def embedding_layer():
    network = NeuralNetwork(
        [
            FeedForwardLayer(3),
            EmbeddingLayer(dist_theme="ellipse"),
            FeedForwardLayer(3),
        ],
        layer_spacing=0.25,
    )
    return [layer for layer in network.all_layers if isinstance(layer, EmbeddingLayer)][
        0
    ]


def test_forward_pass_animation(embedding_layer):
    animation = embedding_layer.make_forward_pass_animation()

    assert animation is not None


def test_gaussian_point_cloud_is_built(embedding_layer):
    cloud = embedding_layer.construct_gaussian_point_cloud(
        [0, 0], [[1.0, 0.0], [0.0, 1.0]]
    )

    assert len(cloud) >= 1


def test_distribution_and_point_locations(embedding_layer):
    location = embedding_layer.get_distribution_location()
    sample = embedding_layer.sample_point_location_from_distribution()

    assert isinstance(location, np.ndarray)
    assert isinstance(sample, np.ndarray)


def test_add_and_remove_gaussian_distribution(embedding_layer):
    distribution = GaussianDistribution(Axes(x_range=[-3, 3], y_range=[-3, 3]))

    added = embedding_layer.add_gaussian_distribution(distribution)
    removed = embedding_layer.remove_gaussian_distribution(distribution)

    assert added is not None
    assert removed is not None
