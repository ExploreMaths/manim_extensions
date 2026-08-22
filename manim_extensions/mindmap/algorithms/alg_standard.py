# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


__all__ = [
    "StandardLayout",
]
from typing import List, Any
from collections import deque
from .alg_tidy_tree import TidyTreeLayout
from .layout_config import LayoutDirection
from .layout import Layout


class TreeNode:
    """Internal tree-node wrapper used by StandardLayout.

    Parameters
    ----------
    height : float, optional
        Height of the tree node. Defaults to ``0``.
    width : float, optional
        Width of the tree node. Defaults to ``0``.

    Examples
    --------
    .. manim:: TreeNodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.alg_standard import TreeNode

       class TreeNodeExample(Scene):
           def construct(self):
               tn = TreeNode(height=1.0, width=2.0)
               label = Text(f"TreeNode: {tn.width}x{tn.height}", font_size=24)
               self.add(label)
    """

    __slots__ = ("height", "width", "children", "parent", "x", "y", "level", "is_flip")

    def __init__(
        self,
        height: float = 0,
        width: float = 0,
    ):
        """Initialize the TreeNode instance."""
        self.width = width
        self.height = height
        self.x: float = 0
        self.y: float = 0
        self.level: int = 0
        self.is_flip: bool = False
        self.children: List["TreeNode"] = []
        self.parent: "TreeNode" = None

    def add_child(self, child: "TreeNode"):
        """Add a child node and establish the parent-child relationship.

        Parameters
        ----------
        child : TreeNode
            The child node to add.
        """
        self.children.append(child)
        child.parent = self


def copy_node(node: Any) -> "TreeNode":
    """Recursively create a deep copy of a node tree.

    Parameters
    ----------
    node : Any
        The source node (must expose ``height``, ``width``, and
        ``children`` attributes).

    Returns
    -------
    TreeNode
        The root of the copied tree, or ``None`` if *node* is ``None``.
    """

    if node is None:
        return None
    root = TreeNode(node.height, node.width)
    for child in node.children:
        root.add_child(copy_node(child))
    return root


def split_integer(n: int):
    """Split an integer into two roughly equal parts.

    Parameters
    ----------
    n : int
        The integer to split.

    Returns
    -------
    tuple of (int, int)
        The two parts ``(k + 1, k)`` if *n* is odd, or ``(k, k)`` if *n* is even.
    """

    if n & 1:
        k = (n - 1) // 2
        return k + 1, k
    k = n // 2
    return k, k


def sync_copy_bfs(src: TreeNode, dst: Any):
    """
    Synchronously traverse two trees and copy data from src to dst.

    Parameters
    ----------
    src
        Source tree (data provider)
    dst
        Destination tree (data receiver)


    """
    queue = deque([(src, dst)])

    while queue:
        s_node, d_node = queue.popleft()

        if s_node is None and d_node is None:
            continue
        if s_node is None or d_node is None:
            raise ValueError("Tree structures do not match")
        if len(s_node.children) != len(d_node.children):
            raise ValueError("Child node counts do not match")

        # Copy data
        d_node.x = s_node.x
        d_node.y = s_node.y
        d_node.level = s_node.level
        d_node.is_flip = s_node.is_flip

        # Synchronously enqueue children
        for s_child, d_child in zip(s_node.children, d_node.children):
            queue.append((s_child, d_child))


class StandardLayout(Layout):
    """Two-sided mind-map layout algorithm: split children into left/right (or top/bottom) sides.

    Parameters
    ----------
    root : Any
        Root node of the tree to lay out.
    direction : LayoutDirection, optional
        Primary layout direction. Defaults to :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutDirection.LeftToRight`.
    node_spacing : float, optional
        Spacing between sibling nodes. Defaults to ``0.5``.
    level_spacing : float, optional
        Spacing between tree levels. Defaults to ``0.5``.

    Examples
    --------
    .. manim:: StandardLayoutExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.alg_standard import StandardLayout

       class StandardLayoutExample(Scene):
           def construct(self):
               label = Text("StandardLayout algorithm", font_size=24)
               self.add(label)
    """

    def __init__(
        self,
        root: Any,
        direction: LayoutDirection = LayoutDirection.LeftToRight,
        node_spacing: float = 0.5,
        level_spacing: float = 0.5,
    ):
        """Initialize the StandardLayout instance."""
        self.root = root
        self.direction = direction
        self.flip_direction = self._flip_direction(direction)
        self.node_spacing = node_spacing
        self.level_spacing = level_spacing

    def _flip_direction(self, direction: LayoutDirection) -> LayoutDirection:
        """Return the opposite of the given direction.

        Parameters
        ----------
        direction : LayoutDirection
            The direction to flip.

        Returns
        -------
        LayoutDirection
            The opposite direction.
        """
        match direction:
            case LayoutDirection.LeftToRight:
                return LayoutDirection.RightToLeft
            case LayoutDirection.RightToLeft:
                return LayoutDirection.LeftToRight
            case LayoutDirection.TopToBottom:
                return LayoutDirection.BottomToTop
            case LayoutDirection.BottomToTop:
                return LayoutDirection.TopToBottom

    def _split(self):
        """Split the root's children into left/right (or top/bottom) parts."""
        self.left = TreeNode(self.root.height, self.root.width)
        if (number := len(self.root.children)) > 0:
            m, n = split_integer(number)
            children = [copy_node(child) for child in self.root.children]
            for child in children[0:m]:
                self.left.add_child(child)
            self.right = None
            if n > 0:
                self.right = TreeNode(self.root.height, self.root.width)
                for child in children[m::]:
                    self.right.add_child(child)

    def layout(self):
        """Run the two-sided layout and return the original root node."""
        self._split()
        self.left = TidyTreeLayout(
            self.left, self.direction, self.node_spacing, self.level_spacing
        ).layout()
        if self.right is not None:
            self.right = TidyTreeLayout(
                self.right, self.flip_direction, self.node_spacing, self.level_spacing
            ).layout()
            x = self.left.x - self.right.x
            y = self.left.y - self.right.y
            self._offset(self.right, x, y)
            self._merge()
        sync_copy_bfs(self.left, self.root)
        return self.root

    def _offset(self, node: Any, x: float, y: float):
        """Translate a subtree by *(x, y)* and mark it as flipped.

        Parameters
        ----------
        node : Any
            The root of the subtree to translate.
        x : float
            Horizontal offset.
        y : float
            Vertical offset.
        """
        node.x += x
        node.y += y
        node.is_flip = True
        for child in node.children:
            self._offset(child, x, y)

    def _merge(self):
        """Merge the right (or bottom) subtree into the left tree."""
        for child in self.right.children:
            self.left.add_child(child)
