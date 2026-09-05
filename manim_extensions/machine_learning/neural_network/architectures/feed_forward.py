# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Feed-forward neural network architecture visualization."""

from ... import config
from ..neural_network import NeuralNetwork
from ..layers.feed_forward import FeedForwardLayer

class FeedForwardNeuralNetwork(NeuralNetwork):
    """NeuralNetwork with just feed forward layers

    Parameters
    ----------
    layer_node_count : list
        Number of nodes in each feed forward layer.
    node_radius : float, optional
        Radius of each node, by default 0.08.
    node_color : ManimColor, optional
        Color of each node, by default ``config.color_scheme.primary_color``.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork`.
    """

    def __init__(
        self, 
        layer_node_count, 
        node_radius=0.08, 
        node_color=config.color_scheme.primary_color, 
        **kwargs
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