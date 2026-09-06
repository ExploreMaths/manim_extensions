# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Sigmoid activation function visualization."""

from manim import *  # noqa: F401
import numpy as np

from .activation_function import ActivationFunction


class SigmoidFunction(ActivationFunction):
    """Sigmoid Activation Function

    Parameters
    ----------
    function_name : str, optional
        Name displayed next to the plot, by default "Sigmoid".
    x_range : list, optional
        Range of the x-axis, by default [-5, 5].
    y_range : list, optional
        Range of the y-axis, by default [0, 1].

    Examples
    --------
    .. manim:: SigmoidFunctionDocExample

       from manim import *
       from manim_extensions.machine_learning.neural_network.activation_functions import (
           SigmoidFunction,
       )

       class SigmoidFunctionDocExample(Scene):
           def construct(self):
               sigmoid = SigmoidFunction(x_range=[-5, 5], y_range=[0, 1])
               sigmoid.scale(2.5)
               sigmoid.move_to(ORIGIN)
               self.add(sigmoid)
               self.play(sigmoid.make_evaluate_animation())
    """

    def __init__(self, function_name="Sigmoid", x_range=[-5, 5], y_range=[0, 1]):
        super().__init__(function_name, x_range, y_range)

    def apply_function(self, x_val):
        return 1 / (1 + np.exp(-1 * x_val))