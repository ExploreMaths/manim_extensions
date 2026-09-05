# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""ReLU activation function visualization."""

from manim import *

from .activation_function import ActivationFunction

class ReLUFunction(ActivationFunction):
    """Rectified Linear Unit Activation Function"""

    def __init__(self, function_name="ReLU", x_range=[-1, 1], y_range=[-1, 1]):
        super().__init__(function_name, x_range, y_range)

    def apply_function(self, x_val):
        if x_val < 0:
            return 0
        else:
            return x_val