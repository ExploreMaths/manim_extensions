# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Feed-forward to vector layer connection visualization."""

from manim import *
from .feed_forward import FeedForwardLayer
from .parent_layers import ConnectiveLayer
from .vector import VectorLayer


class FeedForwardToVector(ConnectiveLayer):
    """Connective layer between a feed-forward layer and a vector layer

    Parameters
    ----------
    input_layer : FeedForwardLayer
        The input feed-forward layer.
    output_layer : VectorLayer
        The output vector layer.
    animation_dot_color : ManimColor, optional
        Color of the dots in the forward pass animation, by default RED.
    dot_radius : float, optional
        Radius of the dots in the forward pass animation, by default 0.05.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.ConnectiveLayer`.
    """

    input_class = FeedForwardLayer
    output_class = VectorLayer

    def __init__(
        self,
        input_layer,
        output_layer,
        animation_dot_color=RED,
        dot_radius=0.05,
        **kwargs
    ):
        super().__init__(input_layer, output_layer, **kwargs)
        self.animation_dot_color = animation_dot_color
        self.dot_radius = dot_radius

        self.feed_forward_layer = input_layer
        self.vector_layer = output_layer

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs
    ):
        return super().construct_layer(input_layer, output_layer, **kwargs)

    def make_forward_pass_animation(self, layer_args={}, **kwargs):
        """Makes dots diverge from the given location and move to the feed forward nodes decoder"""
        animations = []
        # Move the dots to the centers of each of the nodes in the FeedForwardLayer
        destination = self.vector_layer.get_center()
        for node in self.feed_forward_layer.node_group:
            new_dot = Dot(
                node.get_center(),
                radius=self.dot_radius,
                color=self.animation_dot_color,
            )
            per_node_succession = Succession(
                Create(new_dot),
                new_dot.animate.move_to(destination),
            )
            animations.append(per_node_succession)

        animation_group = AnimationGroup(*animations)
        return animation_group

    @override_animation(Create)
    def _create_override(self):
        return AnimationGroup()