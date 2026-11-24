.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

animations
==========

.. module:: manim_extensions.machine_learning.neural_network.animations

Usage
-----

Layer insertion, removal, and dropout animations are applied to an existing network.

.. code-block:: python

   from manim_extensions.machine_learning.neural_network.animations.neural_network_transformations import (
       InsertLayer,
       RemoveLayer,
   )
   from manim_extensions.machine_learning.neural_network.animations.dropout import (
       make_forward_pass_with_dropout_animation,
   )

Modules
-------

.. autosummary::
   :nosignatures:

   ~dropout
   ~neural_network_transformations

.. toctree::
   :hidden:
   :maxdepth: 1

   dropout
   neural_network_transformations
