# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Layout base class for mindmap algorithms.

This module provides base class for layout algorithms.

"""

__all__ = ["Layout"]
from typing import Any


class Layout:
    """Base class for layout algorithms.

    Examples
    --------
    .. manim:: LayoutExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import Node, bfs_walker
       from manim_extensions.mindmap.algorithms.layout import Layout

       class LayoutExample(Scene):
           def construct(self):
               class HorizontalLayout(Layout):
                   def __init__(self, root):
                       self.root = root

                   def layout(self):
                       for i, node in enumerate(bfs_walker(self.root)):
                           node.x, node.y = 2.5 * i - 2.5, 0
                       return self.root

               root = Node(Text("Root", font_size=32), color=WHITE)
               root.add_child(Node(Text("A", font_size=32), color=BLUE))
               root.add_child(Node(Text("B", font_size=32), color=GREEN))
               root = HorizontalLayout(root).layout()
               mobjects = Group()
               for node in bfs_walker(root):
                   node.vmobject.move_to([node.x, node.y, 0])
                   node.surr_rect.move_to([node.x, node.y, 0])
                   mobjects.add(node.vmobject, node.surr_rect)
               self.add(mobjects)
    """

    def layout(self) -> Any:
        """Run the layout computation and return the root node."""
        raise NotImplementedError