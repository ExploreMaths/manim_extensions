# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Max pooling 2D to feed-forward layer connection visualization."""

from manim import *
from .convolutional_2d_to_feed_forward import Convolutional2DToFeedForward
from .feed_forward import FeedForwardLayer
from .max_pooling_2d import MaxPooling2DLayer


class MaxPooling2DToFeedForward(Convolutional2DToFeedForward):
    """Connective layer between a max pooling 2D layer and a feed-forward layer

    Parameters
    ----------
    input_layer : MaxPooling2DLayer
        The input max pooling layer.
    output_layer : FeedForwardLayer
        The output feed-forward layer.
    passing_flash_color : ManimColor, optional
        Color of the flash animation during the forward pass, by default ORANGE.
    **kwargs
        Forwarded to
        :class:`~manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_feed_forward.Convolutional2DToFeedForward`.
    """

    input_class = MaxPooling2DLayer
    output_class = FeedForwardLayer

    def __init__(
        self,
        input_layer: MaxPooling2DLayer,
        output_layer: FeedForwardLayer,
        passing_flash_color=ORANGE,
        **kwargs
    ):
        super().__init__(input_layer, output_layer, **kwargs)

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs
    ):
        return super().construct_layer(input_layer, output_layer, **kwargs)