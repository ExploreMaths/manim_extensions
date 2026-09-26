# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""ReLU activation function visualization."""


from .activation_function import ActivationFunction

from typing import Any
class ReLUFunction(ActivationFunction):
    """Rectified Linear Unit Activation Function

    Parameters
    ----------
    function_name : str, optional
        Name displayed next to the plot, by default "ReLU".
    x_range : list, optional
        Range of the x-axis, by default [-1, 1].
    y_range : list, optional
        Range of the y-axis, by default [-1, 1].

    Examples
    --------
    .. manim:: ReLUFunctionDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.activation_functions import (
           ReLUFunction,
       )

       class ReLUFunctionDocExample(Scene):
           def construct(self):
               relu = ReLUFunction()
               relu.scale(4)
               relu.move_to(ORIGIN)
               self.add(relu)
    """

    def __init__(self, function_name: str = "ReLU", x_range: list = [-1, 1], y_range: list = [-1, 1]):
        """Initialize the ReLU activation function plot with default range settings."""
        super().__init__(function_name, x_range, y_range)

    def apply_function(self, x_val: Any):
        """Return max(0, x_val), the ReLU activation applied to the input value.

        Parameters
        ----------
        x_val : Any
            Input value to which the ReLU activation is applied.
        """
        if x_val < 0:
            return 0
        else:
            return x_val