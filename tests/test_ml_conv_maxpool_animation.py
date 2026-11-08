# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the convolution-to-max-pooling forward pass animation."""

from manim_extensions.machine_learning.neural_network import (
    Convolutional2DLayer,
    FeedForwardLayer,
    MaxPooling2DLayer,
    NeuralNetwork,
)


def _layers():
    return [
        Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
        MaxPooling2DLayer(2),
        Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
        MaxPooling2DLayer(2),
        FeedForwardLayer(3),
    ]


def test_forward_pass_animation_between_conv_and_pooling():
    network = NeuralNetwork(_layers(), layer_spacing=0.25)

    animation = network.make_forward_pass_animation()

    assert animation is not None


def test_single_conv_pool_pair_produces_animations():
    network = NeuralNetwork(
        [
            Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
            MaxPooling2DLayer(2),
            FeedForwardLayer(3),
        ],
        layer_spacing=0.25,
    )

    assert len(network.make_forward_pass_animation().animations) > 0
