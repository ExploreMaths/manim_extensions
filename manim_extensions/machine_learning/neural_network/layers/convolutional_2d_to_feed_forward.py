# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Convolutional 2D to feed-forward layer connection visualization."""

from __future__ import annotations
from typing import Any, cast

from manim import AnimationGroup, Line, ManimColor, ORANGE, ShowPassingFlash
from .max_pooling_2d import MaxPooling2DLayer
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer, ThreeDLayer
from .feed_forward import FeedForwardLayer
from .convolutional_2d import Convolutional2DLayer


class Convolutional2DToFeedForward(ConnectiveLayer, ThreeDLayer):
    """Connective layer between a convolutional 2D layer and a feed-forward layer.

    .. doc-example-covers: make_forward_pass_animation

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

    Examples
    --------
    .. manim:: Convolutional2DToFeedForwardScene
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.convolutional_2d import Convolutional2DLayer
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_feed_forward import Convolutional2DToFeedForward
       first = Convolutional2DLayer(4, 6, 3)
       second = FeedForwardLayer(6)
       first.shift(LEFT * 4)
       second.shift(RIGHT * 4)
       first.construct_layer(None, None)
       second.construct_layer(None, None)
       connection = Convolutional2DToFeedForward(first, second)

       class Convolutional2DToFeedForwardScene(Scene):
           def construct(self):
               content = Group(first, second, connection)
               content.scale_to_fit_height(5.5).move_to(ORIGIN)
               self.add(content)
    """

    input_class: type[Convolutional2DLayer | MaxPooling2DLayer] = Convolutional2DLayer
    output_class: type[FeedForwardLayer] = FeedForwardLayer

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        input_layer: Convolutional2DLayer,
        output_layer: FeedForwardLayer,
        passing_flash_color: ManimColor = ORANGE,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        super().__init__(input_layer, output_layer, **kwargs)
        self.passing_flash_color = passing_flash_color

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

    def make_forward_pass_animation(
        self,
        layer_args: dict[str, object] = {},
        run_time: float = 1.5,
        **kwargs: object,
    ) -> AnimationGroup:
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
            A :class:`~manim.animation.composition.AnimationGroup` instance representing the result.
        """
        animations = []
        # Get input layer final feature map
        input_layer = cast(Convolutional2DLayer, self.input_layer)
        final_feature_map = input_layer.feature_maps[-1]
        # Get output layer nodes
        output_layer = cast(FeedForwardLayer, self.output_layer)
        feed_forward_nodes = output_layer.node_group
        # Go through each corner
        corners = final_feature_map.get_corners_dict().values()
        for corner in corners:
            # Go through each node
            for node in feed_forward_nodes:
                line = Line(corner, node, stroke_width=1.0)
                line.set_z_index(output_layer.node_group.z_index)
                anim = ShowPassingFlash(
                    line.set_color(self.passing_flash_color), time_width=0.2
                )
                animations.append(anim)

        return AnimationGroup(*animations)
