# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Image to convolutional 2D layer connection visualization."""

from manim import (
    ApplyFunction,
    ApplyMethod,
    Create,
    Mobject,
    Succession,
    Wait,
    override_animation,
)
from .convolutional_2d import Convolutional2DLayer
from .image import ImageLayer
from .parent_layers import NeuralNetworkLayer, ThreeDLayer, VGroupNeuralNetworkLayer

from ... import config


class ImageToConvolutional2DLayer(VGroupNeuralNetworkLayer, ThreeDLayer):
    """Connective layer between an image layer and a convolutional 2D layer

    Parameters
    ----------
    input_layer : ImageLayer
        The input image layer.
    output_layer : Convolutional2DLayer
        The output convolutional layer.
    **kwargs
        Forwarded to the parent layer classes.
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
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs,
    ):
        """Forward to the parent construct_layer method.

        Parameters
        ----------
        input_layer : NeuralNetworkLayer
            The layer preceding this connective layer in the network.
        output_layer : NeuralNetworkLayer
            The layer following this connective layer in the network.
        **kwargs
            Forwarded to the parent layer classes.
        """
        return super().construct_layer(input_layer, output_layer, **kwargs)

    def make_forward_pass_animation(self, run_time: float = 5, layer_args: dict = {}, **kwargs):
        """Maps image to convolutional layer

        Parameters
        ----------
        run_time : float, optional
            Run time of the forward pass animation, by default 5.
        layer_args : dict, optional
            Additional arguments passed to the connected layers when making
            their forward pass animations, by default {}.
        **kwargs
            Forwarded to the parent layer classes.

        Raises
        ------
        Exception
            Raised when the number of image channels is not 1 or 3.
        """
        # Transform the image from the input layer to the
        num_image_channels = self.input_layer.num_channels
        if num_image_channels == 1 or num_image_channels == 3:  # TODO fix this later
            return self.grayscale_image_forward_pass_animation()
        elif num_image_channels == 3:
            return self.rbg_image_forward_pass_animation()
        else:
            raise Exception(
                f"Unrecognized number of image channels: {num_image_channels}"
            )

    def rbg_image_forward_pass_animation(self):
        """Handles forward pass animation for 3 channel image

        Raises
        ------
        NotImplementedError
            Always raised; RGB image forward pass animations are not yet
            supported.
        """
        image_mobject = self.input_layer.image_mobject
        # TODO get each color channel and turn it into an image
        # TODO create image mobjects for each channel and transform
        # it to the feature maps of the output_layer
        raise NotImplementedError()

    def grayscale_image_forward_pass_animation(self):
        """Handles forward pass animation for 1 channel image."""
        animations = []
        image_mobject = self.input_layer.image_mobject
        target_feature_map = self.output_layer.feature_maps[0]
        # Map image mobject to feature map
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
        """
        x_rotation = ApplyMethod(
            image_mobject.rotate,
            ThreeDLayer.three_d_x_rotation,
            [1, 0, 0], 
            image_mobject.get_center(),
            run_time=0.5
        )
        y_rotation = ApplyMethod(
            image_mobject.rotate,
            ThreeDLayer.three_d_y_rotation,
            [0, 1, 0], 
            image_mobject.get_center(),
            run_time=0.5
        )
        """
        # Set opacity
        set_opacity = ApplyMethod(image_mobject.set_opacity, 0.2, run_time=0.5)
        # Scale the max of width or height to the
        # width of the feature_map
        def scale_image_func(image_mobject: Mobject):
            """Scale the image to match the target feature map size, preserving aspect ratio."""
            max_width_height = max(image_mobject.width, image_mobject.height)
            scale_factor = target_feature_map.untransformed_width / max_width_height
            image_mobject.scale(scale_factor)

            return image_mobject

        scale_image = ApplyFunction(scale_image_func, image_mobject)
        # scale_image = ApplyMethod(image_mobject.scale, scale_factor, run_time=0.5)
        # Move the image
        move_image = ApplyMethod(image_mobject.move_to, target_feature_map)
        # Compose the animations
        animation = Succession(
            rotation,
            scale_image,
            set_opacity,
            move_image,
        )
        return animation

    def scale(self, scale_factor: float, **kwargs):
        """Scale the layer by forwarding to the parent class.

        Parameters
        ----------
        scale_factor : float
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