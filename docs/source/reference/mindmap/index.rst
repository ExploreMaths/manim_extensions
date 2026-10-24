.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

MindMap
=======

.. vendored-status:: jj-math/manim-mindmap

**Original author:** `jj-math <https://github.com/jj-math>`_ (Bilibili creator **Jiujin Math**)

**Source repository:** `GitHub <https://github.com/jj-math/manim-mindmap>`_

**License:** MIT (see the upstream repository for the full license text)

:attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap` brings mind-map, timeline, and catalog / organisation-chart
diagrams to Manim. It is bundled inside ``manim_extensions`` as the
``manim_extensions.mindmap`` subpackage.

Features
--------

- :class:`~manim_extensions.mindmap.nodes.node.Node` – the basic tree-node class.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap` / :class:`~manim_extensions.mindmap.mindmap.mindmap.StandardMap` – mind-map classes with multiple layout directions.
- :class:`~manim_extensions.mindmap.mindmap.mindmap.CatalogMap` – organisation / directory-structure diagrams.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.TimeLine` – timeline diagrams.
- Animation helpers: :class:`~manim_extensions.mindmap.animations.animations.LayoutAnimation`, :class:`~manim_extensions.mindmap.animations.animations.InsertNode`, :class:`~manim_extensions.mindmap.animations.animations.RemoveNode`,
  :class:`~manim_extensions.mindmap.animations.animations.ScaleNode`, :class:`~manim_extensions.mindmap.animations.animations.AlterNode`.
- Styling / layout options: :class:`~manim_extensions.mindmap.nodes.node.NodeStyle`, :class:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType`, :class:`~manim_extensions.mindmap.algorithms.layout_config.LayoutConfig`.

Layout types
^^^^^^^^^^^^

The ``layout_type`` argument of the animation classes accepts:

- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap` – default mind-map layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.Standard` – left/right or top/bottom two-sided layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.TimeLine` – timeline layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.Catalog` – top-down catalog / directory layout.

Usage
-----

Upstream shipped ``manim-mindmap`` on PyPI; here it is bundled inside
``manim_extensions.mindmap``. The layout engine is a linear-time tidy-tree
implementation of Walker's algorithm, kept fully separate from the node
mobjects so the animation layer can be customised.

Build the tree out of :class:`~manim_extensions.mindmap.nodes.node.Node`
objects and animate changes with the animation classes. Every animation takes
the scene as its first argument and a dictionary mapping parent nodes to the
nodes to insert:

.. manim:: MindMapExample
   :ref_classes: ~manim_extensions.mindmap.nodes.node.Node ~manim_extensions.mindmap.animations.animations.InsertNode

   from manim import *
   from manim_extensions.mindmap import Node, InsertNode

   class MindMapExample(Scene):
       def construct(self):
           root = Node(Tex("Volume of a sphere").to_edge(LEFT))

           a1 = Node(Tex("3rd century BC"))
           a2 = Node(Tex("3rd century AD"))
           a3 = Node(Tex("5th century AD"))

           # create the first level
           self.play(InsertNode(self, {root: [a1, a2, a3]}), run_time=2)
           self.wait()

           # attach further children under a parent node
           self.play(InsertNode(self, {a1: [Node(Tex("Archimedes"))]}))
           self.wait()

The four concrete animations
(:class:`~manim_extensions.mindmap.animations.animations.InsertNode`,
:class:`~manim_extensions.mindmap.animations.animations.RemoveNode`,
:class:`~manim_extensions.mindmap.animations.animations.ScaleNode`,
:class:`~manim_extensions.mindmap.animations.animations.AlterNode`) all
inherit from
:class:`~manim_extensions.mindmap.animations.animations.LayoutAnimation`.

.. warning::

   The four concrete animations operate on the same mind map and cannot be
   combined inside a single ``self.play(...)`` on the same tree. To perform
   several changes at once, mutate the nodes and replay the layout through
   :class:`~manim_extensions.mindmap.animations.animations.LayoutAnimation`.

Node operations
^^^^^^^^^^^^^^^

Mutate the tree directly on the :class:`~manim_extensions.mindmap.nodes.node.Node`
objects and then re-layout. Nodes support
:meth:`~manim_extensions.mindmap.nodes.node.Node.add_child`,
:meth:`~manim_extensions.mindmap.nodes.node.Node.remove_child`, a ``scale``
method and
:meth:`~manim_extensions.mindmap.nodes.node.Node.alter_content`:

.. code-block:: python

   root.add_child(a1)
   a1.scale(1.5)
   root.alter_content(Tex(r"Volume of sphere"))

   # collect and play all layout animations after the mutations
   self.play(LayoutAnimation(self, root))
   self.wait()

Removal
^^^^^^^

:class:`~manim_extensions.mindmap.animations.animations.RemoveNode` takes a
single node or a list of nodes. Removing a node removes the whole subtree
rooted at it, so removing the root clears the entire mind map:

.. code-block:: python

   self.play(RemoveNode(self, [a1, a3]))
   self.play(RemoveNode(self, root))

Styling
^^^^^^^

:class:`~manim_extensions.mindmap.nodes.node.NodeStyle` takes parallel
``node_style`` and ``line_style`` lists of dictionaries (one per depth level),
each giving a Manim color and stroke settings. Pass it as ``node_style=`` to any
animation; changing the style is itself animated:

.. code-block:: python

   node_style = NodeStyle(
       node_style=[
           {"color": RED, "stroke_width": 20, "stroke_opacity": 0.5},
           {"color": YELLOW, "stroke_width": 12, "stroke_opacity": 0.5},
       ],
       line_style=[
           {"color": RED, "stroke_width": 20, "stroke_opacity": 0.5},
           {"color": YELLOW, "stroke_width": 12, "stroke_opacity": 0.5},
       ],
   )
   self.play(ScaleNode(self, {a1: 1.5}, node_style=node_style))

The map classes
^^^^^^^^^^^^^^^

Instead of assembling nodes by hand, pass a nested data structure (a ``"node"``
entry plus a ``"child"`` list) to
:class:`~manim_extensions.mindmap.mindmap.mindmap.MindMap`. The same data
drives :class:`~manim_extensions.mindmap.mindmap.mindmap.StandardMap`,
:class:`~manim_extensions.mindmap.mindmap.mindmap.TimeLine` and
:class:`~manim_extensions.mindmap.mindmap.mindmap.CatalogMap` (the last lays
out top-down only). Walk the resulting tree with
:meth:`~manim_extensions.mindmap.mindmap.base.AbstractMap.dfs_walker`, and select
subtrees with
:meth:`~manim_extensions.mindmap.mindmap.base.AbstractMap.get_children` /
:meth:`~manim_extensions.mindmap.mindmap.base.AbstractMap.get_descendants`,
which take an ``ID`` tuple — ``(0,)`` is the root, ``(0, 1)`` its second child:

.. code-block:: python

   data = {
       "node": "Volume of a sphere",
       "child": [
           {"node": "3rd century BC"},
           {"node": "3rd century AD", "child": [{"node": "Nine Chapters"}]},
       ],
   }
   mind = MindMap(data)
   for node in mind.dfs_walker():
       self.add(node.vmobject)

   descendants = mind.get_descendants(ID=(0, 1))

Layout configuration
^^^^^^^^^^^^^^^^^^^^

Pass a :class:`~manim_extensions.mindmap.algorithms.layout_config.LayoutConfig`
as ``layout_config=`` to choose spacing and direction. Its parameters are
``direction`` (RIGHT/LEFT/UP/DOWN, default RIGHT), ``node_spacing`` (distance
between nodes, default 0.5), ``level_spacing`` (distance between depth levels,
default 0.5) and ``sides`` (allowed growth directions for the timeline
layout — UP, DOWN, or a tuple, default ``(UP, DOWN)``). Choose the layout
algorithm itself with the ``layout_type`` argument of any animation (see
"Layout types" above):

.. code-block:: python

   self.play(
       LayoutAnimation(
           self,
           root,
           layout_type=LayoutType.TimeLine,
           layout_config=LayoutConfig(node_spacing=0.5, level_spacing=0.5),
           node_style=node_style,
       )
   )

.. toctree::
   :hidden:
   :maxdepth: 1

   nodes
   maps
   animations
   layout
   classes
   functions
   constants

See the `original README <https://github.com/jj-math/manim-mindmap>`_
for full animated demos and the complete API.
