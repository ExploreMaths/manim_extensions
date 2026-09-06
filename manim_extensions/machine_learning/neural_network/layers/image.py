# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Image layer visualization for neural networks."""

from manim import *
import numpy as np
from PIL import Image

from ...utils.mobjects.image import GrayscaleImageMobject
from .parent_layers import NeuralNetworkLayer


class ImageLayer(NeuralNetworkLayer):
    """Single Image Layer for Neural Network

    Parameters
    ----------
    numpy_image : np.ndarray
        Image data as a numpy array; 2D is treated as grayscale and 3D as RGB.
    height : float, optional
        Height of the rendered image, by default 1.5.
    show_image_on_create : bool, optional
        Whether the image is shown when the layer is created, by default True.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.NeuralNetworkLayer`.

    Examples
    --------
    .. manim:: ImageLayerDocExample

       from manim import *
       import numpy as np
       from manim_extensions.machine_learning.neural_network import (
           Convolutional2DLayer,
           FeedForwardLayer,
           ImageLayer,
           NeuralNetwork,
       )

       # Widescreen layout used by the upstream ManimML examples
       config.pixel_height = 700
       config.pixel_width = 1900
       config.frame_height = 7.0
       config.frame_width = 7.0

       class ImageLayerDocExample(ThreeDScene):
           def construct(self):
               # Synthesize a digit-like image (the upstream example loads an
               # MNIST digit from assets)
               yy, xx = np.mgrid[0:28, 0:28]
               numpy_image = np.where((yy - 14) ** 2 + (xx - 14) ** 2 < 81, 200, 0).astype(np.uint8)
               nn = NeuralNetwork(
                   [
                       ImageLayer(numpy_image, height=1.5),
                       Convolutional2DLayer(1, 7, filter_spacing=0.32),
                       Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
                       Convolutional2DLayer(5, 3, 3, filter_spacing=0.18),
                       FeedForwardLayer(3),
                       FeedForwardLayer(3),
                   ],
                   layer_spacing=0.25,
               )
               nn.move_to(ORIGIN)
               self.add(nn)
               # Animate the forward pass
               forward_pass = nn.make_forward_pass_animation()
               self.play(ChangeSpeed(forward_pass, speedinfo={}), run_time=10)
               self.wait(1)
    """

    def __init__(
        self, 
        numpy_image, 
        height=1.5, 
        show_image_on_create=True, 
        **kwargs
    ):
        super().__init__(**kwargs)
        self.image_height = height
        self.numpy_image = numpy_image
        self.show_image_on_create = show_image_on_create

    def construct_layer(self, input_layer, output_layer, **kwargs):
        """Construct layer method

        Parameters
        ----------
        input_layer :
            Input layer
        output_layer :
            Output layer
        """
        if len(np.shape(self.numpy_image)) == 2:
            # Assumed Grayscale
            self.num_channels = 1
            self.image_mobject = GrayscaleImageMobject(
                self.numpy_image, 
                height=self.image_height
            )
        elif len(np.shape(self.numpy_image)) == 3:
            # Assumed RGB
            self.num_channels = 3
            self.image_mobject = ImageMobject(self.numpy_image).scale_to_fit_height(
                self.image_height
            )
        self.add(self.image_mobject)
        super().construct_layer(input_layer, output_layer, **kwargs)

    @classmethod
    def from_path(cls, image_path, grayscale=True, **kwargs):
        """Creates a query using the paths"""
        # Load images from path
        image = Image.open(image_path)
        numpy_image = np.asarray(image)
        # Make the layer
        image_layer = cls(numpy_image, **kwargs)

        return image_layer

    @override_animation(Create)
    def _create_override(self, **kwargs):
        debug_mode = False
        if debug_mode:
            return FadeIn(SurroundingRectangle(self.image_mobject))
        if self.show_image_on_create:
            return FadeIn(self.image_mobject)
        else:
            # Nothing to create visually; manim >= 0.21 raises on empty
            # groups, so return a zero-duration Wait instead.
            return Wait(run_time=0)

    def make_forward_pass_animation(self, layer_args={}, **kwargs):
        return AnimationGroup()

    def get_right(self):
        """Override get right"""
        return self.image_mobject.get_right()

    def scale(self, scale_factor, **kwargs):
        """Scales the image mobject"""
        self.image_mobject.scale(scale_factor)

    @property
    def width(self):
        return self.image_mobject.width

    @property
    def height(self):
        return self.image_mobject.height