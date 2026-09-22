# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Triplet layer visualization for neural networks."""

from manim import (
    AnimationGroup,
    Create,
    DOWN,
    FadeIn,
    GREEN,
    Group,
    ImageMobject,
    RED,
    VGroup,
    WHITE,
    override_animation,
)
from . import NeuralNetworkLayer
from ...utils.mobjects.image import GrayscaleImageMobject, LabeledColorImage


class TripletLayer(NeuralNetworkLayer):
    """Shows triplet images

    Parameters
    ----------
    anchor : Mobject
        Mobject shown as the anchor example.
    positive : Mobject
        Mobject shown as the positive example.
    negative : Mobject
        Mobject shown as the negative example.
    stroke_width : float, optional
        Stroke width of the surrounding rectangles, by default 5.
    font_size : float, optional
        Font size of the labels, by default 22.
    buff : float, optional
        Buffer between the images, by default 0.2.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.NeuralNetworkLayer`.
    """

    def __init__(
        self,
        anchor: VGroup,
        positive: VGroup,
        negative: VGroup,
        stroke_width: float = 5,
        font_size: float = 22,
        buff: float = 0.2,
        **kwargs
    ):
        """Initialize the triplet layer with anchor, positive, and negative labeled images."""
        super().__init__(**kwargs)
        self.anchor = anchor
        self.positive = positive
        self.negative = negative
        self.buff = buff

        self.stroke_width = stroke_width
        self.font_size = font_size

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs
    ):
        """Build the triplet assets and add them to the layer.

        Parameters
        ----------
        input_layer : NeuralNetworkLayer
            The layer preceding this layer in the network.
        output_layer : NeuralNetworkLayer
            The layer following this layer in the network.
        **kwargs
            Forwarded to the parent layer classes.
        """
        # Make the assets
        self.assets = self.make_assets()
        self.add(self.assets)
        super().construct_layer(input_layer, output_layer, **kwargs)

    @classmethod
    def from_paths(
        cls,
        anchor_path: str,
        positive_path: str,
        negative_path: str,
        grayscale: bool = True,
        font_size: float = 22,
        buff: float = 0.2,
    ):
        """Creates a triplet using the anchor paths

        Parameters
        ----------
        anchor_path : str
            Path to the image used as the anchor example.
        positive_path : str
            Path to the image used as the positive example.
        negative_path : str
            Path to the image used as the negative example.
        grayscale : bool, optional
            Whether to load the images as grayscale mobjects, by default True.
        font_size : float, optional
            Font size of the labels, by default 22.
        buff : float, optional
            Buffer between the images, by default 0.2.
        """
        # Load images from path
        if grayscale:
            anchor = GrayscaleImageMobject.from_path(anchor_path)
            positive = GrayscaleImageMobject.from_path(positive_path)
            negative = GrayscaleImageMobject.from_path(negative_path)
        else:
            anchor = ImageMobject(anchor_path)
            positive = ImageMobject(positive_path)
            negative = ImageMobject(negative_path)
        # Make the layer
        triplet_layer = cls(anchor, positive, negative, font_size=font_size, buff=buff)

        return triplet_layer

    def make_assets(self):
        """
        Constructs the assets needed for a triplet layer
        """
        # Handle anchor
        anchor_group = LabeledColorImage(
            self.anchor,
            color=WHITE,
            label="Anchor",
            stroke_width=self.stroke_width,
            font_size=self.font_size,
            buff=self.buff,
        )
        # Handle positive
        positive_group = LabeledColorImage(
            self.positive,
            color=GREEN,
            label="Positive",
            stroke_width=self.stroke_width,
            font_size=self.font_size,
            buff=self.buff,
        )
        # Handle negative
        negative_group = LabeledColorImage(
            self.negative,
            color=RED,
            label="Negative",
            stroke_width=self.stroke_width,
            font_size=self.font_size,
            buff=self.buff,
        )
        # Distribute the groups uniformly vertically
        assets = Group(anchor_group, positive_group, negative_group)
        assets.arrange(DOWN, buff=1.5)

        return assets

    @override_animation(Create)
    def _create_override(self):
        # TODO make Create animation that is custom
        return FadeIn(self.assets)

    def make_forward_pass_animation(self, layer_args: dict = {}, **kwargs):
        """Forward pass for triplet

        Parameters
        ----------
        layer_args : dict, optional
            Additional arguments passed to the layers when making their
            forward pass animations, by default {}.
        **kwargs
            Forwarded to the parent layer classes.
        """
        return AnimationGroup()