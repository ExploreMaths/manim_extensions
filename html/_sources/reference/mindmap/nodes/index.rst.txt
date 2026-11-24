.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

nodes
=====

.. module:: manim_extensions.mindmap.nodes

Usage
-----

Each node holds the label, border, and connector used by a mind map.

.. manim:: NodeTree
   :save_last_frame:
   :ref_classes: Node

   from manim import *
   from manim_extensions.mindmap import Node
   from manim_extensions.mindmap.algorithms import LayoutType

   class NodeTree(Scene):
       def construct(self):
           root = Node(MathTex(r"\text{Root}", font_size=36), color=BLUE)
           child = Node(MathTex(r"\text{Child}", font_size=36), color=GREEN)
           leaf = Node(MathTex(r"\text{Leaf}", font_size=36), color=YELLOW)
           root.add_child(child)
           child.add_child(leaf)
           for node, pos in [(root, LEFT * 3), (child, ORIGIN), (leaf, RIGHT * 3)]:
               node.vmobject.move_to(pos)
               node.surr_rect.move_to(pos)
           connectors = Group(
               child.get_connector(LayoutType.MindMap, RIGHT, color=GREY),
               leaf.get_connector(LayoutType.MindMap, RIGHT, color=GREY),
           )
           self.add(connectors, root.vmobject, root.surr_rect,
                    child.vmobject, child.surr_rect, leaf.vmobject, leaf.surr_rect)
           Group(*self.mobjects).scale(1.3).move_to(ORIGIN)

Modules
-------

.. autosummary::
   :nosignatures:

   ~node

.. toctree::
   :hidden:
   :maxdepth: 1

   node
