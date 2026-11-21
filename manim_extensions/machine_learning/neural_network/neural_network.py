# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: implement replace_layer

"""Neural Network Manim Visualization.

This module is responsible for generating a neural network visualization with
manim, specifically a fully connected neural network diagram.

.. code-block:: python

    # Specify how many nodes are in each node layer
    layer_node_count = [5, 3, 5]
    # Create the object with default style settings
    NeuralNetwork(layer_node_count)
"""

from __future__ import annotations
from typing import Any, Callable, Literal, cast

# unlinked-class-ok: Layout, Filters


import textwrap
from ..utils.mobjects.connections import NetworkConnection
import numpy as np
from manim import (
    Animation,
    AnimationGroup,
    Create,
    DEFAULT_FONT_SIZE,
    FadeOut,
    Group,
    ManimColor,
    Mobject,
    ORIGIN,
    ShowPassingFlash,
    Succession,
    Text,
    UP,
    UpdateFromFunc,
    Wait,
    override_animation,
)

from .layers.parent_layers import ConnectiveLayer
from .layers.util import get_connective_layer
from ..utils.mobjects.list_group import ListGroup
from .animations.neural_network_transformations import InsertLayer, RemoveLayer
from .. import config


class NeuralNetwork(Group):
    """Neural Network Visualization Container Class.

    Parameters
    ----------
    input_layers
        Neural network layers to visualize; a list is converted to a dict with
        default names.
    layer_spacing
        Spacing between the layers.
    animation_dot_color
        Color of the dots in the forward pass animation.
    edge_width
        Stroke width of the connective edges.
    dot_radius
        Radius of the dots in the forward pass animation.
    title
        Title displayed above the network.
    layout
        Layout of the network.
    layout_direction
        Direction of the linear layout.
    debug_mode
        Whether to enable debug visuals.

    Examples
    --------
    .. manim:: NeuralNetworkScene

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

       class NeuralNetworkScene(ThreeDScene):
           def construct(self):
               nn = NeuralNetwork(
                   [
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
               # Animate the forward pass
               forward_pass = nn.make_forward_pass_animation()
               self.play(forward_pass)
    """

    def __init__(
        self,
        input_layers: list[Any],
        layer_spacing: float = 0.2,
        animation_dot_color: ManimColor = cast(Any, config).color_scheme.active_color,
        edge_width: float = 2.5,
        dot_radius: float = 0.03,
        title: str = " ",
        layout: str = "linear",
        layout_direction: Literal["left_to_right", "top_to_bottom"] = "left_to_right",
        debug_mode: bool = False,
    ) -> None:
        super(Group, self).__init__()
        self.input_layers_dict = self.make_input_layers_dict(input_layers)
        self.input_layers = ListGroup(*cast(Any, self.input_layers_dict).values())
        self.edge_width = edge_width
        self.layer_spacing = layer_spacing
        self.animation_dot_color = animation_dot_color
        self.dot_radius = dot_radius
        self.title_text = title
        self.created = False
        self.layout = layout
        self.layout_direction = layout_direction
        self.debug_mode = debug_mode
        # Construct all of the layers
        self._construct_input_layers()
        # Place the layers
        self._place_layers(layout=layout, layout_direction=layout_direction)
        # Make the connective layers
        self.connective_layers, self.all_layers = self._construct_connective_layers()
        # Place the connective layers
        self._place_connective_layers()
        # Make overhead title
        self.title = Text(self.title_text, font_size=DEFAULT_FONT_SIZE / 2)
        self.title.next_to(self, UP * self.layer_spacing, buff=0.25)
        self.add(self.title)
        # Place layers at correct z index
        self.connective_layers.set_z_index(2)
        self.input_layers.set_z_index(3)
        # Center the whole diagram by default
        self.all_layers.move_to(ORIGIN)
        self.add(self.all_layers)
        # Make container for connections
        self.connections: list[Any] = []
        # Print neural network
        print(repr(self))

    def make_input_layers_dict(self, input_layers: list[Any]) -> dict[Any, Any] | None:
        """Make dictionary of input layers.

        Parameters
        ----------
        input_layers
            Neural network layers to visualize; a list is converted to a dict
            with default names, a dict is returned unchanged.

        Returns
        -------
            A dictionary of the results. ``None`` if there is no result.

        Raises
        ------
        Exception
            Raised when ``input_layers`` is neither a list nor a dict.
        """
        if isinstance(input_layers, dict):
            # If input layers is dictionary then return it
            return input_layers
        elif isinstance(input_layers, list):
            # If input layers is a list then make a dictionary with default
            return_dict = {}
            for layer_index, input_layer in enumerate(input_layers):
                return_dict[f"layer{layer_index}"] = input_layer

            return return_dict
        else:
            raise Exception(f"Uncrecognized input layers type: {type(input_layers)}")

    def add_connection(
        self,
        start_mobject_or_name: Mobject | str,
        end_mobject_or_name: Mobject | str,
        connection_style: str = "default",
        connection_position: str = "bottom",
        arc_direction: str = "down",
    ) -> Any:
        """Add connection from start layer to end layer.

        Parameters
        ----------
        start_mobject_or_name
            The layer the connection starts from, or its name in the network.
        end_mobject_or_name
            The layer the connection ends at, or its name in the network.
        connection_style
            Style of the connection; currently only "default" is supported.
        connection_position
            Unused position hint reserved for future use.
        arc_direction
            Direction the connection arc bends.


            Returns
            -------
                The resulting value.
        """
        assert connection_style in ["default"]
        if connection_style == "default":
            # Make arrow connection from start layer to end layer
            # Add the connection
            if isinstance(start_mobject_or_name, Mobject):
                input_mobject = start_mobject_or_name
            else:
                input_mobject = cast(Any, self.input_layers_dict)[start_mobject_or_name]
            if isinstance(end_mobject_or_name, Mobject):
                output_mobject = end_mobject_or_name
            else:
                output_mobject = cast(Any, self.input_layers_dict)[end_mobject_or_name]

            connection = NetworkConnection(
                input_mobject, output_mobject, arc_direction=arc_direction, buffer=0.05
            )
            self.connections.append(connection)
            self.add(connection)

    def _construct_input_layers(self) -> Any:
        """Constructs each of the input layers in context
        of their adjacent layers..

            Returns
            -------
                The resulting value.
        """
        prev_layer = None
        next_layer = None
        # Go through all the input layers and run their construct method
        print("Constructing layers")
        for layer_index in range(len(self.input_layers)):
            current_layer = self.input_layers[layer_index]
            print(f"Current layer: {current_layer}")
            if layer_index < len(self.input_layers) - 1:
                next_layer = self.input_layers[layer_index + 1]
            if layer_index > 0:
                prev_layer = self.input_layers[layer_index - 1]
            # Run the construct layer method for each
            cast(Any, current_layer).construct_layer(
                prev_layer, next_layer, debug_mode=self.debug_mode
            )

    def _place_layers(
        self,
        layout: str = "linear",
        layout_direction: Literal["left_to_right", "top_to_bottom"] = "top_to_bottom",
    ) -> Any:
        """Position the layers of the network.

        Parameters
        ----------
        layout
            Layout mode for the network.
        layout_direction
            Direction in which layers are arranged.


        Returns
        -------
            The resulting value.

        Raises
        ------
        Exception
            If an unsupported layout mode is requested.

        """
        # Default: Linear layout
        for layer_index in range(1, len(self.input_layers)):
            previous_layer = self.input_layers[layer_index - 1]
            current_layer = self.input_layers[layer_index]
            cast(Any, current_layer).move_to(cast(Any, previous_layer).get_center())

            if layout_direction == "left_to_right":
                x_shift = (
                    cast(Any, previous_layer).width / 2
                    + cast(Any, current_layer).width / 2
                    + self.layer_spacing
                )
                shift_vector = np.array([x_shift, 0, 0])
            elif layout_direction == "top_to_bottom":
                y_shift = -(
                    (
                        cast(Any, previous_layer).width / 2
                        + cast(Any, current_layer).width / 2
                    )
                    + self.layer_spacing
                )
                shift_vector = np.array([0, y_shift, 0])
            else:
                raise Exception(f"Unrecognized layout direction: {layout_direction}")
            cast(Any, current_layer).shift(shift_vector)

        # After all layers have been placed place their activation functions
        layer_max_height = max([layer.height for layer in self.input_layers])
        for current_layer in self.input_layers:
            # Place activation function
            if hasattr(current_layer, "activation_function"):
                if not current_layer.activation_function is None:
                    # Get max height of layer
                    up_movement = np.array(
                        [
                            0,
                            layer_max_height / 2
                            + cast(Any, current_layer.activation_function).height / 2
                            + 0.5 * self.layer_spacing,
                            0,
                        ]
                    )
                    cast(Any, current_layer.activation_function).move_to(
                        current_layer,
                    )
                    cast(Any, current_layer.activation_function).match_y(
                        self.input_layers[0]
                    )
                    cast(Any, current_layer.activation_function).shift(up_movement)
                    self.add(cast(Any, current_layer).activation_function)

    def _construct_connective_layers(self) -> tuple[ListGroup, ListGroup]:
        """Draws connecting lines between layers.

        Returns
        -------
            The connective layers and the combined list of all layers.
        """
        connective_layers = ListGroup()
        all_layers = ListGroup()
        for layer_index in range(len(self.input_layers) - 1):
            current_layer = self.input_layers[layer_index]
            # Add the layer to the list of layers
            all_layers.add(cast(Mobject, current_layer))
            next_layer = self.input_layers[layer_index + 1]
            # Check if layer is actually a nested NeuralNetwork
            if isinstance(current_layer, NeuralNetwork):
                # Last layer of the current layer
                current_layer = current_layer.all_layers[-1]
            if isinstance(next_layer, NeuralNetwork):
                # First layer of the next layer
                next_layer = next_layer.all_layers[0]
            # Find connective layer with correct layer pair
            connective_layer = get_connective_layer(
                cast(Mobject, current_layer), cast(Mobject, next_layer)
            )
            connective_layers.add(connective_layer)
            # Construct the connective layer
            connective_layer.construct_layer(
                cast(Any, current_layer), cast(Any, next_layer)
            )
            # Add the layer to the list of layers
            all_layers.add(connective_layer)
        # Add final layer
        all_layers.add(cast(Mobject, self.input_layers[-1]))
        # Handle layering
        return connective_layers, all_layers

    def _place_connective_layers(self) -> Any:
        """Center each connective layer between its input and output layers.

        Returns
        -------
            The resulting value.
        """
        # Place each of the connective layers halfway between the adjacent layers
        for connective_layer in self.connective_layers:
            layer_midpoint = (
                cast(Any, connective_layer.input_layer).get_center()
                + cast(Any, connective_layer.output_layer).get_center()
            ) / 2
            connective_layer.move_to(layer_midpoint)

    def insert_layer(self, layer: Mobject, insert_index: int) -> InsertLayer:
        """Inserts a layer at the given index.

        Parameters
        ----------
        layer
            The layer to insert.
        insert_index
            Position in ``all_layers`` at which to insert the layer.

        Returns
        -------
            Animation that inserts the layer into the network.
        """
        neural_network = self
        insert_animation = InsertLayer(layer, insert_index, neural_network)
        return insert_animation

    def remove_layer(self, layer: Mobject) -> RemoveLayer:
        """Removes layer object if it exists.

        Parameters
        ----------
        layer
            The layer to remove.

        Returns
        -------
            Animation that removes the layer from the network.
        """
        neural_network = self
        return RemoveLayer(layer, neural_network, layer_spacing=self.layer_spacing)

    def replace_layer(self, old_layer: Mobject, new_layer: Mobject) -> Succession:
        """Replaces given layer object.

        The old layer is faded out, the new layer is constructed in the
        context of the old layer's neighbours, the surrounding connective
        layers are rebuilt, and the new layer is revealed.

        Parameters
        ----------
        old_layer
            The layer to be replaced.
        new_layer
            The layer that takes the place of ``old_layer``.

        Returns
        -------
            Animation that swaps the two layers.

        Raises
        ------
        Exception
            Raised when ``old_layer`` is not part of the network.
        """
        input_index = self.input_layers.index_of(old_layer)
        if input_index == -1:
            raise Exception("Layer object not found")
        previous_layer = self.input_layers[input_index - 1] if input_index > 0 else None
        next_layer = (
            self.input_layers[input_index + 1]
            if input_index + 1 < len(self.input_layers)
            else None
        )
        # Build the new layer in the context of its neighbours
        new_layer.construct_layer(previous_layer, next_layer)
        new_layer.move_to(old_layer)
        prior_center = self.all_layers.get_center()

        def swap_layer(network: NeuralNetwork) -> Any:
            """Replace the layer and rebuild the surrounding connections."""
            network.input_layers.replace(input_index, new_layer)
            for name, layer in cast(Any, network.input_layers_dict).items():
                if layer is old_layer:
                    cast(Any, network.input_layers_dict)[name] = new_layer
            # Remove the stale activation function from the scene
            if hasattr(old_layer, "activation_function"):
                if old_layer.activation_function is not None:
                    network.remove(cast(Any, old_layer).activation_function)
            # Rebuild the layers and connections around the new layer
            network.remove(network.all_layers)
            (
                network.connective_layers,
                network.all_layers,
            ) = network._construct_connective_layers()
            network._place_layers(
                layout=network.layout, layout_direction=network.layout_direction
            )
            network._place_connective_layers()
            network.connective_layers.set_z_index(2)
            network.input_layers.set_z_index(3)
            network.all_layers.move_to(prior_center)
            network.add(network.all_layers)

        return Succession(
            FadeOut(old_layer),
            UpdateFromFunc(self, cast(Any, swap_layer)),
            Create(cast(Any, new_layer)),
            lag_ratio=1.0,
        )

    def make_forward_pass_animation(
        self,
        run_time: float | None = None,
        passing_flash: bool = True,
        layer_args: dict[Any, Any] = {},
        per_layer_animations: bool = False,
        **kwargs: Any,
    ) -> Succession | dict[Mobject, Animation]:
        """Generates an animation for feed forward propagation.

        Parameters
        ----------
        run_time
            Total run time of the forward pass; the run time is divided
            evenly across the layers.
        passing_flash
            Whether to flash the connections while the signal passes through.
        layer_args
            Extra keyword arguments for individual layers, keyed by layer
            mobject. For connective layers the arguments of the adjacent
            layers are merged in.
        per_layer_animations
            If True, return a mapping from each layer to its animation
            instead of a single combined animation.
        **kwargs
            Additional keyword arguments forwarded to each layer's
            ``make_forward_pass_animation``.

        Returns
        -------
            The forward-pass animation, or a mapping from each layer to
            its animation when ``per_layer_animations`` is ``True``.
        """
        all_animations = []
        per_layer_animation_map = {}
        per_layer_runtime = (
            run_time / len(self.all_layers) if not run_time is None else None
        )
        for layer_index, layer in enumerate(self.all_layers):
            # Get the layer args
            if isinstance(layer, ConnectiveLayer):
                # NOTE: By default a connective layer will get the combined
                # layer_args of the layers it is connecting and itself.
                before_layer_args = {}
                current_layer_args = {}
                after_layer_args = {}
                if layer.input_layer in layer_args:
                    before_layer_args = layer_args[layer.input_layer]
                if layer in layer_args:
                    current_layer_args = layer_args[layer]
                if layer.output_layer in layer_args:
                    after_layer_args = layer_args[layer.output_layer]
                # Merge the two dicts
                current_layer_args = {
                    **before_layer_args,
                    **current_layer_args,
                    **after_layer_args,
                }
            else:
                current_layer_args = {}
                if layer in layer_args:
                    current_layer_args = layer_args[layer]
            # Perform the forward pass of the current layer
            layer_forward_pass = layer.make_forward_pass_animation(
                layer_args=current_layer_args, run_time=per_layer_runtime, **kwargs
            )

            # Animate a forward pass for incoming connections.
            # Layers without an activation function (e.g. Convolutional2DLayer)
            # return an empty AnimationGroup; manim raises when playing empty
            # groups, so only keep non-empty animations.
            def _is_empty(animation: Animation) -> bool:
                """Return whether an animation group contains no animations."""
                return (
                    isinstance(animation, AnimationGroup)
                    and len(animation.animations) == 0
                )

            subanimations = (
                [] if _is_empty(layer_forward_pass) else [layer_forward_pass]
            )
            for connection in self.connections:
                if isinstance(layer, ConnectiveLayer):
                    output_layer = layer.output_layer
                    if connection.end_mobject == output_layer:
                        subanimations.append(
                            ShowPassingFlash(
                                connection,
                                run_time=layer_forward_pass.run_time,
                                time_width=0.2,
                            )
                        )
                        break

            if len(subanimations) > 0:
                layer_forward_pass = AnimationGroup(*subanimations, lag_ratio=0.0)
                all_animations.append(layer_forward_pass)
            # Add the animation to per layer animation
            per_layer_animation_map[layer] = layer_forward_pass
        # Make the animation group
        animation_group = Succession(*all_animations, lag_ratio=1.0)
        if per_layer_animations:
            return per_layer_animation_map
        else:
            return animation_group

    @override_animation(Create)
    def _create_override(self, **kwargs: Any) -> Animation:
        """Create the network with a single guarded pass.

        Parameters
        ----------
        **kwargs
            Keyword arguments forwarded to the creation animations.

        Returns
        -------
            The animation that reveals the network, or an empty wait when it has
            already been created.
        """
        # Stop the neural network from being created twice
        if self.created:
            # manim >= 0.21 raises when playing an empty AnimationGroup.
            return Wait(run_time=0)
        self.created = True

        animations: list[Animation] = []
        # Create the overhead title
        animations.append(Create(cast(Any, self.title)))
        # Create each layer one by one
        for layer in self.all_layers:
            layer_animation = Create(cast(Any, layer))
            # Make titles (empty default titles are plain Groups and
            # cannot be played with Create, so skip them)
            if len(cast(Any, layer.title).submobjects) > 0:
                create_title = Create(cast(Any, layer.title))
                # Create layer animation group
                animation_group = AnimationGroup(layer_animation, create_title)
            else:
                animation_group = AnimationGroup(layer_animation)
            animations.append(animation_group)

        animation_group = AnimationGroup(*animations, lag_ratio=1.0)

        return animation_group

    def set_z_index(self, z_index_value: float, family: bool = False) -> Any:
        """Overridden set_z_index.

        Parameters
        ----------
        z_index_value
            The z-index to set on each layer.
        family
            Kept for signature compatibility; setting ``family=False`` stops
            sub-neural networks from inheriting the parent z-index.


            Returns
            -------
                The resulting value.
        """
        # Setting family=False stops sub-neural networks from inheriting parent z_index
        for layer in self.all_layers:
            if not isinstance(layer, NeuralNetwork):
                layer.set_z_index(z_index_value)

    def scale(self, scale_factor: float, **kwargs: Any) -> Any:
        """Overridden scale.

        Scales every layer and re-places the layers and connective layers
        with scaled spacing, keeping the network centered.

        Parameters
        ----------
        scale_factor
            The scaling factor.
        **kwargs
            Additional keyword arguments forwarded to each layer's ``scale``.


            Returns
            -------
                The resulting value.
        """
        prior_center = self.get_center()

        for layer in self.all_layers:
            layer.scale(scale_factor, **kwargs)
        # Place layers with scaled spacing
        self.layer_spacing *= scale_factor
        # self.connective_layers, self.all_layers = self._construct_connective_layers()
        self._place_layers(layout=self.layout, layout_direction=self.layout_direction)
        self._place_connective_layers()
        # Scale the title
        self.remove(self.title)
        self.title.scale(scale_factor, **kwargs)
        self.title.next_to(self, UP, buff=0.25 * scale_factor)
        self.add(self.title)

        self.move_to(prior_center)

    def filter_layers(self, function: Callable[..., Any]) -> list[Any]:
        """Filters layers of the network given function.

        Parameters
        ----------
        function
            Predicate called with each layer; it must return a boolean
            indicating whether the layer is kept.

        Returns
        -------
            The layers for which ``function`` returned True.
        """
        layers_to_return = []
        for layer in self.all_layers:
            func_out = function(layer)
            assert isinstance(
                func_out, bool
            ), "Filter layers function returned a non-boolean type."
            if func_out:
                layers_to_return.append(layer)

        return layers_to_return

    def __repr__(self, metadata: list[str] = ["z_index", "title_text"]) -> str:
        """Return a layer-by-layer representation.

        Parameters
        ----------
        metadata
            Layer attributes included in the representation.

        Returns
        -------
            The textual representation of all layers.
        """
        inner_string = ""
        for layer in self.all_layers:
            inner_string += f"{repr(layer)}("
            for key in metadata:
                value = getattr(layer, key)
                if value != "":
                    inner_string += f"{key}={value}, "
            inner_string += "),\n"
        inner_string = textwrap.indent(inner_string, "    ")

        string_repr = "NeuralNetwork([\n" + inner_string + "])"
        return string_repr
