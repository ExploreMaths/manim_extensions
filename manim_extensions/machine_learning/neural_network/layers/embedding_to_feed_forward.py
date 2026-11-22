# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Embedding to feed-forward layer connection visualization."""

from __future__ import annotations
from typing import Any, cast

from manim import (
    Animation,
    AnimationGroup,
    Create,
    Dot,
    FadeOut,
    ManimColor,
    RED,
    Succession,
    Wait,
    override_animation,
)
from .feed_forward import FeedForwardLayer
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer
from .embedding import EmbeddingLayer


class EmbeddingToFeedForward(ConnectiveLayer):
    """Connective layer between an embedding layer and a feed-forward layer.

    Parameters
    ----------
    input_layer
        The input embedding layer.
    output_layer
        The output feed-forward layer.
    animation_dot_color
        Color of the dots in the forward pass animation.
    dot_radius
        Radius of the dots in the forward pass animation.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.ConnectiveLayer`.

    Examples
    --------
    .. manim:: EmbeddingToFeedForwardScene
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.embedding import EmbeddingLayer
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.embedding_to_feed_forward import EmbeddingToFeedForward
       first = EmbeddingLayer()
       second = FeedForwardLayer(6)
       first.shift(LEFT * 4)
       second.shift(RIGHT * 4)
       first.construct_layer(None, None)
       second.construct_layer(None, None)
       connection = EmbeddingToFeedForward(first, second)

       class EmbeddingToFeedForwardScene(Scene):
           def construct(self):
               content = Group(first, second, connection)
               content.scale_to_fit_height(5.5).move_to(ORIGIN)
               self.add(content)
    """

    input_class = EmbeddingLayer
    output_class = FeedForwardLayer

    def __init__(
        self,
        input_layer: EmbeddingLayer,
        output_layer: FeedForwardLayer,
        animation_dot_color: ManimColor = RED,
        dot_radius: float = 0.03,
        **kwargs: Any,
    ) -> None:
        super().__init__(cast(Any, input_layer), cast(Any, output_layer), **kwargs)
        self.feed_forward_layer = output_layer
        self.embedding_layer = input_layer
        self.animation_dot_color = animation_dot_color
        self.dot_radius = dot_radius

    def construct_layer(
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs: Any,
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
        self, layer_args: dict[Any, Any] = {}, run_time: float = 1.5, **kwargs: Any
    ) -> Succession:
        """Makes dots diverge from the given location and move the decoder.

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
            A :class:`~manim.animation.composition.Succession` instance representing the result.
        """
        # Find point to converge on by sampling from gaussian distribution
        location = self.embedding_layer.sample_point_location_from_distribution()
        # Move to location
        animations: list[Any] = []
        # Move the dots to the centers of each of the nodes in the FeedForwardLayer
        dots: list[Dot] = []
        for node in self.feed_forward_layer.node_group:
            new_dot = Dot(
                location, radius=self.dot_radius, color=self.animation_dot_color
            )
            per_node_succession = Succession(
                Create(new_dot),
                cast(Animation, new_dot.animate.move_to(node.get_center())),
            )
            animations.append(per_node_succession)
            dots.append(new_dot)
        # Follow up with remove animations
        remove_animations: list[Any] = []
        for dot in dots:
            remove_animations.append(FadeOut(dot))
        remove_animations_group = AnimationGroup(*remove_animations, run_time=0.2)
        animations_group = AnimationGroup(*animations)
        animation_group = Succession(
            animations_group, remove_animations_group, lag_ratio=1.0
        )

        return animation_group

    @override_animation(Create)
    def _create_override(self, **kwargs: Any) -> Animation:
        """Return a zero-duration wait for an invisible layer.

        Parameters
        ----------
        **kwargs
            Ignored extra animation options.

        Returns
        -------
            An animation that does nothing.
        """
        # Nothing to create visually; manim >= 0.21 raises on empty groups,
        # so return a zero-duration Wait instead.
        return Wait(run_time=0)
