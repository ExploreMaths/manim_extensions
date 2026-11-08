# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for neural-network scaling, placement and layer insertion."""

import pytest
from manim import tempconfig

from manim_extensions.machine_learning.neural_network.layers.feed_forward import (
    FeedForwardLayer,
)
from manim_extensions.machine_learning.neural_network.neural_network import (
    NeuralNetwork,
)


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def _network():
    return NeuralNetwork(
        [FeedForwardLayer(4), FeedForwardLayer(3), FeedForwardLayer(2)]
    )


def test_scale_keeps_center_and_title():
    network = _network()
    center = network.get_center()

    network.scale(0.5)

    assert network.get_center() == pytest.approx(center, abs=1e-6)


@pytest.mark.parametrize("direction", ["top_to_bottom", "left_to_right"])
def test_place_layers_with_directions(direction):
    network = _network()

    network._place_layers(layout_direction=direction)

    assert len(network.all_layers) >= 3


def test_insert_layer_with_out_of_range_index_raises():
    network = _network()

    with pytest.raises(AssertionError):
        network.insert_layer(FeedForwardLayer(3), insert_index=5)
