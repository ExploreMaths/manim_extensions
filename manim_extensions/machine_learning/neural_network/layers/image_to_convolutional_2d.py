# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: route three-channel images to the RGB animation and implement it

"""Image to convolutional 2D layer connection visualization."""

from __future__ import annotations

from manim import (
    AnimationGroup,
    ApplyFunction,
    ApplyMethod,
    Create,
    FadeIn,
    Group,
    Mobject,
    Succession,
    Wait,
    override_animation,
)
from .convolutional_2d import Convolutional2DLayer
from .image import ImageLayer
from .parent_layers import NeuralNetworkLayer, ThreeDLayer, VGroupNeuralNetworkLayer

from ... import config
from ...utils.mobjects.image import GrayscaleImageMobject


class ImageToConvolutional2DLayer(VGroupNeuralNetworkLayer, ThreeDLayer):
    """Connective layer between an image layer and a convolutional 2D layer.

    Parameters
    ----------
    input_layer
        The input image layer.
    output_layer
        The output convolutional layer.
    **kwargs
        Forwarded to the parent layer classes.

    Examples
    --------
    .. manim:: RGBImageToConvolutionExample

       import numpy as np
       from manim import *
       from manim_extensions.machine_learning.neural_network import (
           Convolutional2DLayer,
           ImageLayer,
           NeuralNetwork,
       )

       class RGBImageToConvolutionExample(ThreeDScene):
           def construct(self):
               # Synthesize a small RGB image with one channel per colour
               yy, xx = np.mgrid[0:16, 0:16]
               rgb_image = np.stack(
                   [
                       (yy * 12).astype(np.uint8),
                       (xx * 12).astype(np.uint8),
                       ((yy + xx) * 8).astype(np.uint8),
                   ],
                   axis=-1,
               )
               nn = NeuralNetwork(
                   [
                       ImageLayer(rgb_image, height=2.4),
                       Convolutional2DLayer(3, 5, 3, filter_spacing=0.55),
                   ],
                   layer_spacing=0.25,
               )
               nn.move_to(ORIGIN)
               self.add(nn)
               self.play(nn.make_forward_pass_animation(), run_time=4)
    """

    input_class = ImageLayer
    output_class = Convolutional2DLayer

    def __init__(
        self, input_layer: ImageLayer, output_layer: Convolutional2DLayer, **kwargs
    ):
        """Initialize the image-to-conv2d connective layer storing references to both layers."""
        super().__init__(input_layer, output_layer, **kwargs)
        self.input_layer = input_layer
        self.output_layer = output_layer

    def construct_layer(
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs,
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

        Returns
        -------
            The computed result.
        """
        return super().construct_layer(input_layer, output_layer, **kwargs)

    def make_forward_pass_animation(
        self, run_time: float = 5, layer_args: dict = {}, **kwargs
    ) -> Succession:
        """Maps image to convolutional layer.

        Parameters
        ----------
        run_time
            Run time of the forward pass animation.
        layer_args
            Additional arguments passed to the connected layers when making
            their forward pass animations.
        **kwargs
            Forwarded to the parent layer classes.

        Returns
        -------
            The computed result.

        Raises
        ------
        Exception
            Raised when the number of image channels is not 1 or 3.
        """
        # Transform the image from the input layer to the
        num_image_channels = self.input_layer.num_channels
        if num_image_channels == 1:
            return self.grayscale_image_forward_pass_animation()
        elif num_image_channels == 3:
            return self.rbg_image_forward_pass_animation()
        else:
            raise Exception(
                f"Unrecognized number of image channels: {num_image_channels}"
            )

    def rbg_image_forward_pass_animation(self) -> Succession:
        """Handles forward pass animation for 3 channel image.

        Each colour channel is turned into a grayscale image at the position
        of the input image and is then mapped onto one feature map of the
        convolutional layer.

        Returns
        -------
            A :class:`~manim.animation.composition.Succession` instance representing the result.

        Raises
        ------
        ValueError
            If the convolutional layer has fewer feature maps than the image
            has channels.
        """
        numpy_image = self.input_layer.numpy_image
        target_feature_maps = self.output_layer.feature_maps
        if len(target_feature_maps) < self.input_layer.num_channels:
            raise ValueError(
                "The convolutional layer needs at least as many feature maps "
                "as the image has channels."
            )
        channel_images = []
        animations = []
        for channel_index in range(self.input_layer.num_channels):
            channel_image = GrayscaleImageMobject(
                numpy_image[:, :, channel_index],
                height=self.input_layer.image_height,
            )
            channel_image.move_to(self.input_layer.image_mobject)
            channel_images.append(channel_image)
            animations.append(
                self._image_to_feature_map_animation(
                    channel_image, target_feature_maps[channel_index]
                )
            )
        return Succession(
            FadeIn(Group(*channel_images)),
            AnimationGroup(*animations),
        )

    def _image_to_feature_map_animation(
        self, image_mobject: Mobject, target_feature_map: Mobject
    ) -> Succession:
        """Rotate, scale and move an image mobject onto a feature map.

        Parameters
        ----------
        image_mobject
            Image mobject that is transformed.
        target_feature_map
            Feature map the image is mapped onto.

        Returns
        -------
            A :class:`~manim.animation.composition.Succession` instance representing the result.
        """
        # Make rotation of image
        rotation = ApplyMethod(
            image_mobject.rotate,
            config.three_d_config.rotation_angle,
            config.three_d_config.rotation_axis,
            # A trailing dict is forwarded to the method as keyword
            # arguments (see ApplyMethod.create_target).
            {"about_point": image_mobject.get_center()},
            run_time=0.5,
        )
        # Set opacity
        set_opacity = ApplyMethod(image_mobject.set_opacity, 0.2, run_time=0.5)

        # Scale the max of width or height to the
        # width of the feature_map
        def scale_image_func(image_mobject: Mobject) -> Mobject:
            """Scale the image to match the target feature map size, preserving aspect ratio.

            Returns
            -------
                The computed result."""
            max_width_height = max(image_mobject.width, image_mobject.height)
            scale_factor = target_feature_map.untransformed_width / max_width_height
            image_mobject.scale(scale_factor)

            return image_mobject

        scale_image = ApplyFunction(scale_image_func, image_mobject)
        # Move the image
        move_image = ApplyMethod(image_mobject.move_to, target_feature_map)
        # Compose the animations
        return Succession(
            rotation,
            scale_image,
            set_opacity,
            move_image,
        )

    def grayscale_image_forward_pass_animation(self) -> Succession:
        """Handles forward pass animation for 1 channel image.

        Returns
        -------
            A :class:`~manim.animation.composition.Succession` instance representing the result.
        """
        return self._image_to_feature_map_animation(
            self.input_layer.image_mobject, self.output_layer.feature_maps[0]
        )

    def scale(self, scale_factor: float, **kwargs):
        """Scale the layer by forwarding to the parent class.

        Parameters
        ----------
        scale_factor
            Factor by which the layer is scaled.
        **kwargs
            Forwarded to :meth:`~manim.mobject.mobject.Mobject.scale`.
        """
        super().scale(scale_factor, **kwargs)

    @override_animation(Create)
    def _create_override(self, **kwargs):
        # Nothing to create visually; manim >= 0.21 raises on empty groups,
        # so return a zero-duration Wait instead.
        return Wait(run_time=0)
