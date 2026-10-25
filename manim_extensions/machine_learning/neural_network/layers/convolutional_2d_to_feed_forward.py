# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Convolutional 2D to feed-forward layer connection visualization."""

from typing import Any
from manim import AnimationGroup, Line, ManimColor, ORANGE, ShowPassingFlash
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer, ThreeDLayer
from .feed_forward import FeedForwardLayer
from .convolutional_2d import Convolutional2DLayer


class Convolutional2DToFeedForward(ConnectiveLayer, ThreeDLayer):
    """Connective layer between a convolutional 2D layer and a feed-forward layer.

    Parameters
    ----------
    input_layer
        The input convolutional layer.
    output_layer
        The output feed-forward layer.
    passing_flash_color
        Color of the flash animation during the forward pass.
    **kwargs
        Forwarded to the parent layer classes.
    """

    input_class = Convolutional2DLayer
    output_class = FeedForwardLayer

    def __init__(
        self,
        input_layer: Convolutional2DLayer,
        output_layer: FeedForwardLayer,
        passing_flash_color: ManimColor = ORANGE,
        **kwargs
    ):
        """Initialize the conv2d-to-feed-forward connective layer with flash color setting."""
        super().__init__(input_layer, output_layer, **kwargs)
        self.passing_flash_color = passing_flash_color

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs
    ) -> Any:
        """Forward to the parent construct_layer method.

        Parameters
        ----------
        input_layer
            The layer preceding this connective layer in the network.
        output_layer
            The layer following this connective layer in the network.
        **kwargs
            Forwarded to the parent layer classes.

        Returns
        -------
        Any
            The computed result.
"""
        return super().construct_layer(input_layer, output_layer, **kwargs)

    def make_forward_pass_animation(self, layer_args: dict = {}, run_time: float = 1.5, **kwargs) -> AnimationGroup:
        """Forward pass animation from conv2d to conv2d.

        Parameters
        ----------
        layer_args
            Additional arguments passed to the connected layers when making
            their forward pass animations.
        run_time
            Run time of the forward pass animation.
        **kwargs
            Forwarded to the parent layer classes.

        Returns
        -------
        AnimationGroup
            A AnimationGroup instance representing the result.
"""
        animations = []
        # Get input layer final feature map
        final_feature_map = self.input_layer.feature_maps[-1]
        # Get output layer nodes
        feed_forward_nodes = self.output_layer.node_group
        # Go through each corner
        corners = final_feature_map.get_corners_dict().values()
        for corner in corners:
            # Go through each node
            for node in feed_forward_nodes:
                line = Line(corner, node, stroke_width=1.0)
                line.set_z_index(self.output_layer.node_group.get_z_index())
                anim = ShowPassingFlash(
                    line.set_color(self.passing_flash_color), time_width=0.2
                )
                animations.append(anim)

        return AnimationGroup(*animations)