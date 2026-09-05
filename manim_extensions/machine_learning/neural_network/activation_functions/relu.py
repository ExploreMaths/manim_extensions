# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""ReLU activation function visualization."""

from manim import *  # noqa: F401

from .activation_function import ActivationFunction

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
    """

    def __init__(self, function_name="ReLU", x_range=[-1, 1], y_range=[-1, 1]):
        super().__init__(function_name, x_range, y_range)

    def apply_function(self, x_val):
        if x_val < 0:
            return 0
        else:
            return x_val