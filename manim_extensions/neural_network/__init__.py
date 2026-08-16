# SPDX-FileCopyrightText: 2024 Javier Pozo Miranda
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Neural network visualisation helpers.

This package provides mobjects for constructing stylised neural network diagrams.

Examples
--------
.. manim:: NeuralNetworkPackageDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions.neural_network import NeuralNetworkMobject

   class NeuralNetworkPackageDocExample(Scene):
       def construct(self):
"""

from .neural_network import NeuralNetworkMobject