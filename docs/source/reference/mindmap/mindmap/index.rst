.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

mindmap
=======

.. module:: manim_extensions.mindmap.mindmap

Classes
-------

.. autosummary::
   :nosignatures:

   ~mindmap.CatalogMap
   ~mindmap.MindMap
   ~mindmap.StandardMap
   ~mindmap.TimeLine

Usage
-----

Build a mind map from a nested dictionary, then reveal nodes and connectors.

.. manim:: MindMapScene
   :ref_classes: MindMap

   from manim import *
   from manim_extensions.mindmap import MindMap

   data = {
       "node": MathTex(r"\text{Calculus}"),
       "child": [
           {"node": MathTex(r"\text{Limits}")},
           {"node": MathTex(r"\text{Derivatives}")},
       ],
   }

   class MindMapScene(Scene):
       def construct(self):
           mind_map = MindMap(data)
           for node in mind_map.dfs_walker():
               if node.connector:
                   self.play(Create(node.connector), run_time=0.3)
               self.play(Create(node.surr_rect), Write(node.vmobject), run_time=0.3)
           self.wait()

Modules
-------

.. autosummary::
   :nosignatures:

   ~base
   ~mindmap

.. toctree::
   :hidden:
   :maxdepth: 1

   base
   mindmap
