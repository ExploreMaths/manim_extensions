.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

layers
======

.. module:: manim_extensions.machine_learning.neural_network.layers

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

.. autosummary::
   :nosignatures:

   ~connective_layers_list

.. autodata:: manim_extensions.machine_learning.neural_network.layers.connective_layers_list

.. toctree::
   :hidden:
   :maxdepth: 1

   convolutional_2d
   convolutional_2d.Convolutional2DLayer
   convolutional_2d.FeatureMap
   convolutional_2d_to_convolutional_2d
   convolutional_2d_to_convolutional_2d.Convolutional2DToConvolutional2D
   convolutional_2d_to_convolutional_2d.Filters
   convolutional_2d_to_feed_forward
   convolutional_2d_to_feed_forward.Convolutional2DToFeedForward
   convolutional_2d_to_max_pooling_2d
   convolutional_2d_to_max_pooling_2d.Convolutional2DToMaxPooling2D
   embedding
   embedding.EmbeddingLayer
   embedding.NeuralNetworkEmbeddingTestScene
   embedding_to_feed_forward
   embedding_to_feed_forward.EmbeddingToFeedForward
   feed_forward
   feed_forward.FeedForwardLayer
   feed_forward_to_embedding
   feed_forward_to_embedding.FeedForwardToEmbedding
   feed_forward_to_feed_forward
   feed_forward_to_feed_forward.FeedForwardToFeedForward
   feed_forward_to_image
   feed_forward_to_image.FeedForwardToImage
   feed_forward_to_math_operation
   feed_forward_to_math_operation.FeedForwardToMathOperation
   feed_forward_to_vector
   feed_forward_to_vector.FeedForwardToVector
   image
   image.ImageLayer
   image_to_convolutional_2d
   image_to_convolutional_2d.ImageToConvolutional2DLayer
   image_to_feed_forward
   image_to_feed_forward.ImageToFeedForward
   math_operation_layer
   math_operation_layer.MathOperationLayer
   max_pooling_2d
   max_pooling_2d.MaxPooling2DLayer
   max_pooling_2d_to_convolutional_2d
   max_pooling_2d_to_convolutional_2d.MaxPooling2DToConvolutional2D
   max_pooling_2d_to_feed_forward
   max_pooling_2d_to_feed_forward.MaxPooling2DToFeedForward
   paired_query
   paired_query.PairedQueryLayer
   paired_query_to_feed_forward
   paired_query_to_feed_forward.PairedQueryToFeedForward
   parent_layers
   parent_layers.BlankConnective
   parent_layers.ConnectiveLayer
   parent_layers.NeuralNetworkLayer
   parent_layers.ThreeDLayer
   parent_layers.VGroupNeuralNetworkLayer
   triplet
   triplet.TripletLayer
   triplet_to_feed_forward
   triplet_to_feed_forward.TripletToFeedForward
   util
   vector
   vector.VectorLayer
