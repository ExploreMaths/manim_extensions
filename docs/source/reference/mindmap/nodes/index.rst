.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

nodes
=====

.. module:: manim_extensions.mindmap.nodes

Usage
-----

Nodes hold the label, border, and connector used by a mind map.

.. code-block:: python

   from manim import *
   from manim_extensions.mindmap.nodes import Node

   root = Node(Text("Root"))
   root.add_child(Node(Text("Child")))

Modules
-------

.. autosummary::
   :nosignatures:

   ~node

.. toctree::
   :hidden:
   :maxdepth: 1

   node
