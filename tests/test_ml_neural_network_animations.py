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
    with pytest.warns(UserWarning, match="Unrecognized input/output class pair"):
        connection = get_connective_layer(Circle(), Circle())

    assert isinstance(connection, BlankConnective)
    assert len(connection.submobjects) == 0


def test_blank_connective_forward_pass_is_empty():
    with pytest.warns(UserWarning, match="Unrecognized input/output class pair"):
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


def test_remove_last_layer_has_no_after_connective():
    network = build_network()
    animation = RemoveLayer(network.input_layers[-1], network)

    assert len(animation.animations) >= 2


def test_remove_layer_not_in_network_raises():
    network = build_network()

    with pytest.raises(Exception, match="Layer object not found"):
        RemoveLayer(Circle(), network)


def test_remove_layer_new_connective_closure_runs():
    network = build_network()
    animation = RemoveLayer(network.input_layers[0], network)
    update = animation.make_new_connective_animation()
    update.update_function(network)

    assert update is not None


def test_insert_layer_create_connective_layers(monkeypatch):
    import manim_extensions.machine_learning.neural_network.animations.neural_network_transformations as module

    monkeypatch.setattr(module, "get_connective_layer", lambda before, after: Circle())
    network = build_network()
    animation = InsertLayer(build_constructed_layer(4), 2, network)
    group = animation.make_create_connective_layers_animation(None, None)

    assert group is not None


def test_remove_middle_layer_closure_inserts_connective():
    network = NeuralNetwork(
        [FeedForwardLayer(3), FeedForwardLayer(3), FeedForwardLayer(2)]
    )
    layer = network.input_layers[1]
    animation = RemoveLayer(layer, network)
    update = animation.make_new_connective_animation()
    update.update_function(network)

    assert update is not None


def test_add_connection_with_mobject_instances():
    network = build_network()
    network.add_connection(Circle(), Circle())


def test_insert_and_remove_layer_wrappers():
    network = build_network()
    layer = build_constructed_layer(2)
    insert = network.insert_layer(layer, 2)
    remove = network.remove_layer(network.input_layers[0])
    assert insert is not None
    assert remove is not None


def test_set_z_index_and_invalid_layout_direction():
    network = build_network()
    network.set_z_index(2)

    with pytest.raises(Exception, match="Unrecognized layout direction"):
        NeuralNetwork(
            [FeedForwardLayer(3), FeedForwardLayer(2)],
            layout_direction="diagonal",
        )


def test_feed_forward_connection_without_flash_and_widths():
    network = build_network()
    connection = network.connective_layers[0]
    connection.passing_flash = False
    connection.make_forward_pass_animation(run_time=0.1)
    connection.modify_edge_stroke_widths([0.5] * len(connection.edges))
