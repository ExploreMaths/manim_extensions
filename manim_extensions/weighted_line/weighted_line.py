# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Weighted line class for Manim.

This module provides the WeightedLine class for displaying weighted edges in network graphs.

"""


from manim import *
from typing import Any


class WeightedLine(Line):
    """A line to display weighted edges in a network graph.

    Parameters
    ----------
    args
        Arguments to be passed to :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine.Line`
    weight
        The weight of the edge to display
    weight_config
        Dict of options to be passed to :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine.Text`
    weight_alpha
        The alpha position on the edge to show the weight
    bg_config
        Dict of options to be passed to :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine.Rectangle`
    add_bg
        Boolean to show a rectangle behind the weight
    kwargs
        Additional arguments to be passed to :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine.Line`

    Examples
    --------
    A minimal weighted edge between two points.  To use the line in a
    graph, pass the configuration to the edge object and use the
    :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine` as
    the ``edge_type``; if you are using NetworkX to
    create your graph, you can pass the edge data in the ``edge_config``
    dictionary.

    .. manim:: WeightedLineDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.weighted_line import WeightedLine

       class WeightedLineDocExample(Scene):
           def construct(self):
               weighted_line = WeightedLine(
                   0,
                   1,
                   weight=4,
               )
               self.add(weighted_line)

    .. manim:: WeightedLineGraphDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.weighted_line import WeightedLine

       class WeightedLineGraphDocExample(Scene):
           def construct(self):
               vertices = [1, 2, 3, 4, 5, 6, 7, 8]
               edges = [(1, 7), (1, 8), (2, 3), (2, 4), (2, 5),
                        (2, 8), (3, 4), (6, 1), (6, 2),
                        (6, 3), (7, 2), (7, 4)]
               g = DiGraph(vertices, edges, layout="circular", layout_scale=3,
                           labels=True, vertex_config={7: {"fill_color": RED}},
                           edge_type=WeightedLine,
                           edge_config={(1, 7): {"stroke_color": RED, "weight": 2},
                                        (7, 2): {"stroke_color": RED, "weight": 0},
                                        (7, 4): {"stroke_color": RED, "weight": 5}})
               self.add(g)

    .. manim:: WeightedLineNetworkXDocExample
       :save_last_frame:

       import networkx as nx
       from manim import *
       from manim_extensions.weighted_line import WeightedLine

       class WeightedLineNetworkXDocExample(Scene):
           def construct(self):
               G = nx.Graph()
               G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
               G.add_weighted_edges_from([(1, 7, 2), (1, 8, 3), (2, 3, 4), (2, 4, 5),
                                          (2, 5, 6), (2, 8, 1), (3, 4, 5), (6, 1, 0),
                                          (6, 2, 11), (6, 3, 15), (7, 2, 3), (7, 4, 9)])
               g = Graph(G.nodes, G.edges, layout="circular", layout_scale=3,
                         labels=True, vertex_config={7: {"fill_color": RED}},
                         edge_type=WeightedLine,
                         edge_config={(u, v): G.get_edge_data(u, v) for u, v in G.edges})
               self.add(g)

    """

    def __init__(
        self,
        *args: Any,
        weight: str | int | float | None = None,
        weight_config: dict | None = None,
        weight_alpha: float = 0.5,
        bg_config: dict | None = None,
        add_bg: bool = True,
        **kwargs: Any,
    ):
        self.weight = weight
        self.alpha = weight_alpha
        self.add_bg = add_bg
        super().__init__(*args, **kwargs)

        self.weight_config = {
            "color": WHITE,
            "slant": ITALIC,
            "font_size": DEFAULT_FONT_SIZE * 0.5,
        }

        if weight_config:
            self.weight_config.update(weight_config)

        self.bg_config = {
            "color": config.background_color,
            "opacity": 1,
        }
        if bg_config:
            self.bg_config.update(bg_config)

        if self.weight is not None:
            self._add_weight()

    def _add_weight(self):
        """
        Clears any current weight and then displays the weight is not none.

        Use weight_config dict to send options to the Text object.

        Use bg_config dict to send options to the background Rectangle object.

        """

        # Set the new weight if it is present

        point = self.point_from_proportion(self.alpha)
        label = Text(str(self.weight), **self.weight_config)
        label.move_to(point)

        if self.add_bg:
            label.add_background_rectangle(**self.bg_config)
            label.background_rectangle.height += SMALL_BUFF

        self.add(label)