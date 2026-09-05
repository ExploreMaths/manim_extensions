# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Activation functions for neural network visualization."""

from .relu import ReLUFunction
from .sigmoid import SigmoidFunction

name_to_activation_function_map = {"ReLU": ReLUFunction, "Sigmoid": SigmoidFunction}


def get_activation_function_by_name(name):
    assert (
        name in name_to_activation_function_map.keys()
    ), f"Unrecognized activation function {name}"

    return name_to_activation_function_map[name]