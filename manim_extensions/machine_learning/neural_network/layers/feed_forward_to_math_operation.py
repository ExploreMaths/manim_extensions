# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Feed-forward to math operation layer connection visualization."""

from __future__ import annotations
from typing import Any, cast

from manim import ManimColor, ORANGE, ShowPassingFlash
from .feed_forward import FeedForwardLayer
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer
from .math_operation_layer import MathOperationLayer
from ...utils.mobjects.connections import NetworkConnection


class FeedForwardToMathOperation(ConnectiveLayer):
    """Connective layer between a feed-forward layer and a math operation layer.

    Parameters
    ----------
    input_layer
        The input feed-forward layer.
    output_layer
        The output math operation layer.
    active_color
        Color used when highlighting the connection.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.ConnectiveLayer`.

    Examples
    --------
    .. manim:: FeedForwardToMathOperationScene
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.math_operation_layer import MathOperationLayer
       from manim_extensions.machine_learning.neural_network.layers.feed_forward_to_math_operation import FeedForwardToMathOperation
       first = FeedForwardLayer(6)
       second = MathOperationLayer("+")
       first.shift(LEFT * 4)
       second.shift(RIGHT * 4)
       first.construct_layer(None, None)
       second.construct_layer(None, None)
       connection = FeedForwardToMathOperation(first, second)

       class FeedForwardToMathOperationScene(Scene):
           def construct(self):
               content = Group(first, second, connection)
               content.scale_to_fit_height(5.5).move_to(ORIGIN)
               self.add(content)
    """

    input_class = FeedForwardLayer
    output_class = MathOperationLayer

    def __init__(
        self,
        input_layer: FeedForwardLayer,
        output_layer: MathOperationLayer,
        active_color: ManimColor = ORANGE,
        **kwargs: Any,
    ) -> None:
        self.active_color = active_color
        super().__init__(cast(Any, input_layer), cast(Any, output_layer), **kwargs)

    def construct_layer(
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs: Any,
    ) -> None:
        """Build a straight arrow connection between the feed-forward and math operation layers.

        Parameters
        ----------
        input_layer
            The layer preceding this connective layer in the network.
        output_layer
            The layer following this connective layer in the network.
        **kwargs
            Forwarded to the parent layer classes.
        """
        # Draw an arrow from the output of the feed forward layer to the
        # input of the math operation layer
        self.connection = NetworkConnection(
            self.input_layer, self.output_layer, arc_direction="straight", buffer=0.05
        )
        self.add(self.connection)

        super().construct_layer(input_layer, output_layer, **kwargs)
        return None

    def make_forward_pass_animation(
        self, layer_args: dict[Any, Any] = {}, **kwargs: Any
    ) -> ShowPassingFlash:
        """Makes dots diverge from the given location and move to the feed forward nodes decoder.

        Parameters
        ----------
        layer_args
            Additional arguments passed to the connected layers when making
            their forward pass animations.
        **kwargs
            Forwarded to the parent layer classes.

        Returns
        -------
            A :class:`~manim.animation.indication.ShowPassingFlash` instance representing the result.
        """
        # Make flashing pass animation on arrow
        passing_flash = ShowPassingFlash(
            self.connection.copy().set_color(self.active_color)
        )

        return passing_flash
