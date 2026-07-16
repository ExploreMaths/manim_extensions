manim-mindmap
=============

**Original author:** `jj-math <https://github.com/jj-math>`_ (B站博主“**究尽数学**”)

**Source repository:** https://github.com/jj-math/manim-mindmap

This plugin brings mind-map, timeline, and catalog diagrams to Manim. It is
included in this repository as a Git submodule for reference and easy access.

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install manim-mindmap

Then import it in your Manim scene:

.. code-block:: python

   from manim_mindmap import *

Main classes
------------

- ``Node`` – the basic node class.
- ``MindMap`` / ``StandardMap`` – mind-map classes with several layout directions.
- ``CatalogMap`` – organisation / directory-structure diagrams.
- ``TimeLine`` – timeline diagrams.
- ``LayoutAnimation``, ``InsertNode``, ``RemoveNode``, ``ScaleNode``, ``AlterNode`` – layout and animation helpers.
- ``NodeStyle``, ``LayoutType``, ``LayoutConfig`` – styling and layout options.

Example: inserting nodes into a mind map
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class MindMapInsertExample(Scene):
       def construct(self):
           self.camera.frame.set_width(25).move_to(RIGHT)

           root = Node(Tex("球体积").to_edge(LEFT))
           a1 = Node(Tex("公元前3世纪"))
           a2 = Node(Tex("公元3世纪"))
           a3 = Node(Tex("公元5世纪"))
           a4 = Node(Tex("公元17世纪"))
           a5 = Node(Tex("公元18世纪"))

           self.play(
               InsertNode(self, {root: [a1, a2, a3, a4, a5]}),
               run_time=2,
           )

Example: building a tree with ``LayoutAnimation``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class LayoutAnimationExample(Scene):
       def construct(self):
           self.camera.frame.set_width(25).move_to(RIGHT)

           root = Node(Tex("球体积").to_edge(LEFT))
           a1 = Node(Tex("公元前3世纪"))
           a2 = Node(Tex("公元3世纪"))
           a3 = Node(Tex("公元5世纪"))

           for a in [a1, a2, a3]:
               root.add_child(a)

           a21 = Node(Tex("《九章算术》"))
           a22 = Node(Tex("刘徽：牟合方盖"))
           a2.add_child(a21)
           a2.add_child(a22)

           self.play(LayoutAnimation(self, root))

For the full API, layout types, and animated demos, see the
`original README <https://github.com/jj-math/manim-mindmap/blob/main/README.md>`_.
