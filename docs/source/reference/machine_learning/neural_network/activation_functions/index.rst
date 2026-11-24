.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

activation_functions
====================

.. module:: manim_extensions.machine_learning.neural_network.activation_functions

Usage
-----

Plot an activation function on its own.

.. manim:: ActivationScene
   :save_last_frame:
   :ref_classes: ReLUFunction SigmoidFunction

   from manim import *
   from manim_extensions.machine_learning.neural_network.activation_functions import (
       ReLUFunction,
       SigmoidFunction,
   )

   class ActivationScene(Scene):
       def construct(self):
           relu = ReLUFunction()
           relu.scale(4).move_to(ORIGIN)
           self.add(relu)

Modules
-------

.. autosummary::
   :nosignatures:

   ~activation_function
   ~relu
   ~sigmoid

Functions
---------

.. autoall:: manim_extensions.machine_learning.neural_network.activation_functions
   :types: function

Constants
---------

.. autoall:: manim_extensions.machine_learning.neural_network.activation_functions
   :types: data

.. toctree::
   :hidden:
   :maxdepth: 1

   activation_function
   relu
   sigmoid
