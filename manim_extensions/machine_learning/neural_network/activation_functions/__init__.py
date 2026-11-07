# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""Activation functions for neural network visualization."""

from .relu import ReLUFunction
from .sigmoid import SigmoidFunction

#: Mapping from activation function name to its class.
name_to_activation_function_map = {"ReLU": ReLUFunction, "Sigmoid": SigmoidFunction}


def get_activation_function_by_name(name):
    """Return the activation function class matching the given name."""
    assert (
        name in name_to_activation_function_map.keys()
    ), f"Unrecognized activation function {name}"

    return name_to_activation_function_map[name]
