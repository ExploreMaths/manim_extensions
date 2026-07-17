manim-mindmap
=============

**Original author:** `jj-math <https://github.com/jj-math>`_ (Bilibili creator **Jiujin Math**)

**Source repository:** https://github.com/jj-math/manim-mindmap

**License:** MIT (see the upstream repository for the full license text)

``manim-mindmap`` brings mind-map, timeline, and catalog / organisation-chart
diagrams to Manim. It is bundled inside ``manim_extensions`` as the
``manim_extensions.mindmap`` subpackage and is also kept as a Git submodule
under ``third_party/manim-mindmap``.

Features
--------

- ``Node`` – the basic tree-node class.
- ``MindMap`` / ``StandardMap`` – mind-map classes with multiple layout directions.
- ``CatalogMap`` – organisation / directory-structure diagrams.
- ``TimeLine`` – timeline diagrams.
- Animation helpers: ``LayoutAnimation``, ``InsertNode``, ``RemoveNode``,
  ``ScaleNode``, ``AlterNode``.
- Styling / layout options: ``NodeStyle``, ``LayoutType``, ``LayoutConfig``.

Quick start
-----------

Import directly from ``manim_extensions``:

.. code-block:: python

   from manim import *
   from manim_extensions.mindmap import *

Inserting nodes into a mind map
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. manim:: MindMapInsertExample

   from manim import *
   from manim_extensions.mindmap import Node, InsertNode

   class MindMapInsertExample(Scene):
       def construct(self):
           root = Node(MathTex("Root", font_size=36).to_edge(LEFT))
           a1 = Node(MathTex("A1", font_size=36))
           a2 = Node(MathTex("A2", font_size=36))
           a3 = Node(MathTex("A3", font_size=36))

           self.play(
               InsertNode(self, {root: [a1, a2, a3]}),
               run_time=2,
           )

Building a tree with ``LayoutAnimation``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. manim:: LayoutAnimationExample

   from manim import *
   from manim_extensions.mindmap import Node, LayoutAnimation

   class LayoutAnimationExample(Scene):
       def construct(self):
           root = Node(MathTex("Root", font_size=36).to_edge(LEFT))
           a1 = Node(MathTex("A1", font_size=36))
           a2 = Node(MathTex("A2", font_size=36))
           a21 = Node(MathTex("A2-1", font_size=36))
           a22 = Node(MathTex("A2-2", font_size=36))

           root.add_child(a1)
           root.add_child(a2)
           a2.add_child(a21)
           a2.add_child(a22)

           self.play(LayoutAnimation(self, root))

Layout types
^^^^^^^^^^^^

The ``layout_type`` argument of the animation classes accepts:

- ``LayoutType.MindMap`` – default mind-map layout.
- ``LayoutType.Standard`` – left/right or top/bottom two-sided layout.
- ``LayoutType.TimeLine`` – timeline layout.
- ``LayoutType.Catalog`` – top-down catalog / directory layout.

.. toctree::
   :hidden:

   nodes
   maps
   animations
   layout

See the `original README <https://github.com/jj-math/manim-mindmap/blob/main/README.md>`_
for full animated demos and the complete API.
