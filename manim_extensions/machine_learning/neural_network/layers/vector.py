# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Vector layer visualization for neural networks."""

from manim import *
import random

from .parent_layers import VGroupNeuralNetworkLayer


class VectorLayer(VGroupNeuralNetworkLayer):
    """Shows a vector

    Parameters
    ----------
    num_values : int
        Number of values in the vector.
    value_func : callable, optional
        Function generating the displayed value; by default samples uniformly
        from [0, 1].
    **kwargs
        Forwarded to the parent layer classes.

    Examples
    --------
    .. manim:: VectorLayerDocExample

       from manim import *
       from manim_extensions.machine_learning.neural_network import (
           FeedForwardLayer,
           NeuralNetwork,
           VectorLayer,
       )

       # Widescreen layout used by the upstream ManimML examples
       config.pixel_height = 700
       config.pixel_width = 1900
       config.frame_height = 7.0
       config.frame_width = 7.0

       class VectorLayerDocExample(Scene):
           def construct(self):
               nn = NeuralNetwork(
                   [
                       FeedForwardLayer(3),
                       VectorLayer(4),
                   ]
               )
               nn.move_to(ORIGIN)
               self.play(Create(nn))
               # Animate the forward pass
               self.play(nn.make_forward_pass_animation())
    """

    def __init__(self, num_values, value_func=lambda: random.uniform(0, 1), **kwargs):
        super().__init__(**kwargs)
        self.num_values = num_values
        self.value_func = value_func

    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs,
    ):
        super().construct_layer(input_layer, output_layer, **kwargs)
        # Make the vector
        self.vector_label = self.make_vector()
        self.add(self.vector_label)

    def make_vector(self):
        """Makes the vector"""
        if False:
            # TODO install Latex
            values = np.array([self.value_func() for i in range(self.num_values)])
            values = values[None, :].T
            vector = Matrix(values)

        vector_label = Text(f"[{self.value_func():.2f}]")
        vector_label.scale(0.3)

        return vector_label

    def make_forward_pass_animation(self, layer_args={}, **kwargs):
        return AnimationGroup()

    @override_animation(Create)
    def _create_override(self):
        """Create animation"""
        return Write(self.vector_label)