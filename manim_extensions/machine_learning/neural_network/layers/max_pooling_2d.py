# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Max pooling 2D layer visualization for neural networks."""

from manim import *
from ...utils.mobjects.gridded_rectangle import GriddedRectangle

from .parent_layers import ThreeDLayer, VGroupNeuralNetworkLayer
from ... import config

class MaxPooling2DLayer(VGroupNeuralNetworkLayer, ThreeDLayer):
    """Max pooling layer for Convolutional2DLayer

    Note: This is for a Convolutional2DLayer even though
    it is called MaxPooling2DLayer because the 2D corresponds
    to the 2 spatial dimensions of the convolution.

    Parameters
    ----------
    kernel_size : int or tuple, optional
        Width/Height of max pooling kernel, by default 2.
    stride : int, optional
        Stride of the max pooling operation, by default 1.
    cell_highlight_color : ManimColor, optional
        Color used to highlight the pooled cells, by default ORANGE.
    cell_width : float, optional
        Width of a single cell, by default 0.2.
    filter_spacing : float, optional
        Spacing between feature maps, by default 0.1.
    color : ManimColor, optional
        Color of the feature map borders, by default BLUE.
    show_grid_lines : bool, optional
        Whether to show the grid lines, by default False.
    stroke_width : float, optional
        Stroke width of the borders, by default 2.0.
    **kwargs
        Forwarded to the parent layer classes.

    Examples
    --------
    .. manim:: MaxPooling2DLayerDocExample

       from manim import *
       from manim_extensions.machine_learning.neural_network import (
           Convolutional2DLayer,
           MaxPooling2DLayer,
           NeuralNetwork,
       )

       # Widescreen layout used by the upstream ManimML examples
       config.pixel_height = 1200
       config.pixel_width = 1900
       config.frame_height = 6.0
       config.frame_width = 6.0

       class MaxPooling2DLayerDocExample(ThreeDScene):
           def construct(self):
               nn = NeuralNetwork(
                   [
                       Convolutional2DLayer(1, 8),
                       Convolutional2DLayer(3, 6, 3),
                       MaxPooling2DLayer(kernel_size=2),
                       Convolutional2DLayer(5, 2, 2),
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
        kernel_size=2,
        stride=1,
        cell_highlight_color=ORANGE,
        cell_width=0.2,
        filter_spacing=0.1,
        color=BLUE,
        show_grid_lines=False,
        stroke_width=2.0,
        **kwargs
    ):
        """Layer object for animating 2D Convolution Max Pooling

        Parameters
        ----------
        kernel_size : int or tuple, optional
            Width/Height of max pooling kernel, by default 2
        stride : int, optional
            Stride of the max pooling operation, by default 1
        """
        super().__init__(**kwargs)
        self.kernel_size = kernel_size
        self.stride = stride
        self.cell_highlight_color = cell_highlight_color
        self.cell_width = cell_width
        self.filter_spacing = filter_spacing
        self.color = color
        self.show_grid_lines = show_grid_lines
        self.stroke_width = stroke_width
        self.padding = (0, 0)

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs
    ):
        # Make the output feature maps
        self.feature_maps = self._make_output_feature_maps(
            input_layer.num_feature_maps, input_layer.feature_map_size
        )
        self.add(self.feature_maps)
        self.rotate(
            config.three_d_config.rotation_angle,
            about_point=self.get_center(),
            axis=config.three_d_config.rotation_axis
        )
        self.feature_map_size = (
            input_layer.feature_map_size[0] / self.kernel_size,
            input_layer.feature_map_size[1] / self.kernel_size,
        )
        super().construct_layer(input_layer, output_layer, **kwargs)


    def _make_output_feature_maps(self, num_input_feature_maps, input_feature_map_size):
        """Makes a set of output feature maps"""
        # Compute the size of the feature maps
        output_feature_map_size = (
            input_feature_map_size[0] / self.kernel_size,
            input_feature_map_size[1] / self.kernel_size,
        )
        # Draw rectangles that are filled in with opacity
        feature_maps = []
        for filter_index in range(num_input_feature_maps):
            rectangle = GriddedRectangle(
                color=self.color,
                height=output_feature_map_size[1] * self.cell_width,
                width=output_feature_map_size[0] * self.cell_width,
                fill_color=self.color,
                fill_opacity=0.2,
                stroke_color=self.color,
                stroke_width=self.stroke_width,
                grid_xstep=self.cell_width,
                grid_ystep=self.cell_width,
                grid_stroke_width=self.stroke_width / 2,
                grid_stroke_color=self.color,
                show_grid_lines=self.show_grid_lines,
            )
            # Move the feature map
            rectangle.move_to([0, 0, filter_index * self.filter_spacing])
            # rectangle.set_z_index(4)
            feature_maps.append(rectangle)

        return VGroup(*feature_maps)

    def make_forward_pass_animation(self, layer_args={}, **kwargs):
        """Makes forward pass of Max Pooling Layer.

        Parameters
        ----------
        layer_args : dict, optional
            _description_, by default {}
        """
        return AnimationGroup()

    @override_animation(Create)
    def _create_override(self, **kwargs):
        """Create animation for the MaxPooling operation"""
        pass