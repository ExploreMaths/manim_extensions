# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Max pooling 2D to feed-forward layer connection visualization."""

from __future__ import annotations
from typing import Any, cast

from manim import ManimColor, ORANGE
from .convolutional_2d import Convolutional2DLayer
from .convolutional_2d_to_feed_forward import Convolutional2DToFeedForward
from .feed_forward import FeedForwardLayer
from .max_pooling_2d import MaxPooling2DLayer
from .parent_layers import NeuralNetworkLayer


class MaxPooling2DToFeedForward(Convolutional2DToFeedForward):
    """Connective layer between a max pooling 2D layer and a feed-forward layer.

    Parameters
    ----------
    input_layer
        The input max pooling layer.
    output_layer
        The output feed-forward layer.
    passing_flash_color
        Color of the flash animation during the forward pass.
    **kwargs
        Forwarded to
        :class:`~manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_feed_forward.Convolutional2DToFeedForward`.

    Examples
    --------
    .. manim:: MaxPooling2DToFeedForwardScene
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.convolutional_2d import Convolutional2DLayer
       from manim_extensions.machine_learning.neural_network.layers.max_pooling_2d import MaxPooling2DLayer
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.max_pooling_2d_to_feed_forward import MaxPooling2DToFeedForward
       source = Convolutional2DLayer(4, 8, 3)
       source.construct_layer(None, None)
       first = MaxPooling2DLayer(kernel_size=2)
       second = FeedForwardLayer(6)
       first.shift(LEFT * 4)
       second.shift(RIGHT * 4)
       first.construct_layer(source, None)
       second.construct_layer(None, None)
       connection = MaxPooling2DToFeedForward(first, second)

       class MaxPooling2DToFeedForwardScene(Scene):
           def construct(self):
               content = Group(first, second, connection)
               content.scale_to_fit_height(5.5).move_to(ORIGIN)
               self.add(content)
    """

    input_class = MaxPooling2DLayer
    output_class = FeedForwardLayer

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        input_layer: MaxPooling2DLayer,
        output_layer: FeedForwardLayer,
        passing_flash_color: ManimColor = ORANGE,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        super().__init__(
            cast(Convolutional2DLayer, input_layer), output_layer, **kwargs
        )

    def construct_layer(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        """Forward to the parent construct_layer method.

        Parameters
        ----------
        input_layer
            The layer preceding this connective layer in the network.
        output_layer
            The layer following this connective layer in the network.
        **kwargs
            Forwarded to the parent layer classes.
        """
        super().construct_layer(input_layer, output_layer, **kwargs)
        return None
