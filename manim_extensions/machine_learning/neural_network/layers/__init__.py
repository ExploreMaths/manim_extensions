# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""Neural network layers for Manim ML.

This module provides various neural network layer classes for visualizations.

"""

from .convolutional_2d_to_feed_forward import Convolutional2DToFeedForward
from .convolutional_2d_to_max_pooling_2d import Convolutional2DToMaxPooling2D
from .image_to_convolutional_2d import ImageToConvolutional2DLayer
from .max_pooling_2d_to_convolutional_2d import MaxPooling2DToConvolutional2D
from .max_pooling_2d_to_feed_forward import MaxPooling2DToFeedForward
from .convolutional_2d_to_convolutional_2d import Convolutional2DToConvolutional2D
from .convolutional_2d import Convolutional2DLayer
from .feed_forward_to_vector import FeedForwardToVector
from .paired_query_to_feed_forward import PairedQueryToFeedForward
from .embedding_to_feed_forward import EmbeddingToFeedForward
from .embedding import EmbeddingLayer
from .feed_forward_to_embedding import FeedForwardToEmbedding
from .feed_forward_to_feed_forward import FeedForwardToFeedForward
from .feed_forward_to_image import FeedForwardToImage
from .feed_forward import FeedForwardLayer
from .image_to_feed_forward import ImageToFeedForward
from .image import ImageLayer
from .parent_layers import ConnectiveLayer, NeuralNetworkLayer
from .triplet import TripletLayer
from .triplet_to_feed_forward import TripletToFeedForward
from .paired_query import PairedQueryLayer
from .max_pooling_2d import MaxPooling2DLayer
from .feed_forward_to_math_operation import FeedForwardToMathOperation

__all__ = [
    "ConnectiveLayer",
    "Convolutional2DLayer",
    "Convolutional2DToConvolutional2D",
    "Convolutional2DToFeedForward",
    "Convolutional2DToMaxPooling2D",
    "EmbeddingLayer",
    "EmbeddingToFeedForward",
    "FeedForwardLayer",
    "FeedForwardToEmbedding",
    "FeedForwardToFeedForward",
    "FeedForwardToImage",
    "FeedForwardToMathOperation",
    "FeedForwardToVector",
    "ImageLayer",
    "ImageToConvolutional2DLayer",
    "ImageToFeedForward",
    "MaxPooling2DLayer",
    "MaxPooling2DToConvolutional2D",
    "MaxPooling2DToFeedForward",
    "NeuralNetworkLayer",
    "PairedQueryLayer",
    "PairedQueryToFeedForward",
    "TripletLayer",
    "TripletToFeedForward",
    "connective_layers_list",
]

#: Registry of connective layer classes used to infer the connection between adjacent layers.
connective_layers_list = (
    EmbeddingToFeedForward,
    FeedForwardToEmbedding,
    FeedForwardToFeedForward,
    FeedForwardToImage,
    ImageToFeedForward,
    PairedQueryToFeedForward,
    TripletToFeedForward,
    FeedForwardToVector,
    Convolutional2DToConvolutional2D,
    ImageToConvolutional2DLayer,
    Convolutional2DToFeedForward,
    Convolutional2DToMaxPooling2D,
    MaxPooling2DToConvolutional2D,
    MaxPooling2DToFeedForward,
    FeedForwardToMathOperation
)
