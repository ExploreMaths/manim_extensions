.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Machine Learning
================

.. module:: manim_extensions.machine_learning

.. vendored-status:: helblazer811/ManimML

**Original author:** `Alec Helbling <https://github.com/helblazer811>`_

**Source repository:** `GitHub <https://github.com/helblazer811/ManimML>`_

**License:** MIT

``ManimML`` is a machine-learning visualisation toolkit for Manim. It
provides animated neural networks, decision trees, and diffusion model
diagrams.

The code is bundled inside ``manim_extensions`` as the
:mod:`~manim_extensions.machine_learning` subpackage.

.. inheritance-diagram:: manim_extensions.machine_learning.decision_tree.decision_tree.LeafNode manim_extensions.machine_learning.decision_tree.decision_tree.SplitNode manim_extensions.machine_learning.decision_tree.decision_tree.DecisionTreeDiagram manim_extensions.machine_learning.decision_tree.decision_tree_surface.IrisDatasetPlot manim_extensions.machine_learning.decision_tree.decision_tree_surface.DecisionTreeSurface manim_extensions.machine_learning.decision_tree.decision_tree_embedding.DecisionTreeEmbedding manim_extensions.machine_learning.decision_tree.helpers.SklearnTree manim_extensions.machine_learning.diffusion.mcmc.MCMCAxes manim_extensions.machine_learning.neural_network.activation_functions.activation_function.ActivationFunction manim_extensions.machine_learning.neural_network.activation_functions.relu.ReLUFunction manim_extensions.machine_learning.neural_network.activation_functions.sigmoid.SigmoidFunction manim_extensions.machine_learning.neural_network.animations.dropout.XMark manim_extensions.machine_learning.neural_network.animations.neural_network_transformations.RemoveLayer manim_extensions.machine_learning.neural_network.animations.neural_network_transformations.InsertLayer manim_extensions.machine_learning.neural_network.architectures.variational_autoencoder.VariationalAutoencoder manim_extensions.machine_learning.neural_network.architectures.feed_forward.FeedForwardNeuralNetwork manim_extensions.machine_learning.neural_network.layers.convolutional_2d.FeatureMap manim_extensions.machine_learning.neural_network.layers.convolutional_2d.Convolutional2DLayer manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_convolutional_2d.Filters manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_convolutional_2d.Convolutional2DToConvolutional2D manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_feed_forward.Convolutional2DToFeedForward manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_max_pooling_2d.Convolutional2DToMaxPooling2D manim_extensions.machine_learning.neural_network.layers.embedding.EmbeddingLayer manim_extensions.machine_learning.neural_network.layers.embedding.NeuralNetworkEmbeddingTestScene manim_extensions.machine_learning.neural_network.layers.embedding_to_feed_forward.EmbeddingToFeedForward manim_extensions.machine_learning.neural_network.layers.feed_forward.FeedForwardLayer manim_extensions.machine_learning.neural_network.layers.feed_forward_to_embedding.FeedForwardToEmbedding manim_extensions.machine_learning.neural_network.layers.feed_forward_to_feed_forward.FeedForwardToFeedForward manim_extensions.machine_learning.neural_network.layers.feed_forward_to_image.FeedForwardToImage manim_extensions.machine_learning.neural_network.layers.feed_forward_to_math_operation.FeedForwardToMathOperation manim_extensions.machine_learning.neural_network.layers.feed_forward_to_vector.FeedForwardToVector manim_extensions.machine_learning.neural_network.layers.image.ImageLayer manim_extensions.machine_learning.neural_network.layers.image_to_convolutional_2d.ImageToConvolutional2DLayer manim_extensions.machine_learning.neural_network.layers.image_to_feed_forward.ImageToFeedForward manim_extensions.machine_learning.neural_network.layers.math_operation_layer.MathOperationLayer manim_extensions.machine_learning.neural_network.layers.max_pooling_2d.MaxPooling2DLayer manim_extensions.machine_learning.neural_network.layers.max_pooling_2d_to_convolutional_2d.MaxPooling2DToConvolutional2D manim_extensions.machine_learning.neural_network.layers.max_pooling_2d_to_feed_forward.MaxPooling2DToFeedForward manim_extensions.machine_learning.neural_network.layers.paired_query.PairedQueryLayer manim_extensions.machine_learning.neural_network.layers.paired_query_to_feed_forward.PairedQueryToFeedForward manim_extensions.machine_learning.neural_network.layers.parent_layers.NeuralNetworkLayer manim_extensions.machine_learning.neural_network.layers.parent_layers.VGroupNeuralNetworkLayer manim_extensions.machine_learning.neural_network.layers.parent_layers.ThreeDLayer manim_extensions.machine_learning.neural_network.layers.parent_layers.ConnectiveLayer manim_extensions.machine_learning.neural_network.layers.parent_layers.BlankConnective manim_extensions.machine_learning.neural_network.layers.triplet.TripletLayer manim_extensions.machine_learning.neural_network.layers.triplet_to_feed_forward.TripletToFeedForward manim_extensions.machine_learning.neural_network.layers.vector.VectorLayer manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork manim_extensions.machine_learning.scene.ManimML3DScene manim_extensions.machine_learning.utils.mobjects.connections.NetworkConnection manim_extensions.machine_learning.utils.mobjects.gridded_rectangle.GriddedRectangle manim_extensions.machine_learning.utils.mobjects.image.GrayscaleImageMobject manim_extensions.machine_learning.utils.mobjects.image.LabeledColorImage manim_extensions.machine_learning.utils.mobjects.list_group.ListGroup manim_extensions.machine_learning.utils.mobjects.probability.GaussianDistribution
   :parts: 1

.. important::

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
- :class:`~manim_extensions.machine_learning.decision_tree.decision_tree_embedding.DecisionTreeEmbedding`
  – dataset points on axes together with the decision areas of the tree.
- :class:`~manim_extensions.machine_learning.ManimMLConfig` – global
  colour-scheme and 3-D rotation configuration.
- Most neural-network layers and :class:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork`
  itself are importable from a single namespace,
  :mod:`~manim_extensions.machine_learning.neural_network`.
- Activation-function rendering (e.g. ``"ReLU"``, ``"Sigmoid"``) on feed-forward
  and convolutional layers.
- Image input layers, 2-D max-pooling layers, and a dropout animation.

Usage
-----

ManimML targets Manim Community Edition (not the original 3Blue1Brown
version). The upstream package was published as ``manim-ml``; here it is
bundled inside ``manim_extensions``. The project is described in the
`arXiv paper <https://arxiv.org/abs/2306.17108>`_.

Build a scene by extending ``Scene`` (or ``ThreeDScene`` when the network has
3-D content). Neural networks are composed from a list of layers, which
ManimML pieces together automatically:

.. manim:: NeuralNetworkForwardPass
   :ref_classes: Convolutional2DLayer FeedForwardLayer NeuralNetwork

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       Convolutional2DLayer,
       FeedForwardLayer,
       NeuralNetwork,
   )
   # Widescreen layout used by the upstream ManimML examples
   config.pixel_height = 700
   config.pixel_width = 1900
   config.frame_height = 7.0
   config.frame_width = 7.0

   class NeuralNetworkForwardPass(ThreeDScene):
       def construct(self):
           # Make the neural network
           nn = NeuralNetwork([
                   Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
                   Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
                   Convolutional2DLayer(5, 3, 3, filter_spacing=0.18),
                   FeedForwardLayer(3),
                   FeedForwardLayer(3),
               ],
               layer_spacing=0.25,
           )
           # Center the neural network
           nn.move_to(ORIGIN)
           self.add(nn)
           # Make a forward pass animation
           forward_pass = nn.make_forward_pass_animation()
           # Play animation
           self.play(forward_pass)

Feed-forward networks
^^^^^^^^^^^^^^^^^^^^^

For a simple feed-forward network, pass each layer's node count, then
animate the forward pass with
:meth:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork.make_forward_pass_animation`:

.. manim:: FeedForwardScene
   :ref_classes: FeedForwardLayer NeuralNetwork

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       FeedForwardLayer, NeuralNetwork,
   )
   config.pixel_height = 700
   config.pixel_width = 1900
   config.frame_height = 7.0
   config.frame_width = 7.0

   class FeedForwardScene(Scene):
       def construct(self):
           nn = NeuralNetwork([
               FeedForwardLayer(num_nodes=3),
               FeedForwardLayer(num_nodes=5),
               FeedForwardLayer(num_nodes=3),
           ])
           nn.move_to(ORIGIN)
           self.add(nn)
           self.play(nn.make_forward_pass_animation())

Convolutional networks
^^^^^^^^^^^^^^^^^^^^^^

Specify a :class:`~manim_extensions.machine_learning.neural_network.layers.convolutional_2d.Convolutional2DLayer`
as ``Convolutional2DLayer(num_feature_maps, feature_map_size, filter_size)``.
The feature-map sizes and filter dimensions of adjacent layers must match up;
the default stride is 1:

.. manim:: ConvolutionalScene
   :ref_classes: Convolutional2DLayer FeedForwardLayer NeuralNetwork

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       Convolutional2DLayer,
       FeedForwardLayer,
       NeuralNetwork,
   )
   config.pixel_height = 700
   config.pixel_width = 1900
   config.frame_height = 7.0
   config.frame_width = 7.0

   class ConvolutionalScene(ThreeDScene):
       def construct(self):
           nn = NeuralNetwork([
                   Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
                   Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
                   Convolutional2DLayer(5, 3, 3, filter_spacing=0.18),
                   FeedForwardLayer(3),
                   FeedForwardLayer(3),
               ],
               layer_spacing=0.25,
           )
           nn.move_to(ORIGIN)
           self.add(nn)
           self.play(nn.make_forward_pass_animation())

Feeding an image
^^^^^^^^^^^^^^^^

Place an :class:`~manim_extensions.machine_learning.neural_network.layers.image.ImageLayer`
before the first convolutional layer to animate an image being fed into the
network:

.. note::

   This example loads an image from an external ``digit.jpeg`` file, so it
   is shown as a runnable script rather than rendered inline.

.. code-block:: python

   import numpy as np
   from PIL import Image

   from manim import *

   from manim_extensions.machine_learning.neural_network import (
       Convolutional2DLayer, FeedForwardLayer, ImageLayer, NeuralNetwork,
   )

   config.pixel_height = 700
   config.pixel_width = 1900
   config.frame_height = 7.0
   config.frame_width = 7.0

   class ImageScene(ThreeDScene):
       def construct(self):
           numpy_image = np.asarray(Image.open("digit.jpeg"))
           nn = NeuralNetwork([
                   ImageLayer(numpy_image, height=1.5),
                   Convolutional2DLayer(1, 7, 3, filter_spacing=0.32),
                   Convolutional2DLayer(3, 5, 3, filter_spacing=0.32),
                   Convolutional2DLayer(5, 3, 3, filter_spacing=0.18),
                   FeedForwardLayer(3),
                   FeedForwardLayer(3),
               ],
               layer_spacing=0.25,
           )
           nn.move_to(ORIGIN)
           self.add(nn)
           self.play(nn.make_forward_pass_animation())

Max pooling
^^^^^^^^^^^

:class:`~manim_extensions.machine_learning.neural_network.layers.max_pooling_2d.MaxPooling2DLayer`
visualizes the 2-D max-pooling operation that shrinks convolutional feature
maps:

.. manim:: MaxPoolingScene
   :ref_classes: Convolutional2DLayer MaxPooling2DLayer NeuralNetwork

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       Convolutional2DLayer,
       MaxPooling2DLayer,
       NeuralNetwork,
   )
   config.pixel_height = 700
   config.pixel_width = 1900
   config.frame_height = 7.0
   config.frame_width = 7.0

   class MaxPoolingScene(ThreeDScene):
       def construct(self):
           nn = NeuralNetwork([
                   Convolutional2DLayer(1, 8),
                   Convolutional2DLayer(3, 6, 3),
                   MaxPooling2DLayer(kernel_size=2),
                   Convolutional2DLayer(5, 2, 2),
               ],
               layer_spacing=0.25,
           )
           nn.move_to(ORIGIN)
           self.wait(1)
           self.play(nn.make_forward_pass_animation())

Activation functions
^^^^^^^^^^^^^^^^^^^^

Pass ``activation_function`` to a layer (for example ``"ReLU"`` or
``"Sigmoid"``) to render its non-linearity:

.. manim:: ActivationScene
   :ref_classes: Convolutional2DLayer FeedForwardLayer NeuralNetwork

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       Convolutional2DLayer,
       FeedForwardLayer,
       NeuralNetwork,
   )
   config.pixel_height = 700
   config.pixel_width = 1900
   config.frame_height = 7.0
   config.frame_width = 7.0

   class ActivationScene(ThreeDScene):
       def construct(self):
           nn = NeuralNetwork([
                   Convolutional2DLayer(1, 7, filter_spacing=0.32),
                   Convolutional2DLayer(3, 5, 3, filter_spacing=0.32, activation_function="ReLU"),
                   FeedForwardLayer(3, activation_function="Sigmoid"),
               ],
               layer_spacing=0.25,
           )
           nn.move_to(ORIGIN)
           self.add(nn)
           self.play(nn.make_forward_pass_animation())

Dropout
^^^^^^^

:func:`~manim_extensions.machine_learning.neural_network.animations.dropout.make_neural_network_dropout_animation`
drops feed-forward-layer nodes, optionally runs the forward pass, and then
reverts the network to its pre-dropout appearance:

.. manim:: DropoutScene
   :ref_classes: FeedForwardLayer NeuralNetwork

   from manim import *
   from manim_extensions.machine_learning.neural_network import (
       FeedForwardLayer,
       NeuralNetwork,
   )
   from manim_extensions.machine_learning.neural_network.animations.dropout import (
       make_neural_network_dropout_animation,
   )
   config.pixel_height = 700
   config.pixel_width = 1900
   config.frame_height = 7.0
   config.frame_width = 7.0

   class DropoutScene(Scene):
       def construct(self):
           nn = NeuralNetwork([
                   FeedForwardLayer(3),
                   FeedForwardLayer(5),
                   FeedForwardLayer(3),
                   FeedForwardLayer(5),
                   FeedForwardLayer(4),
               ],
               layer_spacing=0.4,
           )
           nn.move_to(ORIGIN)
           self.add(nn)
           self.play(
               make_neural_network_dropout_animation(
                   nn, dropout_rate=0.25, do_forward_pass=True
               )
           )
           self.wait(1)

Style and configuration
^^^^^^^^^^^^^^^^^^^^^^^

:class:`~manim_extensions.machine_learning.ManimMLConfig` holds the active
colour scheme (:data:`~manim_extensions.machine_learning.utils.colorschemes.colorschemes.dark_mode` / :data:`~manim_extensions.machine_learning.utils.colorschemes.colorschemes.light_mode`) and the default 3-D camera
orientation used by neural-network scenes. Layer styling parameters such as
node radius, node spacing, and colours are set on the layer constructors.
Upstream design notes describe each layer as owning its visual content; more
elaborate animations can be built by composing smaller networks as layers.

See the `upstream README <https://github.com/helblazer811/ManimML>`_ and the
`upstream paper <https://arxiv.org/abs/2306.17108>`_ for more architecture
examples.

Modules
-------

.. autosummary::
   :nosignatures:

   ~decision_tree
   ~diffusion
   ~neural_network
   ~scene
   ~utils

Classes
-------

.. autosummary::
   :nosignatures:

   ~ManimMLConfig

.. toctree::
   :hidden:
   :maxdepth: 1

   decision_tree/index
   diffusion/index
   ManimMLConfig
   neural_network/index
   scene
   utils/index
