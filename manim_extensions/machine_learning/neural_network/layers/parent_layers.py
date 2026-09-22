# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Parent layer classes for neural network visualizations.

This module provides abstract base classes for neural network layer visualizations.

"""

from typing import Any

from manim import (
    Animation,
    AnimationGroup,
    Create,
    DEFAULT_FONT_SIZE,
    Group,
    SurroundingRectangle,
    Text,
    UP,
    Wait,
    override_animation,
)
from abc import ABC, abstractmethod

class NeuralNetworkLayer(ABC, Group):
    """Abstract Neural Network Layer class

    Parameters
    ----------
    text : str, optional
        Text of the layer title; unused in the base implementation.
    args : tuple
        Positional arguments forwarded to the parent class.
    **kwargs
        Forwarded to the parent class; a ``"title"`` entry adds a title above
        the layer.

    Examples
    --------
    .. manim:: NeuralNetworkLayerExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.parent_layers import NeuralNetworkLayer

       class NeuralNetworkLayerExample(Scene):
           def construct(self):
               # NeuralNetworkLayer is abstract; FeedForwardLayer is a
               # concrete subclass.
               layer = FeedForwardLayer(3)
               layer.construct_layer(None, None)
               assert isinstance(layer, NeuralNetworkLayer)
               self.add(layer)
    """

    def __init__(self, text: str | None = None, *args: Any, **kwargs: Any) -> None:
        """TODO: add docstring for __init__."""
        super(Group, self).__init__()
        self.title_text = kwargs["title"] if "title" in kwargs else " "
        self.title: Text | Group
        if "title" in kwargs:
            self.title = Text(self.title_text, font_size=DEFAULT_FONT_SIZE // 3).scale(0.6)
            self.title.next_to(self, UP, 1.2)
        else:
            self.title = Group()
        # self.add(self.title)

    @abstractmethod
    def construct_layer(
        self,
        input_layer: "NeuralNetworkLayer",
        output_layer: "NeuralNetworkLayer",
        **kwargs: Any,
    ) -> None:
        """Constructs the layer at network construction time

        Parameters
        ----------
        input_layer : NeuralNetworkLayer
            preceding layer
        output_layer : NeuralNetworkLayer
            following layer
        **kwargs
            Forwarded to the parent class; a ``"debug_mode"`` entry draws a
            surrounding rectangle around the layer.
        """
        if "debug_mode" in kwargs and kwargs["debug_mode"]:
            self.add(SurroundingRectangle(self))

    @abstractmethod
    def make_forward_pass_animation(
        self, *args: Any, **kwargs: Any
    ) -> Animation:
        """Makes the forward pass animation for the layer.

        Parameters
        ----------
        **kwargs
            Forwarded to the layer's forward pass animation.

        Returns
        -------
        Animation
            The forward pass animation.
        """
        pass

    @override_animation(Create)
    def _create_override(self) -> Animation:
        # A zero-duration Wait: connective layers have no visible geometry to
        # create, and manim >= 0.21 raises when playing an empty Succession.
        return Wait(run_time=0)

    def __repr__(self) -> str:
        return f"{type(self).__name__}"

class VGroupNeuralNetworkLayer(NeuralNetworkLayer):
    """Neural network layer variant based on :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Parameters
    ----------
    args : tuple
        Positional arguments forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.VGroupNeuralNetworkLayer.NeuralNetworkLayer`.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.VGroupNeuralNetworkLayer.NeuralNetworkLayer`.

    Examples
    --------
    .. manim:: VGroupNeuralNetworkLayerExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.parent_layers import VGroupNeuralNetworkLayer

       class VGroupNeuralNetworkLayerExample(Scene):
           def construct(self):
               # VGroupNeuralNetworkLayer is abstract; FeedForwardLayer is a
               # concrete subclass.
               layer = FeedForwardLayer(4)
               layer.construct_layer(None, None)
               assert isinstance(layer, VGroupNeuralNetworkLayer)
               self.add(layer)
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """TODO: add docstring for __init__."""
        super().__init__(*args, **kwargs)
        # self.camera = camera

    @abstractmethod
    def make_forward_pass_animation(self, *args: Any, **kwargs: Any) -> Animation:
        """Makes the forward pass animation for the layer.

        Parameters
        ----------
        **kwargs
            Forwarded to the layer's forward pass animation.

        Returns
        -------
        Animation
            The forward pass animation.
        """
        pass

    @override_animation(Create)
    def _create_override(self) -> Animation:
        return super()._create_override()

class ThreeDLayer(ABC):
    """Abstract class for 3D layers"""
    pass
    # Angle of ThreeD layers is static context


class ConnectiveLayer(VGroupNeuralNetworkLayer):
    """Forward pass animation for a given pair of layers

    Parameters
    ----------
    input_layer : NeuralNetworkLayer
        The layer the forward pass animation starts from.
    output_layer : NeuralNetworkLayer
        The layer the forward pass animation ends at.
    **kwargs
        Forwarded to the parent layer classes.

    Examples
    --------
    .. manim:: ConnectiveLayerExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.feed_forward_to_feed_forward import FeedForwardToFeedForward
       from manim_extensions.machine_learning.neural_network.layers.parent_layers import ConnectiveLayer

       class ConnectiveLayerExample(Scene):
           def construct(self):
               # ConnectiveLayer is abstract; FeedForwardToFeedForward is a
               # concrete subclass.
               input_layer = FeedForwardLayer(3).shift(LEFT * 2)
               output_layer = FeedForwardLayer(2).shift(RIGHT * 2)
               input_layer.construct_layer(None, None)
               output_layer.construct_layer(None, None)
               connection = FeedForwardToFeedForward(input_layer, output_layer)
               assert isinstance(connection, ConnectiveLayer)
               self.add(input_layer, output_layer, connection)
    """

    @abstractmethod
    def __init__(
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs: Any,
    ) -> None:
        """TODO: add docstring for __init__."""
        super(VGroupNeuralNetworkLayer, self).__init__(**kwargs)
        self.input_layer = input_layer
        self.output_layer = output_layer
        # Handle input and output class
        # assert isinstance(input_layer, self.input_class), f"{input_layer}, {self.input_class}"
        # assert isinstance(output_layer, self.output_class), f"{output_layer}, {self.output_class}"

    @abstractmethod
    def make_forward_pass_animation(
        self, run_time: float = 2.0, layer_args: Any = {}, **kwargs: Any
    ) -> Animation:
        """Makes the forward pass animation between the connected layers.

        Parameters
        ----------
        run_time : float, optional
            Run time of the forward pass animation, by default 2.0.
        layer_args : Any, optional
            Additional arguments passed to the connected layers when making
            their forward pass animations, by default {}.
        **kwargs
            Forwarded to the layer's forward pass animation.

        Returns
        -------
        Animation
            The forward pass animation.
        """
        pass

    @override_animation(Create)
    def _create_override(self) -> Animation:
        return super()._create_override()

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            + f"input_layer={self.input_layer.__class__.__name__},"
            + f"output_layer={self.output_layer.__class__.__name__},"
            + ")"
        )


class BlankConnective(ConnectiveLayer):
    """Connective layer to be used when the given pair of layers is undefined

    Parameters
    ----------
    input_layer : NeuralNetworkLayer
        The layer the connection starts from.
    output_layer : NeuralNetworkLayer
        The layer the connection ends at.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.BlankConnective.ConnectiveLayer`.

    Examples
    --------
    .. manim:: BlankConnectiveExample
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.layers.feed_forward import FeedForwardLayer
       from manim_extensions.machine_learning.neural_network.layers.feed_forward_to_feed_forward import FeedForwardToFeedForward
       from manim_extensions.machine_learning.neural_network.layers.parent_layers import BlankConnective

       class BlankConnectiveExample(Scene):
           def construct(self):
               # BlankConnective is abstract (construct_layer is not
               # implemented); NeuralNetwork uses it for layer pairs without
               # a specific connective. FeedForwardToFeedForward shows what
               # a concrete connective looks like.
               input_layer = FeedForwardLayer(3).shift(LEFT * 2)
               output_layer = FeedForwardLayer(2).shift(RIGHT * 2)
               input_layer.construct_layer(None, None)
               output_layer.construct_layer(None, None)
               connection = FeedForwardToFeedForward(input_layer, output_layer)
               self.add(input_layer, output_layer, connection)
    """

    def __init__(
        self,
        input_layer: NeuralNetworkLayer,
        output_layer: NeuralNetworkLayer,
        **kwargs: Any,
    ) -> None:
        """TODO: add docstring for __init__."""
        super().__init__(input_layer, output_layer, **kwargs)

    def make_forward_pass_animation(
        self, run_time: float = 1.5, layer_args: Any = {}, **kwargs: Any
    ) -> Animation:
        """Makes an empty forward pass animation for the blank connection.

        Parameters
        ----------
        run_time : float, optional
            Run time of the forward pass animation, by default 1.5.
        layer_args : Any, optional
            Additional arguments passed to the connected layers when making
            their forward pass animations, by default {}.
        **kwargs
            Forwarded to the layer's forward pass animation.

        Returns
        -------
        Animation
            The forward pass animation.
        """
        return AnimationGroup(run_time=run_time)

    @override_animation(Create)
    def _create_override(self) -> Animation:
        return super()._create_override()

