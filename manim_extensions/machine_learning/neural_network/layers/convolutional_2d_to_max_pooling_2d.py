# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Convolutional 2D to max pooling 2D layer connection visualization."""

from __future__ import annotations
from typing import Any, cast

import random

import numpy as np
from manim import (
    AnimationGroup,
    Create,
    ManimColor,
    ORANGE,
    ReplacementTransform,
    Succession,
    Uncreate,
    VGroup,
    Wait,
)
from ...utils.mobjects.gridded_rectangle import GriddedRectangle

from .max_pooling_2d import MaxPooling2DLayer
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer, ThreeDLayer
from .convolutional_2d import Convolutional2DLayer

from ... import config


class Convolutional2DToMaxPooling2D(ConnectiveLayer, ThreeDLayer):
    """Connective layer between a convolutional 2D layer and a max pooling 2D layer.

    Parameters
    ----------
    input_layer
        The input convolutional layer.
    output_layer
        The output max pooling layer.
    active_color
        Color used to highlight the kernel windows.
    **kwargs
        Forwarded to the parent layer classes.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.machine_learning.neural_network.layers.convolutional_2d import Convolutional2DLayer
        from manim_extensions.machine_learning.neural_network.layers.max_pooling_2d import MaxPooling2DLayer
        from manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_max_pooling_2d import Convolutional2DToMaxPooling2D

        conv = Convolutional2DLayer(4, 6, 3)
        pool = MaxPooling2DLayer(kernel_size=2)
        connection = Convolutional2DToMaxPooling2D(conv, pool)
    """

    input_class = Convolutional2DLayer
    output_class = MaxPooling2DLayer

    def __init__(
        self,
        input_layer: Convolutional2DLayer,
        output_layer: MaxPooling2DLayer,
        active_color: ManimColor = ORANGE,
        **kwargs: Any,
    ) -> None:
        super().__init__(cast(Any, input_layer), cast(Any, output_layer), **kwargs)
        self.active_color = active_color

    def construct_layer(
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs: Any,
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
        """
        super().construct_layer(input_layer, output_layer, **kwargs)
        return None

    def make_forward_pass_animation(
        self, layer_args: dict[Any, Any] = {}, run_time: float = 1.5, **kwargs: Any
    ) -> Succession:
        """Forward pass animation from conv2d to max pooling.

        Parameters
        ----------
        layer_args
            Additional arguments passed to the connected layers when making
            their forward pass animations.
        run_time
            Run time of the forward pass animation.
        **kwargs
            Forwarded to the parent layer classes.

        Returns
        -------
            A :class:`~manim.animation.composition.Succession` instance representing the result.
        """
        input_layer = cast(Convolutional2DLayer, self.input_layer)
        output_layer = cast(MaxPooling2DLayer, self.output_layer)
        cell_width = input_layer.cell_width
        feature_map_size = input_layer.feature_map_size
        kernel_size = output_layer.kernel_size
        feature_maps = input_layer.feature_maps
        grid_stroke_width = 1.0
        # Make all of the kernel gridded rectangles
        create_gridded_rectangle_animations: list[Any] = []
        create_and_remove_cell_animations: list[Any] = []
        transform_gridded_rectangle_animations: list[Any] = []
        remove_gridded_rectangle_animations: list[Any] = []

        for feature_map_index, feature_map in enumerate(feature_maps):
            # 1. Draw gridded rectangle with kernel_size x kernel_size
            #   box regions over the input feature maps.
            gridded_rectangle = GriddedRectangle(
                color=self.active_color,
                height=cell_width * feature_map_size[1],
                width=cell_width * feature_map_size[0],
                grid_xstep=cell_width * kernel_size,
                grid_ystep=cell_width * kernel_size,
                grid_stroke_width=grid_stroke_width,
                grid_stroke_color=self.active_color,
                show_grid_lines=True,
            )
            gridded_rectangle.set_z_index(10)
            # 2. Randomly highlight one of the cells in the kernel.
            highlighted_cells = []
            num_cells_in_kernel = kernel_size * kernel_size
            num_x_kernels = int(feature_map_size[0] / kernel_size)
            num_y_kernels = int(feature_map_size[1] / kernel_size)
            for kernel_x in range(0, num_x_kernels):
                for kernel_y in range(0, num_y_kernels):
                    # Choose a random cell index
                    cell_index = random.randint(0, num_cells_in_kernel - 1)
                    # Make a rectangle in that cell
                    cell_rectangle = GriddedRectangle(
                        color=self.active_color,
                        height=cell_width,
                        width=cell_width,
                        fill_opacity=0.7,
                        stroke_width=0.0,
                        z_index=10,
                    )
                    # Move to the correct location
                    kernel_shift_vector = np.array(
                        [
                            kernel_size * cell_width * kernel_x,
                            -1 * kernel_size * cell_width * kernel_y,
                            0,
                        ]
                    )
                    cell_shift_vector = np.array(
                        [
                            (cell_index % kernel_size) * cell_width,
                            -1 * int(cell_index / kernel_size) * cell_width,
                            0,
                        ]
                    )
                    cell_rectangle.next_to(
                        gridded_rectangle.get_corners_dict()["top_left"],
                        submobject_to_align=cell_rectangle.get_corners_dict()[
                            "top_left"
                        ],
                        buff=0.0,
                    )
                    cell_rectangle.shift(kernel_shift_vector)
                    cell_rectangle.shift(cell_shift_vector)
                    highlighted_cells.append(cell_rectangle)
            # Rotate the gridded rectangles so they match the angle
            # of the conv maps
            gridded_rectangle_group = VGroup(gridded_rectangle, *highlighted_cells)
            gridded_rectangle_group.rotate(
                cast(Any, config).three_d_config.rotation_angle,
                about_point=gridded_rectangle.get_center(),
                axis=cast(Any, config).three_d_config.rotation_axis,
            )
            gridded_rectangle_group.next_to(
                feature_map.get_corners_dict()["top_left"],
                submobject_to_align=gridded_rectangle.get_corners_dict()["top_left"],
                buff=0.0,
            )
            # 3. Make a create gridded rectangle
            create_rectangle = Create(
                gridded_rectangle,
            )
            create_gridded_rectangle_animations.append(create_rectangle)
            # 4. Create and fade out highlighted cells
            create_group = AnimationGroup(
                *[Create(highlighted_cell) for highlighted_cell in highlighted_cells],
                lag_ratio=1.0,
            )
            uncreate_group = AnimationGroup(
                *[Uncreate(highlighted_cell) for highlighted_cell in highlighted_cells],
                lag_ratio=0.0,
            )
            create_and_remove_cell_animation = Succession(
                create_group, Wait(1.0), uncreate_group
            )
            create_and_remove_cell_animations.append(create_and_remove_cell_animation)
            # 5. Move and resize the gridded rectangle to the output
            #   feature maps.
            output_gridded_rectangle = GriddedRectangle(
                color=self.active_color,
                height=cell_width * feature_map_size[1] / 2,
                width=cell_width * feature_map_size[0] / 2,
                grid_xstep=cell_width,
                grid_ystep=cell_width,
                grid_stroke_width=grid_stroke_width,
                grid_stroke_color=self.active_color,
                show_grid_lines=True,
            )
            output_gridded_rectangle.rotate(
                cast(Any, config).three_d_config.rotation_angle,
                about_point=output_gridded_rectangle.get_center(),
                axis=cast(Any, config).three_d_config.rotation_axis,
            )
            output_gridded_rectangle.move_to(
                output_layer.feature_maps[feature_map_index].copy()
            )
            transform_rectangle = ReplacementTransform(
                gridded_rectangle,
                output_gridded_rectangle,
                introducer=True,
            )
            transform_gridded_rectangle_animations.append(
                transform_rectangle,
            )
            """
            Succession(
                Uncreate(gridded_rectangle),
                transform_rectangle,
                lag_ratio=1.0
            )
            """
            # 6. Make the gridded feature map(s) disappear.
            remove_gridded_rectangle_animations.append(
                Uncreate(gridded_rectangle_group)
            )

        create_gridded_rectangle_animation = AnimationGroup(
            *create_gridded_rectangle_animations
        )
        create_and_remove_cell_animation_group = AnimationGroup(
            *create_and_remove_cell_animations
        )
        transform_gridded_rectangle_animation = AnimationGroup(
            *transform_gridded_rectangle_animations
        )
        remove_gridded_rectangle_animation = AnimationGroup(
            *remove_gridded_rectangle_animations
        )

        return Succession(
            create_gridded_rectangle_animation,
            Wait(1),
            create_and_remove_cell_animation_group,
            transform_gridded_rectangle_animation,
            Wait(1),
            remove_gridded_rectangle_animation,
            lag_ratio=1.0,
        )
