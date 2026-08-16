.. SPDX-FileCopyrightText: 2024 Javier Pozo Miranda
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Neural network
==============

**Original author:** `Javier Pozo Miranda <https://github.com/JPM2002>`_

**Source repository:** `GitHub <https://github.com/JPM2002/manim-neural-network>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-neural-network`` is a lightweight neural-network visualisation library
for Manim. It is aimed at teaching ML architecture layouts and layer structure
without requiring a full custom scene-building pipeline.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.neural_network`` subpackage.

Features
--------

- :class:`~manim_extensions.neural_network.neural_network.NeuralNetworkMobject` – main layered network display.
- input/output and hidden-layer layout helpers.
- connection lines between adjacent layers.
- simple styling options for neuron groups and edge placement.
- lecture-oriented visuals for deep-learning explanations.

Quick start
-----------

.. manim:: NeuralNetworkLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.neural_network import NeuralNetworkMobject

   class NeuralNetworkLibraryExample(Scene):
       def construct(self):
           network = NeuralNetworkMobject([3, 5, 2])
           self.add(network)

This library is best suited for:

* ML and deep-learning lectures,
* architecture diagrams,
* layer-structure explanations in teaching videos.

See the `original project page <https://github.com/JPM2002/manim-neural-network>`_
for examples and implementation notes.

.. toctree::
   :hidden:

   classes