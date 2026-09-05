# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Max pooling 2D to convolutional 2D layer connection visualization."""

from manim import *

from .convolutional_2d_to_convolutional_2d import Convolutional2DToConvolutional2D
from .max_pooling_2d import MaxPooling2DLayer
from .convolutional_2d import Convolutional2DLayer



class MaxPooling2DToConvolutional2D(Convolutional2DToConvolutional2D):
    """Connective layer between a max pooling 2D layer and a convolutional 2D layer

    Parameters
    ----------
    input_layer : MaxPooling2DLayer
        The input max pooling layer.
    output_layer : Convolutional2DLayer
        The output convolutional layer.
    passing_flash_color : ManimColor, optional
        Color of the flash animation during the forward pass, by default ORANGE.
    cell_width : float, optional
        Width of a single grid cell, by default 1.0.
    stroke_width : float, optional
        Stroke width of the filter rectangles, by default 2.0.
    show_grid_lines : bool, optional
        Whether to show the grid lines, by default False.
    **kwargs
        Forwarded to
        :class:`~manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_convolutional_2d.Convolutional2DToConvolutional2D`.
    """

    input_class = MaxPooling2DLayer
    output_class = Convolutional2DLayer

    def __init__(
        self,
        input_layer: MaxPooling2DLayer,
        output_layer: Convolutional2DLayer,
        passing_flash_color=ORANGE,
        cell_width=1.0,
        stroke_width=2.0,
        show_grid_lines=False,
        **kwargs
    ):
        input_layer.num_feature_maps = output_layer.num_feature_maps
        super().__init__(input_layer, output_layer, **kwargs)
        self.passing_flash_color = passing_flash_color
        self.cell_width = cell_width
        self.stroke_width = stroke_width
        self.show_grid_lines = show_grid_lines

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs
    ):
        """Constructs the MaxPooling to Convolution3D layer

        Parameters
        ----------
        input_layer : NeuralNetworkLayer
            input layer
        output_layer : NeuralNetworkLayer
            output layer
        """
        super().construct_layer(input_layer, output_layer, **kwargs)