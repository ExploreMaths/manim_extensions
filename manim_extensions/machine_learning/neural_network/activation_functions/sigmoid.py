# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Sigmoid activation function visualization."""

import numpy as np

from .activation_function import ActivationFunction


class SigmoidFunction(ActivationFunction):
    """Sigmoid Activation Function.

    Parameters
    ----------
    function_name
        Name displayed next to the plot.
    x_range
        Range of the x-axis.
    y_range
        Range of the y-axis.

    Examples
    --------
    .. manim:: SigmoidFunctionScene

       from manim import *
       from manim_extensions.machine_learning.neural_network.activation_functions import (
           SigmoidFunction,
       )

       class SigmoidFunctionScene(Scene):
           def construct(self):
               sigmoid = SigmoidFunction(x_range=[-5, 5], y_range=[0, 1])
               sigmoid.scale(4)
               sigmoid.move_to(ORIGIN)
               self.add(sigmoid)
               self.play(sigmoid.make_evaluate_animation())
               self.wait()
    """

    def __init__(
        self,
        function_name: str = "Sigmoid",
        x_range: list[float] = [-5, 5],
        y_range: list[float] = [0, 1],
    ) -> None:
        super().__init__(function_name, x_range, y_range)

    def apply_function(self, x_val: float) -> float:  # type: ignore[override]
        r"""Return :math:`\frac{1}{1 + e^{-x}}`, the sigmoid of the input value.

        Parameters
        ----------
        x_val
            Input value to which the sigmoid is applied.

        Returns
        -------
            The :math:`\frac{1}{1 + e^{-x}}`, the sigmoid of the input value.
        """
        return float(1 / (1 + np.exp(-1 * x_val)))
