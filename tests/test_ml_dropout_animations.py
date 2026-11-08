# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the neural-network dropout animation helpers."""

import pytest

from manim_extensions.machine_learning.neural_network import (
    FeedForwardLayer,
    NeuralNetwork,
)
from manim_extensions.machine_learning.neural_network.animations.dropout import (
    get_edges_to_drop_out,
    make_forward_pass_with_dropout_animation,
    make_neural_network_dropout_animation,
    make_post_dropout_animation,
    make_pre_dropout_animation,
)
from manim_extensions.machine_learning.neural_network.layers.feed_forward_to_feed_forward import (
    FeedForwardToFeedForward,
)


@pytest.fixture()
def network_and_mapping():
    network = NeuralNetwork([FeedForwardLayer(3), FeedForwardLayer(2)])
    layers = network.filter_layers(lambda layer: isinstance(layer, FeedForwardLayer))
    mapping = {layers[0]: [0], layers[1]: [1]}
    return network, mapping


def test_edges_to_drop_out(network_and_mapping):
    network, mapping = network_and_mapping
    connective = network.filter_layers(
        lambda layer: isinstance(layer, FeedForwardToFeedForward)
    )[0]

    edges, indices = get_edges_to_drop_out(connective, mapping)

    assert len(edges) > 0
    assert len(edges) == len(indices)


def test_pre_dropout_animation_returns_group_and_marks(network_and_mapping):
    network, mapping = network_and_mapping

    group, marks = make_pre_dropout_animation(network, mapping)

    assert len(group.animations) > 0
    assert len(marks) > 0


def test_post_dropout_animation(network_and_mapping):
    network, mapping = network_and_mapping
    _, marks = make_pre_dropout_animation(network, mapping)

    group = make_post_dropout_animation(network, mapping, marks)

    assert len(group.animations) > 0


def test_forward_pass_with_dropout(network_and_mapping):
    network, mapping = network_and_mapping

    animation = make_forward_pass_with_dropout_animation(network, mapping)

    assert animation is not None


@pytest.mark.parametrize(
    "flags",
    [
        {},
        {"last_layer_stable": True},
        {"first_layer_stable": True},
        {"do_forward_pass": False},
    ],
)
def test_full_dropout_animation_with_seed(flags):
    network = NeuralNetwork([FeedForwardLayer(3), FeedForwardLayer(2)])

    animation = make_neural_network_dropout_animation(
        network, dropout_rate=0.5, seed=0, **flags
    )

    assert animation is not None
