from manim import *
import itertools as it

# A customizable Sequential Neural Network
class NeuralNetworkMobject(VGroup):
    """Visual representation of a feed-forward neural network.

    Each layer is drawn as a vertical stack of circular neurons and connections
    are drawn as edges between adjacent layers.

    Parameters
    ----------
    neural_network : Sequence[int]
        Number of neurons in each layer, including the input and output layers.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------

    .. manim:: NeuralNetworkMobjectDocExample
      :save_last_frame:

       from manim import *
       from manim_extensions.neural_network import NeuralNetworkMobject

       class NeuralNetworkMobjectDocExample(Scene):
           def construct(self):
               nn = NeuralNetworkMobject([3, 4, 2])
               self.add(nn)
    """

    def __init__(self, neural_network, **kwargs):
        """Create a layered neural network graph from a list of layer sizes."""
        super().__init__(**kwargs)
        self.layer_sizes = neural_network
        self.neuron_radius = 0.15
        self.neuron_to_neuron_buff = 0.2
        self.layer_to_layer_buff = 1.0
        self.output_neuron_color = WHITE
        self.input_neuron_color = WHITE
        self.hidden_layer_neuron_color = WHITE
        self.neuron_stroke_width = 2
        self.neuron_fill_opacity = 1
        self.edge_color = LIGHT_GREY
        self.edge_stroke_width = 2
        self.add_neurons()
        self.add_edges()
        self.add_to_back(self.layers)

    def add_neurons(self):
        """Create the neuron layers and arrange them horizontally."""
        layers = VGroup(*[
            self.get_layer(size, index)
            for index, size in enumerate(self.layer_sizes)
        ])
        layers.arrange(RIGHT, buff=self.layer_to_layer_buff)
        self.layers = layers

    def get_nn_fill_color(self, index):
        """Return the stroke colour for the layer at the given index.

        The first layer uses :attr:`input_neuron_color`, the last layer
        uses :attr:`output_neuron_color`, and every layer in between uses
        :attr:`hidden_layer_neuron_color`.

        Parameters
        ----------
        index : int
            Layer index (0-based).

        Returns
        -------
        ManimColor
            The colour assigned to the requested layer type.
        """
        if index == 0:
            return self.input_neuron_color
        elif index == len(self.layer_sizes) - 1:
            return self.output_neuron_color
        else:
            return self.hidden_layer_neuron_color

    def get_layer(self, size, index=-1):
        """Create a single layer containing *size* neurons arranged vertically.

        Each neuron is drawn as a circle with the layer-specific stroke
        colour returned by :meth:`get_nn_fill_color`.

        Parameters
        ----------
        size : int
            Number of neurons in the layer.
        index : int, optional
            Layer index used to determine the stroke colour (default ``-1``).

        Returns
        -------
        VGroup
            A group containing the neuron circles for this layer.
        """
        layer = VGroup()
        neurons = VGroup(*[
            Circle(
                radius=self.neuron_radius,
                stroke_color=self.get_nn_fill_color(index),
                stroke_width=self.neuron_stroke_width,
                fill_color=BLACK,
                fill_opacity=self.neuron_fill_opacity,
            )
            for _ in range(size)
        ])
        for neuron in neurons:
            neuron.z_index = 1  # Ensure neurons are in front of edges
        neurons.arrange(DOWN, buff=self.neuron_to_neuron_buff)
        layer.neurons = neurons
        layer.add(neurons)
        return layer


    def add_edges(self):
        """Draw edges connecting the neuron layers."""
        self.edge_groups = VGroup()
        for l1, l2 in zip(self.layers[:-1], self.layers[1:]):
            edge_group = VGroup()
            for n1, n2 in it.product(l1.neurons, l2.neurons):
                edge = Line(
                    n1.get_center(),
                    n2.get_center(),
                    stroke_color=self.edge_color,
                    stroke_width=self.edge_stroke_width,
                )
                edge.z_index = 0  # Set edges to a lower z-index
                edge_group.add(edge)
            self.edge_groups.add(edge_group)
        self.add(self.edge_groups)  # Add edges first



    def label_inputs(self, label):
        """Add symbolic labels to the input layer neurons.

        Parameters
        ----------
        label : str
            Base name used for the input labels, for example ``"x"``.
        """
        for i, neuron in enumerate(self.layers[0].neurons):
            text = MathTex(f"{label}_{{{i + 1}}}")
            text.set_height(0.3)
            text.next_to(neuron, LEFT)
            self.add(text)

    def label_outputs(self, label):
        """Add symbolic labels to the output layer neurons.

        Parameters
        ----------
        label : str
            Base name used for the output labels, for example ``"y"``.
        """
        for i, neuron in enumerate(self.layers[-1].neurons):
            text = MathTex(f"{label}_{{{i + 1}}}")
            text.set_height(0.3)
            text.next_to(neuron, RIGHT)
            self.add(text)


    def label_layers(self, labels, input_size=0.4, hidden_size=0.25, output_size=0.4):
        """Add text labels above each layer of the neural network.

        Parameters
        ----------
        labels : Sequence[str]
            Labels assigned to each layer in order.
        input_size : float, optional
            Scale factor used for the first layer label.
        hidden_size : float, optional
            Scale factor used for hidden-layer labels.
        output_size : float, optional
            Scale factor used for the final layer label.

        Returns
        -------
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`
            The group containing the layer labels.
        """
        label_objects = VGroup()
        for i, (label_text, layer) in enumerate(zip(labels, self.layers)):
            label = Text(label_text)

            if i == 0:
                label.scale(input_size)
            elif i == len(self.layers) - 1:
                label.scale(output_size)
            else:
                label.scale(hidden_size)

            label.next_to(layer, UP)
            label_objects.add(label)

        self.add(label_objects)
        return label_objects