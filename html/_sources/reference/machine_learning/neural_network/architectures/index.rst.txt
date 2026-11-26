.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

architectures
=============

.. automodule:: manim_extensions.machine_learning.neural_network.architectures

Usage
-----

Instantiate a ready-made architecture and style it inside a scene.

.. manim:: VAEScene
   :save_last_frame:
   :ref_classes: VariationalAutoencoder

   from manim import *
   from manim_extensions.machine_learning.neural_network.architectures import (
       VariationalAutoencoder,
   )

   class VAEScene(Scene):
       def construct(self):
           vae = VariationalAutoencoder()
           vae.scale_to_fit_width(9).move_to(ORIGIN)
           self.add(vae)

Modules
-------

.. autosummary::
   :nosignatures:

   ~feed_forward
   ~variational_autoencoder

.. toctree::
   :hidden:
   :maxdepth: 1

   feed_forward
   variational_autoencoder
