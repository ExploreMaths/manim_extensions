# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Utility functions for neural network layers."""

import warnings

from manim import *  # noqa: F401
from .parent_layers import BlankConnective
from . import connective_layers_list


def get_connective_layer(input_layer, output_layer):
    """
    Deduces the relevant connective layer
    """
    connective_layer_class = None
    for candidate_class in connective_layers_list:
        input_class = candidate_class.input_class
        output_class = candidate_class.output_class
        if isinstance(input_layer, input_class) and isinstance(
            output_layer, output_class
        ):
            connective_layer_class = candidate_class
            break

    if connective_layer_class is None:
        connective_layer_class = BlankConnective
        warnings.warn(
            f"Unrecognized input/output class pair: {input_layer} and {output_layer}"
        )
    # Make the instance now
    connective_layer = connective_layer_class(input_layer, output_layer)

    return connective_layer