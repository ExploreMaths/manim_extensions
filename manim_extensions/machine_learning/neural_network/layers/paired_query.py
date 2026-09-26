# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Paired query layer visualization for neural networks."""

from manim import (
    AnimationGroup,
    BLUE,
    Create,
    DOWN,
    FadeIn,
    Group,
    ImageMobject,
    RED,
    VGroup,
    override_animation,
)
from .parent_layers import NeuralNetworkLayer
from ...utils.mobjects.image import GrayscaleImageMobject, LabeledColorImage


class PairedQueryLayer(NeuralNetworkLayer):
    """Paired Query Layer

    Parameters
    ----------
    positive : Mobject
        Mobject shown as the positive query example.
    negative : Mobject
        Mobject shown as the negative query example.
    stroke_width : float, optional
        Stroke width of the surrounding rectangles, by default 5.
    font_size : float, optional
        Font size of the labels, by default 18.
    spacing : float, optional
        Spacing between the two images, by default 0.5.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.NeuralNetworkLayer`.

    Examples
    --------
    .. manim:: PairedQueryLayerDocExample

       from manim import *
       import numpy as np
       from manim_extensions.machine_learning.neural_network import (
           FeedForwardLayer,
           NeuralNetwork,
           PairedQueryLayer,
       )
       from manim_extensions.machine_learning.utils.mobjects.image import (
           GrayscaleImageMobject,
       )

       # Widescreen layout used by the upstream ManimML examples
       config.pixel_height = 700
       config.pixel_width = 1900
       config.frame_height = 7.0
       config.frame_width = 7.0

       class PairedQueryLayerDocExample(Scene):
           def construct(self):
               # Synthesize digit-like query images
               yy, xx = np.mgrid[0:28, 0:28]
               positive_array = np.where(
                   (yy - 14) ** 2 + (xx - 14) ** 2 < 81, 200, 0
               ).astype(np.uint8)
               negative_array = np.where(
                   (yy - 20) ** 2 + (xx - 20) ** 2 < 81, 200, 0
               ).astype(np.uint8)
               query_layer = PairedQueryLayer(
                   GrayscaleImageMobject(positive_array, height=0.6),
                   GrayscaleImageMobject(negative_array, height=0.6),
               )
               nn = NeuralNetwork([query_layer, FeedForwardLayer(3)])
               nn.move_to(ORIGIN)
               self.play(Create(nn))
               # Animate the forward pass
               self.play(nn.make_forward_pass_animation())
    """

    def __init__(
        self, positive: VGroup, negative: VGroup, stroke_width: float = 5, font_size: float = 18, spacing: float = 0.5, **kwargs
    ):
        """Initialize the paired query layer with positive/negative examples and labeled borders."""
        super().__init__(**kwargs)
        self.positive = positive
        self.negative = negative
        self.font_size = font_size
        self.spacing = spacing

        self.stroke_width = stroke_width
        # Make the assets
        self.assets = self.make_assets()
        self.add(self.assets)
        self.add(self.title)

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
            The layer preceding this layer in the network.
        output_layer : NeuralNetworkLayer
            The layer following this layer in the network.
        **kwargs
            Forwarded to the parent layer classes.
        """
        return super().construct_layer(input_layer, output_layer, **kwargs)

    @classmethod
    def from_paths(cls, positive_path: str, negative_path: str, grayscale: bool = True, **kwargs):
        """Creates a query using the paths

        Parameters
        ----------
        positive_path : str
            Path to the image used as the positive query example.
        negative_path : str
            Path to the image used as the negative query example.
        grayscale : bool, optional
            Whether to load the images as grayscale mobjects, by default True.
        **kwargs
            Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.paired_query.PairedQueryLayer.PairedQueryLayer`.
        """
        # Load images from path
        if grayscale:
            positive = GrayscaleImageMobject.from_path(positive_path)
            negative = GrayscaleImageMobject.from_path(negative_path)
        else:
            positive = ImageMobject(positive_path)
            negative = ImageMobject(negative_path)
        # Make the layer
        query_layer = cls(positive, negative, **kwargs)

        return query_layer

    def make_assets(self):
        """
        Constructs the assets needed for a query layer.
        """
        # Handle positive
        positive_group = LabeledColorImage(
            self.positive,
            color=BLUE,
            label="Positive",
            font_size=self.font_size,
            stroke_width=self.stroke_width,
        )
        # Handle negative
        negative_group = LabeledColorImage(
            self.negative,
            color=RED,
            label="Negative",
            font_size=self.font_size,
            stroke_width=self.stroke_width,
        )
        # Distribute the groups uniformly vertically
        assets = Group(positive_group, negative_group)
        assets.arrange(DOWN, buff=self.spacing)

        return assets

    @override_animation(Create)
    def _create_override(self):
        # TODO make Create animation that is custom
        return FadeIn(self.assets)

    def make_forward_pass_animation(self, layer_args: dict = {}, **kwargs):
        """Forward pass for query

        Parameters
        ----------
        layer_args : dict, optional
            Additional arguments passed to the layers when making their
            forward pass animations, by default {}.
        **kwargs
            Forwarded to the parent layer classes.
        """
        return AnimationGroup()