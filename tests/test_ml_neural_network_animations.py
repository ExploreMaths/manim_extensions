# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the neural network layer transformations and dropout marker."""

import pytest
from manim import Circle

from manim_extensions.machine_learning.neural_network.animations.dropout import XMark
from manim_extensions.machine_learning.neural_network.animations.neural_network_transformations import (
    InsertLayer,
    RemoveLayer,
)
from manim_extensions.machine_learning.neural_network.layers.feed_forward import (
    FeedForwardLayer,
)
from manim_extensions.machine_learning.neural_network.layers.parent_layers import (
    BlankConnective,
)
from manim_extensions.machine_learning.neural_network.layers.util import (
    get_connective_layer,
)
from manim_extensions.machine_learning.neural_network.neural_network import (
    NeuralNetwork,
)


def build_network():
    return NeuralNetwork([FeedForwardLayer(3), FeedForwardLayer(2)])


def build_constructed_layer(size: int):
    layer = FeedForwardLayer(size)
    layer.construct_layer(None, None)
    return layer


def test_network_infers_connective_layer():
    network = build_network()

    assert len(network.all_layers) == 3
    assert len(network.input_layers) == 2


def test_unregistered_pair_falls_back_to_blank_connective():
    connection = get_connective_layer(Circle(), Circle())

    assert isinstance(connection, BlankConnective)
    assert len(connection.submobjects) == 0


def test_blank_connective_forward_pass_is_empty():
    connection = get_connective_layer(Circle(), Circle())

    animation = connection.make_forward_pass_animation(run_time=0.2)

    assert len(animation.animations) == 0


@pytest.mark.parametrize("index", [0, 2])
def test_insert_layer_builds_animations(index):
    network = build_network()
    animation = InsertLayer(build_constructed_layer(4), index, network)

    assert len(animation.animations) >= 3


def test_remove_layer_builds_animations():
    network = build_network()
    animation = RemoveLayer(network.input_layers[0], network)

    assert len(animation.animations) >= 3


def test_x_mark_shape():
    mark = XMark()
    wide = XMark(stroke_width=2.0)

    assert len(mark.submobjects) == 2
    assert len(wide.submobjects) == 2
