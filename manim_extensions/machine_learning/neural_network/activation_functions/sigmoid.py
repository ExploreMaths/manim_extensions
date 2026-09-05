# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Sigmoid activation function visualization."""

from manim import *
import numpy as np

from .activation_function import ActivationFunction


class SigmoidFunction(ActivationFunction):
    """Sigmoid Activation Function"""

    def __init__(self, function_name="Sigmoid", x_range=[-5, 5], y_range=[0, 1]):
        super().__init__(function_name, x_range, y_range)

    def apply_function(self, x_val):
        return 1 / (1 + np.exp(-1 * x_val))