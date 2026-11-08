# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the all-at-once convolutional filter animation."""

import pytest
from manim import VMobject, tempconfig

from manim_extensions.machine_learning.neural_network import (
    Convolutional2DLayer,
    FeedForwardLayer,
    NeuralNetwork,
)


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_all_filters_at_once_produces_animation():
    network = NeuralNetwork(
        [
            Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
            Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
            FeedForwardLayer(3),
        ],
        layer_spacing=0.25,
    )

    connective = network.connective_layers[0]

    animation = connective.animate_filters_all_at_once(VMobject())

    assert animation is not None


def test_connective_layer_constructs_content():
    network = NeuralNetwork(
        [
            Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
            Convolutional2DLayer(2, 5, 3, filter_spacing=0.32),
            FeedForwardLayer(2),
        ],
        layer_spacing=0.25,
    )

    layer = network.all_layers[1]

    assert layer is not None
