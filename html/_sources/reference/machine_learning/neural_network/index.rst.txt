.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

neural_network
==============

.. module:: manim_extensions.machine_learning.neural_network

Classes
-------

.. autosummary::
   :nosignatures:

   ~neural_network.NeuralNetwork

Usage
-----

Compose a network from layer objects and run a forward pass.

.. manim:: NetworkScene
   :ref_classes: FeedForwardLayer NeuralNetwork

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       FeedForwardLayer,
       NeuralNetwork,
   )

   class NetworkScene(Scene):
       def construct(self):
           network = NeuralNetwork(
               [FeedForwardLayer(4), FeedForwardLayer(6), FeedForwardLayer(3)]
           )
           network.scale_to_fit_height(6).move_to(ORIGIN)
           self.add(network)
           self.play(network.make_forward_pass_animation(run_time=1.0))

Modules
-------

.. autosummary::
   :nosignatures:

   ~activation_functions
   ~animations
   ~architectures
   ~layers
   ~neural_network

.. toctree::
   :hidden:
   :maxdepth: 1

   activation_functions/index
   animations/index
   architectures/index
   layers/index
   neural_network
