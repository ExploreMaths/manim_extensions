# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Algorithm visualisation helpers.

This package provides structural helpers for visualising algorithmic concepts,
including nodes, arrays, queues, and code-like blocks in Manim scenes.

Examples
--------
.. manim:: AlgorithmPackageDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions.algorithm import Node, Array

   class AlgorithmPackageDocExample(Scene):
       def construct(self):
           title = Text("Algorithm primitives", font_size=28).to_edge(UP)
           nodes = VGroup(
               Node("1"),
               Node("2"),
               Node("3"),
           ).arrange(RIGHT, buff=0.5).next_to(title, DOWN, buff=1)
           arr = Array([10, 20, 30, 40], total_width=8).next_to(nodes, DOWN, buff=1)
           self.add(title, nodes, arr)
"""

from .node import *
from .array import *
from .code import *
from .queue import *