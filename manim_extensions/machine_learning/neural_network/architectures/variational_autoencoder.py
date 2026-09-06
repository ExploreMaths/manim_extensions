# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Variational Autoencoder Manim Visualizations

In this module I define Manim visualizations for Variational Autoencoders
and Traditional Autoencoders.

"""
from manim import *
from ..layers import FeedForwardLayer, EmbeddingLayer, ImageLayer
from ..neural_network import NeuralNetwork


class VariationalAutoencoder(VGroup):
    """Variational Autoencoder Manim Visualization

    Parameters
    ----------
    encoder_nodes_per_layer : list, optional
        Number of nodes in each encoder layer, by default [5, 3].
    decoder_nodes_per_layer : list, optional
        Number of nodes in each decoder layer, by default [3, 5].
    point_color : ManimColor, optional
        Color of the points in the embedding layer, by default BLUE.
    dot_radius : float, optional
        Radius of the points in the embedding layer, by default 0.05.
    ellipse_stroke_width : float, optional
        Stroke width of the embedding ellipse, by default 1.0.
    layer_spacing : float, optional
        Spacing between the neural network layers, by default 0.5.

    Examples
    --------
    .. manim:: VariationalAutoencoderDocExample

       from manim import *
       from manim_extensions.machine_learning.neural_network.architectures.variational_autoencoder import (
           VariationalAutoencoder,
       )

       # Widescreen layout used by the upstream ManimML examples
       config.pixel_height = 700
       config.pixel_width = 1900
       config.frame_height = 7.0
       config.frame_width = 7.0

       class VariationalAutoencoderDocExample(Scene):
           def construct(self):
               vae = VariationalAutoencoder()
               vae.move_to(ORIGIN)
               self.play(Create(vae))
    """

    def __init__(
        self,
        encoder_nodes_per_layer=[5, 3],
        decoder_nodes_per_layer=[3, 5],
        point_color=BLUE,
        dot_radius=0.05,
        ellipse_stroke_width=1.0,
        layer_spacing=0.5,
    ):
        super(VGroup, self).__init__()
        self.encoder_nodes_per_layer = encoder_nodes_per_layer
        self.decoder_nodes_per_layer = decoder_nodes_per_layer
        self.point_color = point_color
        self.dot_radius = dot_radius
        self.layer_spacing = layer_spacing
        self.ellipse_stroke_width = ellipse_stroke_width
        # Make the VMobjects
        self.neural_network, self.embedding_layer = self._construct_neural_network()

    def _construct_neural_network(self):
        """Makes the VAE encoder, embedding layer, and decoder"""
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

    def make_triplet_forward_pass(self, triplet):
        pass

    def make_image_forward_pass(self, input_image, output_image, run_time=1.5):
        """Override forward pass animation specific to a VAE"""
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
