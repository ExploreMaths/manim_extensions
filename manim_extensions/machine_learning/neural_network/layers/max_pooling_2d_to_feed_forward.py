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
    """Feed Forward to Embedding Layer"""

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