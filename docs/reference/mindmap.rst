manim-mindmap
=============

**Original author:** `jj-math <https://github.com/jj-math>`_ (B站博主“**究尽数学**”)

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

.. code-block:: python

   class MindMapInsertExample(Scene):
       def construct(self):
           self.camera.frame.set_width(25).move_to(RIGHT)

           root = Node(Tex("Root").to_edge(LEFT))
           a1 = Node(Tex("A1"))
           a2 = Node(Tex("A2"))
           a3 = Node(Tex("A3"))

           self.play(
               InsertNode(self, {root: [a1, a2, a3]}),
               run_time=2,
           )

Building a tree with ``LayoutAnimation``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class LayoutAnimationExample(Scene):
       def construct(self):
           self.camera.frame.set_width(25).move_to(RIGHT)

           root = Node(Tex("Root").to_edge(LEFT))
           a1 = Node(Tex("A1"))
           a2 = Node(Tex("A2"))
           a21 = Node(Tex("A2-1"))
           a22 = Node(Tex("A2-2"))

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

API reference
-------------

Nodes
^^^^^

.. autoclass:: manim_extensions.mindmap.Node
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.NodeStyle
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autofunction:: manim_extensions.mindmap.bfs_walker
.. autofunction:: manim_extensions.mindmap.dfs_walker

Mind maps
^^^^^^^^^

.. autoclass:: manim_extensions.mindmap.MindMap
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.StandardMap
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.CatalogMap
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.TimeLine
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Animations
^^^^^^^^^^

.. autoclass:: manim_extensions.mindmap.LayoutAnimation
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.InsertNode
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.RemoveNode
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.AlterNode
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.ScaleNode
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Layout
^^^^^^

.. autoclass:: manim_extensions.mindmap.LayoutConfig
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.LayoutType
   :members:
   :undoc-members:
   :show-inheritance:

See the `original README <https://github.com/jj-math/manim-mindmap/blob/main/README.md>`_
for full animated demos and the complete API.
