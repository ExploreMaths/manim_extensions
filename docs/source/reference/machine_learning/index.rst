.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Machine Learning
================

**Original author:** `Alec Helbling <https://github.com/helblazer811>`_

**Source repository:** `GitHub <https://github.com/helblazer811/ManimML>`_

**License:** MIT

``ManimML`` is a machine-learning visualisation toolkit for Manim. It
provides animated neural networks, decision trees, and diffusion model
diagrams.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.machine_learning`` subpackage.

.. note::

   The diffusion and decision-tree surface modules require optional
   dependencies (matplotlib, scikit-learn, seaborn, tqdm). Install them
   with ``pip install manim_extensions[ml]``.

Features
--------

- :class:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork`
  – composable neural-network visualisation with layers, edges, and
  forward-pass animations.
- Layer classes: :class:`~manim_extensions.machine_learning.neural_network.layers.feed_forward.FeedForwardLayer`, :class:`~manim_extensions.machine_learning.neural_network.layers.convolutional_2d.Convolutional2DLayer`,
  :class:`~manim_extensions.machine_learning.neural_network.layers.embedding.EmbeddingLayer`, :class:`~manim_extensions.machine_learning.neural_network.layers.image.ImageLayer`, :class:`~manim_extensions.machine_learning.neural_network.layers.vector.VectorLayer`, :class:`~manim_extensions.machine_learning.neural_network.layers.max_pooling_2d.MaxPooling2DLayer`,
  and more.
- :class:`~manim_extensions.machine_learning.decision_tree.decision_tree.DecisionTreeDiagram`
  – decision-tree diagram from a scikit-learn tree.
- :class:`~manim_extensions.machine_learning.ManimMLConfig` – global
  colour-scheme and 3-D rotation configuration.

Quick start
-----------

.. manim:: MLExample
   :save_last_frame:

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       NeuralNetwork, FeedForwardLayer,
   )

   class MLExample(Scene):
       def construct(self):
           nn = NeuralNetwork(FeedForwardLayer(3), FeedForwardLayer(5))
           self.add(nn)

.. toctree::
   :hidden:

   classes
