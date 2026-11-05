# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
#
# SPDX-License-Identifier: MIT
# patched: implement make_triplet_forward_pass
"""Variational Autoencoder Manim Visualizations.

In this module I define Manim visualizations for Variational Autoencoders
and Traditional Autoencoders.
"""
from manim import AnimationGroup, BLUE, Create, Group, ImageMobject, ManimColor, override_animation
import numpy as np
from ..layers import FeedForwardLayer, EmbeddingLayer, ImageLayer, TripletLayer
from ..neural_network import NeuralNetwork
from ...utils.mobjects.image import GrayscaleImageMobject
from manim.typing import PixelArray
class VariationalAutoencoder(Group):
    """Variational Autoencoder Manim Visualization.

    Parameters
    ----------
    encoder_nodes_per_layer
        Number of nodes in each encoder layer.
    decoder_nodes_per_layer
        Number of nodes in each decoder layer.
    point_color
        Color of the points in the embedding layer.
    dot_radius
        Radius of the points in the embedding layer.
    ellipse_stroke_width
        Stroke width of the embedding ellipse.
    layer_spacing
        Spacing between the neural network layers.

    Examples
    --------
    .. manim:: VariationalAutoencoderDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.architectures.variational_autoencoder import (
           VariationalAutoencoder,
       )

       class VariationalAutoencoderDocExample(Scene):
           def construct(self):
               vae = VariationalAutoencoder()
               vae.move_to(ORIGIN)
               self.add(vae.scale(2))
    """

    def __init__(
        self,
        encoder_nodes_per_layer: list = [5, 3],
        decoder_nodes_per_layer: list = [3, 5],
        point_color: ManimColor = BLUE,
        dot_radius: float = 0.05,
        ellipse_stroke_width: float = 1.0,
        layer_spacing: float = 0.5,
    ):
        """Initialize the VAE visualization with encoder, embedding, and decoder layers."""
        super().__init__()
        self.encoder_nodes_per_layer = encoder_nodes_per_layer
        self.decoder_nodes_per_layer = decoder_nodes_per_layer
        self.point_color = point_color
        self.dot_radius = dot_radius
        self.layer_spacing = layer_spacing
        self.ellipse_stroke_width = ellipse_stroke_width
        # Make the VMobjects
        self.neural_network, self.embedding_layer = self._construct_neural_network()
        # The network is a Group (not a VMobject), and VAE is a VGroup whose
        # add() rejects non-VMobjects; append directly so the VAE renders its
        # network as subcontent.
        self.submobjects.extend([self.neural_network])

    def _construct_neural_network(self):
        """Makes the VAE encoder, embedding layer, and decoder."""
        embedding_layer = EmbeddingLayer()

        neural_network = NeuralNetwork(
            [
                FeedForwardLayer(5),
                FeedForwardLayer(3),
                embedding_layer,
                FeedForwardLayer(3),
                FeedForwardLayer(5),
            ]
        )

        return neural_network, embedding_layer

    @override_animation(Create)
    def _create_vae(self):
        return Create(self.neural_network)

    def make_triplet_forward_pass(self, triplet: tuple[PixelArray, PixelArray, PixelArray], run_time: float = 1.5) -> AnimationGroup:
        """Animate a triplet forward pass through the network.

        The three images of the triplet (anchor, positive, negative) are
        shown next to the encoder and then propagated through the network.

        Parameters
        ----------
        triplet
            The triplet of inputs passed through the network.
        run_time
            Run time of the forward pass animation.

        Returns
        -------
            A AnimationGroup instance representing the result.

        Raises
        ------
        ValueError
            Raised when the triplet does not contain exactly three images
            or an image does not have two or three dimensions.
        """
        if len(triplet) != 3:
            raise ValueError("A triplet must contain exactly three images.")
        images = []
        for pixels in triplet:
            pixels = np.asarray(pixels)
            if pixels.ndim == 2:
                images.append(GrayscaleImageMobject(pixels))
            elif pixels.ndim == 3:
                images.append(ImageMobject(pixels, image_mode="RGB"))
            else:
                raise ValueError(
                    "Triplet images must be 2D grayscale or 3D RGB arrays."
                )
        anchor, positive, negative = images
        triplet_layer = TripletLayer(anchor, positive, negative)
        # Make a wrapper NN with the triplet input. The encoder and decoder
        # layers are rebuilt so the triplet animation does not re-parent the
        # existing network.
        wrapper_layers = [triplet_layer]
        wrapper_layers.extend(
            FeedForwardLayer(node_count)
            for node_count in self.encoder_nodes_per_layer
        )
        wrapper_layers.append(EmbeddingLayer())
        wrapper_layers.extend(
            FeedForwardLayer(node_count)
            for node_count in self.decoder_nodes_per_layer
        )
        wrapper_neural_network = NeuralNetwork(wrapper_layers)
        # Make animation
        animation_group = AnimationGroup(
            Create(wrapper_neural_network),
            wrapper_neural_network.make_forward_pass_animation(run_time=run_time),
            lag_ratio=1.0,
        )

        return animation_group

    def make_image_forward_pass(self, input_image: PixelArray, output_image: PixelArray, run_time: float = 1.5) -> AnimationGroup:
        """Override forward pass animation specific to a VAE.

        Parameters
        ----------
        input_image
            The input image fed into the encoder.
        output_image
            The output image produced by the decoder.
        run_time
            Run time of the forward pass animation.

        Returns
        -------
            A AnimationGroup instance representing the result.
        """
        # Make a wrapper NN with images
        wrapper_neural_network = NeuralNetwork(
            [ImageLayer(input_image), self.neural_network, ImageLayer(output_image)]
        )
        # Make animation
        animation_group = AnimationGroup(
            Create(wrapper_neural_network),
            wrapper_neural_network.make_forward_pass_animation(),
            lag_ratio=1.0,
        )

        return animation_group
