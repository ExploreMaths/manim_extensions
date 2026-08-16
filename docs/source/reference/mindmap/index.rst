MindMap
=======

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

Quick start
-----------

Import directly from ``manim_extensions`` (``from manim_extensions.mindmap import *``).

Inserting nodes into a mind map
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. manim:: MindMapInsertExample

   from manim import *
   from manim_extensions.mindmap import Node, InsertNode

   class MindMapInsertExample(Scene):
       def construct(self):
           root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
           a1 = Node(MathTex(r"\text{A1}", font_size=36))
           a2 = Node(MathTex(r"\text{A2}", font_size=36))
           a3 = Node(MathTex(r"\text{A3}", font_size=36))

           self.play(
               InsertNode(self, {root: [a1, a2, a3]}),
               run_time=2,
           )

Building a tree with :class:`~manim_extensions.mindmap.animations.animations.LayoutAnimation`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. manim:: LayoutAnimationExample

   from manim import *
   from manim_extensions.mindmap import Node, LayoutAnimation

   class LayoutAnimationExample(Scene):
       def construct(self):
           root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
           a1 = Node(MathTex(r"\text{A1}", font_size=36))
           a2 = Node(MathTex(r"\text{A2}", font_size=36))
           a21 = Node(MathTex(r"\text{A2-1}", font_size=36))
           a22 = Node(MathTex(r"\text{A2-2}", font_size=36))

           root.add_child(a1)
           root.add_child(a2)
           a2.add_child(a21)
           a2.add_child(a22)

           self.play(LayoutAnimation(self, root))

Layout types
^^^^^^^^^^^^

The ``layout_type`` argument of the animation classes accepts:

- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap` – default mind-map layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.Standard` – left/right or top/bottom two-sided layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.TimeLine` – timeline layout.
- :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.Catalog` – top-down catalog / directory layout.

.. toctree::
   :hidden:

   nodes
   maps
   animations
   layout

See the `original README <https://github.com/jj-math/manim-mindmap/blob/main/README.md>`_
for full animated demos and the complete API.