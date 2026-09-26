# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Feed-forward to image layer connection visualization."""

from manim import AnimationGroup, Create, Dot, ManimColor, Mobject, RED, Succession, Wait, override_animation
from .feed_forward import FeedForwardLayer
from .image import ImageLayer
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer


class FeedForwardToImage(ConnectiveLayer):
    """Connective layer between a feed-forward layer and an image layer.

    Parameters
    ----------
    input_layer : FeedForwardLayer
        The input feed-forward layer.
    output_layer : ImageLayer
        The output image layer.
    animation_dot_color : ManimColor, optional
        Color of the dots in the forward pass animation, by default RED.
    dot_radius : float, optional
        Radius of the dots in the forward pass animation, by default 0.05.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.ConnectiveLayer`.
    """

    input_class = FeedForwardLayer
    output_class = ImageLayer

    def __init__(
        self,
        input_layer: Mobject,
        output_layer: Mobject,
        animation_dot_color: ManimColor = RED,
        dot_radius: float = 0.05,
        **kwargs
    ):
        """Initialize the feed-forward-to-image connective layer with dot animation settings."""
        super().__init__(input_layer, output_layer, **kwargs)
        self.animation_dot_color = animation_dot_color
        self.dot_radius = dot_radius

        self.feed_forward_layer = input_layer
        self.image_layer = output_layer

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs
    ):
        """Forward to the parent construct_layer method.

        Parameters
        ----------
        input_layer : NeuralNetworkLayer
            The layer preceding this connective layer in the network.
        output_layer : NeuralNetworkLayer
            The layer following this connective layer in the network.
        **kwargs
            Forwarded to the parent layer classes.
        """
        return super().construct_layer(input_layer, output_layer, **kwargs)

    def make_forward_pass_animation(self, layer_args: dict = {}, **kwargs):
        """Makes dots diverge from the given location and move to the feed forward nodes decoder.

        Parameters
        ----------
        layer_args : dict, optional
            Additional arguments passed to the connected layers when making
            their forward pass animations, by default {}.
        **kwargs
            Forwarded to the parent layer classes.
        """
        animations = []
        image_mobject = self.image_layer.image_mobject
        # Move the dots to the centers of each of the nodes in the FeedForwardLayer
        image_location = image_mobject.get_center()
        for node in self.feed_forward_layer.node_group:
            new_dot = Dot(
                node.get_center(),
                radius=self.dot_radius,
                color=self.animation_dot_color,
            )
            per_node_succession = Succession(
                Create(new_dot),
                new_dot.animate.move_to(image_location),
            )
            animations.append(per_node_succession)

        animation_group = AnimationGroup(*animations)
        return animation_group

    @override_animation(Create)
    def _create_override(self):
        # Nothing to create visually; manim >= 0.21 raises on empty groups,
        # so return a zero-duration Wait instead.
        return Wait(run_time=0)