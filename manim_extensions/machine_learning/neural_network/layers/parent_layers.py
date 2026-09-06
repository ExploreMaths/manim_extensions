# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Parent layer classes for neural network visualizations.

This module provides abstract base classes for neural network layer visualizations.

"""

from manim import *
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
    """

    def __init__(self, text=None, *args, **kwargs):
        super(Group, self).__init__()
        self.title_text = kwargs["title"] if "title" in kwargs else " "
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
        **kwargs,
    ):
        """Constructs the layer at network construction time

        Parameters
        ----------
        input_layer : NeuralNetworkLayer
            preceding layer
        output_layer : NeuralNetworkLayer
            following layer
        """
        if "debug_mode" in kwargs and kwargs["debug_mode"]:
            self.add(SurroundingRectangle(self))

    @abstractmethod
    def make_forward_pass_animation(self, layer_args={}, **kwargs):
        pass

    @override_animation(Create)
    def _create_override(self):
        # A zero-duration Wait: connective layers have no visible geometry to
        # create, and manim >= 0.21 raises when playing an empty Succession.
        return Wait(run_time=0)

    def __repr__(self):
        return f"{type(self).__name__}"

class VGroupNeuralNetworkLayer(NeuralNetworkLayer):
    """Neural network layer variant based on :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Parameters
    ----------
    args : tuple
        Positional arguments forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.VGroupNeuralNetworkLayer.NeuralNetworkLayer`.
    **kwargs
        Forwarded to :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.VGroupNeuralNetworkLayer.NeuralNetworkLayer`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.camera = camera

    @abstractmethod
    def make_forward_pass_animation(self, **kwargs):
        pass

    @override_animation(Create)
    def _create_override(self):
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
    """

    @abstractmethod
    def __init__(self, input_layer, output_layer, **kwargs):
        super(VGroupNeuralNetworkLayer, self).__init__(**kwargs)
        self.input_layer = input_layer
        self.output_layer = output_layer
        # Handle input and output class
        # assert isinstance(input_layer, self.input_class), f"{input_layer}, {self.input_class}"
        # assert isinstance(output_layer, self.output_class), f"{output_layer}, {self.output_class}"

    @abstractmethod
    def make_forward_pass_animation(self, run_time=2.0, layer_args={}, **kwargs):
        pass

    @override_animation(Create)
    def _create_override(self):
        return super()._create_override()

    def __repr__(self):
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
    """

    def __init__(self, input_layer, output_layer, **kwargs):
        super().__init__(input_layer, output_layer, **kwargs)

    def make_forward_pass_animation(self, run_time=1.5, layer_args={}, **kwargs):
        return AnimationGroup(run_time=run_time)

    @override_animation(Create)
    def _create_override(self):
        return super()._create_override()