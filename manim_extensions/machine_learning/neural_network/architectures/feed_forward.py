# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Feed-forward neural network architecture visualization."""

from ... import config
from ..neural_network import NeuralNetwork
from ..layers.feed_forward import FeedForwardLayer

from manim import ManimColor


class FeedForwardNeuralNetwork(NeuralNetwork):
    """:class:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork` with just feed forward layers.

    Parameters
    ----------
    layer_node_count
        Number of nodes in each feed forward layer.
    node_radius
        Radius of each node.
    node_color
        Color of each node.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork`.
    """

    def __init__(
        self,
        layer_node_count: list[int],
        node_radius: float = 0.08,
        node_color: ManimColor = config.color_scheme.primary_color,
        **kwargs,
    ):
        # construct layer
        layers = []
        for num_nodes in layer_node_count:
            layer = FeedForwardLayer(
                num_nodes, node_color=node_color, node_radius=node_radius
            )
            layers.append(layer)
        # call super class
        super().__init__(layers, **kwargs)
