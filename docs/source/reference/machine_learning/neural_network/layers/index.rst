.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

layers
======

.. automodule:: manim_extensions.machine_learning.neural_network.layers

Usage
-----

Layers are the units passed to :class:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork`.

.. manim:: FeedForwardLayerOverview
   :save_last_frame:
   :ref_classes: FeedForwardLayer

   from manim import *
   from manim_extensions.machine_learning.neural_network import NeuralNetwork
   from manim_extensions.machine_learning.neural_network.layers import FeedForwardLayer

   class FeedForwardLayerOverview(Scene):
       def construct(self):
           layer = FeedForwardLayer(5, node_color=BLUE, node_outline_color=WHITE)
           network = NeuralNetwork([layer])
           network.scale_to_fit_height(6).move_to(ORIGIN)
           self.add(network)

Modules
-------

.. autosummary::
   :nosignatures:

   ~convolutional_2d
   ~convolutional_2d_to_convolutional_2d
   ~convolutional_2d_to_feed_forward
   ~convolutional_2d_to_max_pooling_2d
   ~embedding
   ~embedding_to_feed_forward
   ~feed_forward
   ~feed_forward_to_embedding
   ~feed_forward_to_feed_forward
   ~feed_forward_to_image
   ~feed_forward_to_math_operation
   ~feed_forward_to_vector
   ~image
   ~image_to_convolutional_2d
   ~image_to_feed_forward
   ~math_operation_layer
   ~max_pooling_2d
   ~max_pooling_2d_to_convolutional_2d
   ~max_pooling_2d_to_feed_forward
   ~paired_query
   ~paired_query_to_feed_forward
   ~parent_layers
   ~triplet
   ~triplet_to_feed_forward
   ~util
   ~vector

Constants
---------

.. autoall:: manim_extensions.machine_learning.neural_network.layers
   :types: data

.. toctree::
   :hidden:
   :maxdepth: 1

   convolutional_2d
   convolutional_2d_to_convolutional_2d
   convolutional_2d_to_feed_forward
   convolutional_2d_to_max_pooling_2d
   embedding
   embedding_to_feed_forward
   feed_forward
   feed_forward_to_embedding
   feed_forward_to_feed_forward
   feed_forward_to_image
   feed_forward_to_math_operation
   feed_forward_to_vector
   image
   image_to_convolutional_2d
   image_to_feed_forward
   math_operation_layer
   max_pooling_2d
   max_pooling_2d_to_convolutional_2d
   max_pooling_2d_to_feed_forward
   paired_query
   paired_query_to_feed_forward
   parent_layers
   triplet
   triplet_to_feed_forward
   util
   vector
