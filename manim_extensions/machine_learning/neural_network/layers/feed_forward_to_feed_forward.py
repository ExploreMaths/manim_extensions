# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: implement modify_edge_colors

"""Feed-forward to feed-forward layer connection visualization."""

from __future__ import annotations
from collections.abc import Sequence
from typing import Any, cast

import numpy as np

from manim import (
    Animation,
    AnimationGroup,
    Camera,
    Create,
    Dot,
    FadeOut,
    Line,
    ManimColor,
    MoveAlongPath,
    ShowPassingFlash,
    VGroup,
    override_animation,
    sigmoid,
)

from .feed_forward import FeedForwardLayer
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer
from ... import config
from ....utils.deps import require
from manim.typing import VectorND


class FeedForwardToFeedForward(ConnectiveLayer):
    """Layer for connecting FeedForward layer to :class:`~manim_extensions.machine_learning.neural_network.layers.feed_forward.FeedForwardLayer`.

    Parameters
    ----------
    input_layer
        The input feed-forward layer.
    output_layer
        The output feed-forward layer.
    passing_flash
        Whether to flash the edges during the forward pass animation.
    dot_radius
        Radius of the dots in the forward pass animation.
    animation_dot_color
        Color of the dots in the forward pass animation.
    edge_color
        Color of the edges between the layers.
    edge_width
        Stroke width of the edges.
    camera
        Unused camera reference reserved for future use.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.ConnectiveLayer`.

    Examples
    --------
    .. manim:: FeedForwardToFeedForwardScene
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.feed_forward_to_feed_forward import FeedForwardToFeedForward
       first = FeedForwardLayer(5)
       second = FeedForwardLayer(4)
       first.shift(LEFT * 4)
       second.shift(RIGHT * 4)
       first.construct_layer(None, None)
       second.construct_layer(None, None)
       connection = FeedForwardToFeedForward(first, second)

       class FeedForwardToFeedForwardScene(Scene):
           def construct(self):
               content = Group(first, second, connection)
               content.scale_to_fit_height(5.5).move_to(ORIGIN)
               self.add(content)
    """

    input_class = FeedForwardLayer
    output_class = FeedForwardLayer

    def __init__(
        self,
        input_layer: FeedForwardLayer,
        output_layer: FeedForwardLayer,
        passing_flash: bool = True,
        dot_radius: float = 0.05,
        animation_dot_color: ManimColor = cast(Any, config).color_scheme.active_color,
        edge_color: ManimColor = cast(Any, config).color_scheme.secondary_color,
        edge_width: float = 1.5,
        camera: Camera | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(cast(Any, input_layer), cast(Any, output_layer), **kwargs)
        self.passing_flash = passing_flash
        self.edge_color = edge_color
        self.dot_radius = dot_radius
        self.animation_dot_color = animation_dot_color
        self.edge_width = edge_width

    def construct_layer(
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs: Any,
    ) -> Any:
        """Build the fully-connected edges between input and output layers.

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
                The resulting value.
        """
        self.edges = self.construct_edges()
        self.add(self.edges)
        super().construct_layer(input_layer, output_layer, **kwargs)

    def construct_edges(self) -> VGroup:
        """Create all connecting lines between input and output layer nodes.

        Returns
        -------
            A list of the results."""
        # Go through each node in the two layers and make a connecting line
        input_layer = cast(FeedForwardLayer, self.input_layer)
        output_layer = cast(FeedForwardLayer, self.output_layer)
        edge_lines: list[Any] = []
        for node_i in input_layer.node_group:
            for node_j in output_layer.node_group:
                line = Line(
                    node_i.get_center(),
                    node_j.get_center(),
                    color=self.edge_color,
                    stroke_width=self.edge_width,
                )
                edge_lines.append(line)

        return VGroup(*edge_lines)

    @override_animation(FadeOut)
    def _fadeout_animation(self) -> AnimationGroup:
        """Fade out every connection edge.

        Returns
        -------
            The grouped fade-out animation for all edges.
        """
        animations: list[Any] = []

        for edge in self.edges:
            animations.append(FadeOut(edge))

        animation_group = AnimationGroup(*animations)

        return animation_group

    def make_forward_pass_animation(
        self,
        layer_args: dict[Any, Any] = {},
        run_time: float = 1,
        feed_forward_dropout: float = 0.0,
        **kwargs: Any,
    ) -> AnimationGroup:
        """Animation for passing information from one :class:`~manim_extensions.machine_learning.neural_network.layers.feed_forward.FeedForwardLayer` to the next.

        Parameters
        ----------
        layer_args
            May contain the key ``edge_indices_to_dropout`` with the indices
            of the edges that are dropped out.
        run_time
            Run time of the dot animations.
        feed_forward_dropout
            Unused dropout rate reserved for future use.
        **kwargs
            Forwarded to the parent layer classes.

        Returns
        -------
            A list of the results.
        """
        path_animations: list[Any] = []
        dots: list[Dot] = []
        for edge_index, edge in enumerate(self.edges):
            if (
                not "edge_indices_to_dropout" in layer_args
                or not edge_index in layer_args["edge_indices_to_dropout"]
            ):
                dot = Dot(
                    color=self.animation_dot_color,
                    fill_opacity=1.0,
                    radius=self.dot_radius,
                )
                # Add to dots group
                dots.append(dot)
                # Make the animation
                anim: Animation
                if self.passing_flash:
                    copy_edge = edge.copy()
                    anim = ShowPassingFlash(
                        copy_edge.set_color(self.animation_dot_color), time_width=0.3
                    )
                else:
                    anim = MoveAlongPath(
                        dot, edge, run_time=run_time, rate_func=sigmoid
                    )
                path_animations.append(anim)

        if not self.passing_flash:
            dots_group = VGroup(*dots)
            self.add(dots_group)

        return AnimationGroup(*path_animations)

    def modify_edge_colors(
        self,
        colors: list[ManimColor] | None = None,
        magnitudes: VectorND | None = None,
        color_scheme: str = "inferno",
    ) -> Any:
        """Changes the colors of edges.

        Either explicit per-edge colors or magnitudes mapped through a
        matplotlib colormap must be provided.

        Parameters
        ----------
        colors
            Colors to apply to the edges, one per edge.
        magnitudes
            Magnitudes used to determine the edge colors. Values are mapped
            to colors through ``color_scheme``.
        color_scheme
            Name of the color scheme used when mapping magnitudes to colors.


        Returns
        -------
            The resulting value.

        Raises
        ------
        ValueError
            If neither ``colors`` nor ``magnitudes`` is provided.

        """
        if colors is not None:
            assert len(colors) == len(self.edges)
            for edge, color in zip(self.edges, colors):
                edge.set_color(color)
        elif magnitudes is not None:
            magnitudes = np.asarray(magnitudes, dtype=float).flatten()
            assert len(magnitudes) == len(self.edges)
            matplotlib = require("ml", "matplotlib")
            colormap = matplotlib.colormaps[color_scheme]
            normalize = matplotlib.colors.Normalize(
                vmin=float(magnitudes.min()), vmax=float(magnitudes.max())
            )
            for edge, magnitude in zip(self.edges, magnitudes):
                edge.set_color(
                    ManimColor(matplotlib.colors.to_hex(colormap(normalize(magnitude))))
                )
        else:
            raise ValueError("Provide either colors or magnitudes.")

    def modify_edge_stroke_widths(self, widths: Sequence[float]) -> AnimationGroup:
        """Changes the widths of the edges.

        Parameters
        ----------
        widths
            New stroke widths for the edges, one per edge.

        Returns
        -------
            A :class:`~manim.animation.composition.AnimationGroup` instance representing the result.
        """
        assert len(widths) > 0
        # Note: 1d-arrays are assumed to be in row major order
        widths_array = cast(Any, np.array(widths)).flatten()
        # Check thickness size
        assert np.shape(widths_array)[0] == len(self.edges)
        # Make animation
        animations: list[Any] = []

        for index, edge in enumerate(self.edges):
            width = widths_array[index]
            change_width = cast(Animation, edge.animate.set_stroke_width(width))
            animations.append(change_width)

        animation_group = AnimationGroup(*animations)

        return animation_group

    @override_animation(Create)
    def _create_override(self, **kwargs: Any) -> Animation:
        """Create every connection edge.

        Parameters
        ----------
        **kwargs
            Ignored extra animation options.

        Returns
        -------
            The grouped edge creation animation.
        """
        animations = []

        for edge in self.edges:
            animations.append(Create(edge))

        animation_group = AnimationGroup(*animations, lag_ratio=0.0)
        return animation_group
