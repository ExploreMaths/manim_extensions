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
    """NeuralNetwork with just feed forward layers"""

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