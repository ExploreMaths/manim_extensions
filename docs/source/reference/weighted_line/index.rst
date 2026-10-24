.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Weighted Line
=============

.. vendored-status:: mutable-learning/manim-weighted-line

**Original author:** `Mutable Learning <https://github.com/mutable-learning>`_

**Source repository:** `GitHub <https://github.com/mutable-learning/manim-weighted-line>`_

**License:** MIT

``manim-weighted-line`` provides a :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine` mobject — a
:class:`~manim.mobject.geometry.line.Line` subclass that displays a
weight label at its midpoint with an optional background rectangle. Useful
for graph-theory and network-flow visualisations. Manim has no easy way to
put weightings on graph edges, so this plugin fills that gap for both
undirected and directed graphs.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.weighted_line`` subpackage.

Features
--------

- :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine` – a
  line with an attached weight label and background.
- Drop-in edge type for both undirected
  :class:`~manim.mobject.graph.Graph` and directed
  :class:`~manim.mobject.graph.DiGraph` scenes.
- Configurable weight label (``weight_config``) and background rectangle
  (``bg_config`` / ``add_bg``), with the label placed at ``weight_alpha``
  along the edge.

Usage
-----

After importing, construct a :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine`
between two points and pass it a ``weight`` to label:

.. manim:: SimpleExample
   :ref_classes: WeightedLine
   :save_last_frame:

   from manim import *
   from manim_extensions.weighted_line import WeightedLine


   class SimpleExample(Scene):
       def construct(self):
           weighted_line = WeightedLine(
               0,
               1,
               weight=4,
           )
           self.add(weighted_line)

To use the line in a graph, pass the configuration to the edge object and
use :class:`~manim_extensions.weighted_line.weighted_line.WeightedLine` as
the ``edge_type``. Per-edge options (including ``weight`` and
``stroke_color``) go in the ``edge_config`` dictionary keyed by edge:

.. manim:: WeightedGraph
   :ref_classes: WeightedLine
   :save_last_frame:

   from manim import *
   from manim_extensions.weighted_line import WeightedLine


   class WeightedGraph(Scene):
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

If you build your graph with NetworkX, use
:class:`~manim_extensions.weighted_line.weighted_line.WeightedLine` as the
``edge_type`` and pass the edge data through the ``edge_config`` dictionary:

.. manim:: NetworkXGraph
   :ref_classes: WeightedLine
   :save_last_frame:

   from manim import *
   from manim_extensions.weighted_line import WeightedLine
   import networkx as nx


   class NetworkXGraph(Scene):
       def construct(self):
           G = nx.Graph()
           G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8])
           G.add_weighted_edges_from([(1, 7, 2), (1, 8, 3), (2, 3, 4), (2, 4, 5), (2, 5, 6),
                                      (2, 8, 1), (3, 4, 5), (6, 1, 0), (6, 2, 11),
                                      (6, 3, 15), (7, 2, 3), (7, 4, 9)])
           g = Graph(G.nodes, G.edges, layout="circular", layout_scale=3,
                     labels=True, vertex_config={7: {"fill_color": RED}},
                     edge_type=WeightedLine,
                     edge_config={(u, v): G.get_edge_data(u, v) for u, v in G.edges})
           self.add(g)

Parameters
^^^^^^^^^^

- ``weight`` – the weight of the edge to display.
- ``weight_config`` – a dict of options forwarded to the ``Text`` label
  (defaults to a half-size italic white label).
- ``weight_alpha`` – position along the edge at which to show the weight,
  as a proportion between 0 and 1 (default ``0.5``, the midpoint).
- ``bg_config`` – a dict of options forwarded to the background rectangle.
- ``add_bg`` – whether to draw a background rectangle behind the weight
  label (default ``True``).

The upstream ``examples/`` folder contains more scenes using the plugin with
different undirected and directed graphs, showing how to configure the weight
label and its background.

.. toctree::
   :hidden:
   :maxdepth: 1

   classes
