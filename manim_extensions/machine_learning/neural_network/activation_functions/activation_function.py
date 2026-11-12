# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: highlight the evaluated point in make_evaluate_animation

"""Base class for activation function visualization."""

from manim import (
    AnimationGroup,
    ApplyMethod,
    Axes,
    Dot,
    FadeIn,
    FadeOut,
    ManimColor,
    Succession,
    SurroundingRectangle,
    Text,
    UP,
    VGroup,
    Wait,
)

from abc import ABC, abstractmethod
import random

from ... import config


class ActivationFunction(ABC, VGroup):
    """Abstract parent class for defining activation functions.

    Parameters
    ----------
    function_name
        Name displayed next to the plot.
    x_range
        Range of the x-axis.
    y_range
        Range of the y-axis.
    x_length
        Length of the x-axis.
    y_length
        Length of the y-axis.
    show_function_name
        Whether to display the function name.
    active_color
        Color used when highlighting the function.
    plot_color
        Color of the function plot.
    rectangle_color
        Color of the surrounding rectangle and axes.

    Examples
    --------
    .. manim:: ActivationFunctionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.activation_functions.activation_function import ActivationFunction
       from manim_extensions.machine_learning.neural_network.activation_functions.relu import ReLUFunction

       class ActivationFunctionExample(Scene):
           def construct(self):
               # ActivationFunction is abstract; ReLUFunction is a concrete
               # subclass.
               activation = ReLUFunction()
               assert isinstance(activation, ActivationFunction)
               activation.scale(6)
               activation.move_to(ORIGIN)
               self.add(activation)
    """

    def __init__(
        self,
        function_name: str | None = None,
        x_range: list = [-1, 1],
        y_range: list = [-1, 1],
        x_length: float = 0.5,
        y_length: float = 0.3,
        show_function_name: bool = True,
        active_color: ManimColor = config.color_scheme.active_color,
        plot_color: ManimColor = config.color_scheme.primary_color,
        rectangle_color: ManimColor = config.color_scheme.secondary_color,
    ):
        super(VGroup, self).__init__()
        self.function_name = function_name
        self.x_range = x_range
        self.y_range = y_range
        self.x_length = x_length
        self.y_length = y_length
        self.show_function_name = show_function_name
        self.active_color = active_color
        self.plot_color = plot_color
        self.rectangle_color = rectangle_color

        self.construct_activation_function()

    def construct_activation_function(self):
        """Makes the activation function."""
        # Make an axis
        self.axes = Axes(
            x_range=self.x_range,
            y_range=self.y_range,
            x_length=self.x_length,
            y_length=self.y_length,
            tips=False,
            axis_config={
                "include_numbers": False,
                "stroke_width": 0.5,
                "include_ticks": False,
                "color": self.rectangle_color,
            },
        )
        self.add(self.axes)
        # Surround the axis with a rounded rectangle.
        self.surrounding_rectangle = SurroundingRectangle(
            self.axes,
            corner_radius=0.05,
            buff=0.05,
            stroke_width=2.0,
            stroke_color=self.rectangle_color,
        )
        self.add(self.surrounding_rectangle)
        # Plot function on axis by applying it and showing in given range
        self.graph = self.axes.plot(
            lambda x: self.apply_function(x),
            x_range=self.x_range,
            stroke_color=self.plot_color,
            stroke_width=2.0,
        )
        self.add(self.graph)
        # Add the function name
        if self.show_function_name:
            function_name_text = Text(
                self.function_name, font_size=12, font="sans-serif"
            )
            function_name_text.next_to(self.axes, UP * 0.5)
            self.add(function_name_text)

    @abstractmethod
    def apply_function(self, x_val: float | None):
        """Evaluates function at given x_val.

        Abstract method: concrete subclasses implement the actual
        activation function.

        Parameters
        ----------
        x_val
            Input value at which to evaluate the function. If ``None``,
            a random value within ``x_range`` is used instead.
        """
        if x_val == None:
            x_val = random.uniform(self.x_range[0], self.x_range[1])

    def make_evaluate_animation(self, x_val: float | None = None) -> Succession:
        """Evaluates the function at a random point in the x_range.

        The graph and its surrounding rectangle are highlighted and a dot
        marks the evaluated point for the duration of the animation.

        Parameters
        ----------
        x_val
            Input value at which to evaluate the function.

        Returns
        -------
            A :class:`~manim.animation.composition.Succession` instance representing the result.
        """
        if x_val is None:
            x_val = random.uniform(self.x_range[0], self.x_range[1])
        y_val = self.apply_function(x_val)
        evaluation_dot = Dot(
            self.axes.coords_to_point(x_val, y_val),
            color=self.active_color,
        )
        # Highlight the graph
        animation_group = Succession(
            AnimationGroup(
                ApplyMethod(self.graph.set_color, self.active_color),
                ApplyMethod(
                    self.surrounding_rectangle.set_stroke_color, self.active_color
                ),
                FadeIn(evaluation_dot),
                lag_ratio=0.0,
            ),
            Wait(1),
            AnimationGroup(
                ApplyMethod(self.graph.set_color, self.plot_color),
                ApplyMethod(
                    self.surrounding_rectangle.set_stroke_color, self.rectangle_color
                ),
                FadeOut(evaluation_dot),
                lag_ratio=0.0,
            ),
            lag_ratio=1.0,
        )

        return animation_group
