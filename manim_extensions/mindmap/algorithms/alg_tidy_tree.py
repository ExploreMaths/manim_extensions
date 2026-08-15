"""
Non-layered Tidy Tree Layout Algorithm (Python Implementation)
Used to compute node positions for tree structures.

Algorithm reference: "Improving Walker's Algorithm to Run in Linear Time"
"""
__all__ = [
    'TidyTreeLayout'
]
from dataclasses import dataclass, field
from typing import List, Optional, Any
from .layout_config import LayoutDirection
from .layout import Layout

@dataclass
class WrappedTree:
    """Wrapper tree node used during layout computation.

    Examples
    --------
    .. manim:: WrappedTreeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.alg_tidy_tree import WrappedTree

       class WrappedTreeExample(Scene):
           def construct(self):
               wt = WrappedTree()
               label = Text(f"WrappedTree: x={wt.x}, y={wt.y}", font_size=24)
               self.add(label)
"""
    # Reference to the original node
    node: Any = None
    # Basic attributes
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    level: int = 0  # node depth
    # Children
    children: List['WrappedTree'] = field(default_factory=list)
    child_number: int = 0

    # === Core layout attributes ===
    prelim: float = 0.0  # preliminary position of the node relative to its parent, before overlap correction
    mod: float = 0.0     # extra shift to apply to the whole subtree rooted at this node
    shift: float = 0.0   # spacing share to distribute over subsequent sibling subtrees
    change: float = 0.0  # one-time correction at the end of a distribution chain to eliminate accumulated error

    # === Subtree contour tracking for overlap detection ===
    extreme_left: Optional['WrappedTree'] = None  # leftmost extreme node
    extreme_right: Optional['WrappedTree'] = None  # rightmost extreme node
    mod_sum_extreme_left: float = 0.0   # sum of mod values along the path from leftmost extreme to root
    mod_sum_extreme_right: float = 0.0  # sum of mod values along the path from rightmost extreme to root

    # Threads for contour traversal: when two subtrees have different heights,
    # the shorter subtree links to a neighbouring subtree's contour when exhausted
    thread_left: Optional['WrappedTree'] = None
    thread_right: Optional['WrappedTree'] = None

    @classmethod
    def from_node(cls, node, is_horizontal: bool, level: int = 0) -> 'WrappedTree':
        """Create a :class:`WrappedTree` wrapper tree from the original node.

        Recursively copies dimensions and child references.  When
        *is_horizontal* is ``True``, width/height and x/y are swapped so that
        the layout algorithm always works in the vertical orientation.

        Parameters
        ----------
        node
            The source node (must expose ``width``, ``height``, and
            ``children`` attributes).
        is_horizontal : bool
            Whether the layout direction is horizontal (swaps width/height).
        level : int
            The starting depth level (root is 0).

        Returns
        -------
        WrappedTree
            The root of the newly created wrapper tree.
        """
        wt = cls()
        wt.node = node
        wt.level = level
        level += 1
        # Copy dimensions
        if is_horizontal:
            wt.width = getattr(node, 'height', 0)
            wt.height = getattr(node, 'width', 0)
            wt.x = getattr(node, 'x', 0)
        else:
            wt.width = getattr(node, 'width', 0)
            wt.height = getattr(node, 'height', 0)
            wt.y = getattr(node, 'y', 0)

        # Recursively create children
        children = getattr(node, 'children', [])
        wt.children = [cls.from_node(child, is_horizontal, level) for child in children]
        wt.child_number = len(wt.children)
        return wt

@dataclass
class IYLNode:
    """Lowest contour line in the separate function:
    To avoid comparing the i-th subtree with each of the previous i-1 subtrees one by one,
    a monotonically-clipped linked list is used for efficiency!
    Subtrees pruned by IYLNode are completely hidden by a taller, more-rightward intermediate subtree,
    so the current subtree can never collide with them first.

    Examples
    --------
    .. manim:: IYLNodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.alg_tidy_tree import IYLNode

       class IYLNodeExample(Scene):
           def construct(self):
               iyl = IYLNode(low=0.0, index=0)
               label = Text(f"IYLNode: low={iyl.low}, idx={iyl.index}", font_size=24)
               self.add(label)
"""
    low: float                       # low end of the subtree's right contour in the orthogonal direction
    index: int                       # index of the subtree among its siblings
    nxt: Optional['IYLNode'] = None  # next node in the list (with a strictly larger low value)

def move_right(node, move: float, is_horizontal: bool):
    """Move a node and all its descendants by *move* in the non-layered direction.

    Parameters
    ----------
    node : WrappedTree
        The subtree root.
    move : float
        The offset to apply.
    is_horizontal : bool
        If ``True``, shifts ``y``; otherwise shifts ``x``.
    """
    if is_horizontal:
        node.y += move
    else:
        node.x += move
    for child in node.children:
        move_right(child, move, is_horizontal)

def get_min(node, is_horizontal: bool) -> float:
    """Return the minimum non-layered coordinate in a subtree.

    Parameters
    ----------
    node : WrappedTree
        The subtree root.
    is_horizontal : bool
        If ``True``, inspects ``y``; otherwise inspects ``x``.

    Returns
    -------
    float
        The minimum coordinate value.
    """
    res = node.y if is_horizontal else node.x
    for child in node.children:
        res = min(get_min(child, is_horizontal), res)
    return res

def normalize(node, is_horizontal: bool):
    """Shift the subtree so that its minimum non-layered coordinate is 0.

    Parameters
    ----------
    node : WrappedTree
        The subtree root.
    is_horizontal : bool
        Whether the layout is horizontal.
    """
    min_val = get_min(node, is_horizontal)
    move_right(node, -min_val, is_horizontal)

def convert_back(converted: WrappedTree, root, is_horizontal: bool):
    """Write computed coordinates back to the original node tree.

    Copies :attr:`WrappedTree.x` to the original node's ``x`` or ``y``
    (depending on *is_horizontal*) and recurses into children.

    Parameters
    ----------
    converted : WrappedTree
        The wrapper tree root containing computed coordinates.
    root
        The original node to update.
    is_horizontal : bool
        Whether the layout is horizontal.
    """
    if is_horizontal:
        root.y = converted.x
    else:
        root.x = converted.x

    for i, child in enumerate(converted.children):
        if i < len(root.children):
            convert_back(child, root.children[i], is_horizontal)

def layer(node, direction, level_spacing):
    """Set the layer (depth) coordinate for each node in the tree.

    Assigns ``level`` based on the parent's level and positions the
    layered coordinate (``x`` or ``y``) relative to the parent.

    Parameters
    ----------
    node
        The current node.
    direction : LayoutDirection
        The layout direction.
    level_spacing : float
        Spacing between adjacent layers.
    """
    if (parent := node.parent) is not None:
        node.level = parent.level + 1
        if direction == LayoutDirection.LeftToRight:
            node.x = parent.x + (parent.width + node.width) / 2 + level_spacing
        elif direction == LayoutDirection.RightToLeft:
            node.x = parent.x - (parent.width + node.width) / 2 - level_spacing
        elif direction == LayoutDirection.BottomToTop:
            node.y = parent.y + (parent.height + node.height) / 2 + level_spacing
        else:
            node.y = parent.y - (parent.height + node.height) / 2 - level_spacing

    for child in node.children:
        layer(child, direction,level_spacing)

class TidyTreeLayout(Layout):
    """Non-layered tidy tree layout algorithm.

    Examples
    --------
    .. manim:: TidyTreeLayoutExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.alg_tidy_tree import TidyTreeLayout

       class TidyTreeLayoutExample(Scene):
           def construct(self):
               label = Text("TidyTreeLayout algorithm", font_size=24)
               self.add(label)
"""
    def __init__(
        self,
        root,
        direction: LayoutDirection = LayoutDirection.LeftToRight,
        node_spacing: float = 0.5,
        level_spacing: float = 0.5
    ):
        """Initialize the TidyTreeLayout instance."""
        self.root = root
        self.direction = direction
        self.is_horizontal = self._is_horizontal(direction)
        self.node_spacing = node_spacing
        self.level_spacing = level_spacing
        self.wt = None

    def _is_horizontal(self,direction):
        """Check whether the given layout direction is horizontal.

        Parameters
        ----------
        direction : LayoutDirection
            The layout direction to test.

        Returns
        -------
        bool
            ``True`` if the direction is left-to-right or right-to-left.
        """
        return direction in (LayoutDirection.LeftToRight, LayoutDirection.RightToLeft)

    def layout(self):
        """Run the layout computation."""
        layer(self.root, self.direction,self.level_spacing)
        self.wt = WrappedTree.from_node(self.root, self.is_horizontal)
        self.first_walk(self.wt)
        self.second_walk(self.wt, 0)
        convert_back(self.wt, self.root, self.is_horizontal)
        normalize(self.root, self.is_horizontal)
        # self.compute_connectors()
        return self.root

    def first_walk(self, t: WrappedTree):
        """First traversal: compute prelim and mod, detect and eliminate overlaps.

        Parameters
        ----------
        t : WrappedTree
            The root of the subtree to process.
        """
        if t.child_number == 0:
            self.set_extremes(t)
            return

        # Process the first child
        self.first_walk(t.children[0])
        ih = self.update_iyl(self.bottom(t.children[0].extreme_right), 0, None)

        # Process the remaining children
        for i in range(1, t.child_number):
            self.first_walk(t.children[i])
            min_val = self.bottom(t.children[i].extreme_right)
            self.separate(t, i, ih)
            ih = self.update_iyl(min_val, i, ih)

        self.position_root(t)
        self.set_extremes(t)

    def set_extremes(self, t: WrappedTree):
        """Set the extreme (leftmost and rightmost) nodes for a subtree.

        Parameters
        ----------
        t : WrappedTree
            The subtree root.
        """
        if t.child_number == 0:
            t.extreme_left = t
            t.extreme_right = t
            t.mod_sum_extreme_left = 0
            t.mod_sum_extreme_right = 0
        else:
            t.extreme_left = t.children[0].extreme_left
            t.mod_sum_extreme_left = t.children[0].mod_sum_extreme_left
            t.extreme_right = t.children[-1].extreme_right
            t.mod_sum_extreme_right = t.children[-1].mod_sum_extreme_right

    def update_iyl(self, low: float, index: int, ih: Optional[IYLNode]) -> IYLNode:
        """Prune the IYL list and prepend a new node.

        Removes any existing :class:`IYLNode` whose ``low`` is less than or
        equal to *low*, then returns a new head node for the current subtree.

        Parameters
        ----------
        low : float
            The low end of the current subtree's right contour.
        index : int
            The index of the current subtree among its siblings.
        ih : Optional[IYLNode]
            The previous head of the IYL list.

        Returns
        -------
        IYLNode
            The new head of the IYL list.
        """
        while ih is not None and low >= ih.low:
            ih = ih.nxt
        return IYLNode(low, index, ih)

    def separate(self, t: WrappedTree, i: int, ih: Optional[IYLNode]):
        """
        Core of the algorithm: separate the i-th subtree from previous subtrees to avoid overlap.

        Parameters
        ----------
        t : WrappedTree
            parent node
        i : int
            index of the current subtree
        ih : Optional[IYLNode]
            preceding subtrees whose right contour may still collide with the current subtree
        """
        sr = t.children[i - 1]   # current right-contour node, initially the immediate left sibling
        mssr = sr.mod            # sum of mod values from t.children[i-1] to sr
        cl = t.children[i]       # current left-contour node, initially the current subtree root
        mscl = cl.mod            # sum of mod values from t.children[i] to cl

        while sr is not None and cl is not None:
            # Skip preceding subtrees that are completely hidden
            if ih is not None and self.bottom(sr) > ih.low:
                # sr's height exceeds this preceding subtree's contour range; at this height, ih cannot collide with the current subtree
                # Skip this preceding subtree and compare with the next higher one
                ih = ih.nxt

            dist = mssr + sr.prelim + self.node_spacing + (sr.width + cl.width)/2 - (mscl + cl.prelim)
            if dist > 0:
                mscl += dist
                si = ih.index if ih is not None else i - 1
                self.move_subtree(t, i, si, dist)

            sy = self.bottom(sr)
            cy = self.bottom(cl)

            if sy <= cy:
                sr = self.next_right_contour(sr)
                if sr is not None:
                    mssr += sr.mod

            if sy >= cy:
                cl = self.next_left_contour(cl)
                if cl is not None:
                    mscl += cl.mod

        if sr is None and cl is not None:
            self.set_left_thread(t, i, cl, mscl)
        elif sr is not None and cl is None:
            self.set_right_thread(t, i, sr, mssr)

    def move_subtree(self, t: WrappedTree, i: int, si: int, dist: float):
        """Shift a subtree by adding *dist* to its modifier.

        Parameters
        ----------
        t : WrappedTree
            The parent node.
        i : int
            Index of the subtree to move.
        si : int
            Index of the leftmost sibling that was moved.
        dist : float
            The shift distance.
        """
        t.children[i].mod += dist
        t.children[i].mod_sum_extreme_left += dist
        t.children[i].mod_sum_extreme_right += dist
        self.distribute_extra(t, i, si, dist)

    def distribute_extra(self, t: WrappedTree, i: int, si: int, dist: float):
        """Distribute extra spacing among siblings after a subtree is moved.

        Parameters
        ----------
        t : WrappedTree
            The parent node.
        i : int
            Index of the moved subtree.
        si : int
            Index of the leftmost sibling that was moved.
        dist : float
            The total extra distance to distribute.
        """
        if si != i - 1:
            nr = i - si
            t.children[si + 1].shift += dist / nr
            t.children[i].shift -= dist / nr
            t.children[i].change -= dist - dist / nr

    def next_left_contour(self, t: WrappedTree) -> Optional[WrappedTree]:
        """Return the next node on the left contour of a subtree.

        Parameters
        ----------
        t : WrappedTree
            The current contour node.

        Returns
        -------
        Optional[WrappedTree]
            The next left-contour node, or ``None`` if exhausted.
        """
        return t.thread_left if t.child_number == 0 else t.children[0]

    def next_right_contour(self, t: WrappedTree) -> Optional[WrappedTree]:
        """Return the next node on the right contour of a subtree.

        Parameters
        ----------
        t : WrappedTree
            The current contour node.

        Returns
        -------
        Optional[WrappedTree]
            The next right-contour node, or ``None`` if exhausted.
        """
        return t.thread_right if t.child_number == 0 else t.children[-1]

    def bottom(self, t: WrappedTree) -> float:
        """Return the node's extent in the orthogonal direction.

        Parameters
        ----------
        t : WrappedTree
            The node whose extent is computed.

        Returns
        -------
        float
            The extent used for contour comparison.
        """
        if self.is_horizontal:
            return t.height/2 + abs(t.x)
        return abs(t.y) + t.height/2

    def set_left_thread(self, t: WrappedTree, i: int, cl: WrappedTree, modsumcl: float):
        """Set the left thread for a subtree whose left contour is exhausted.

        Parameters
        ----------
        t : WrappedTree
            The parent node.
        i : int
            Index of the current subtree.
        cl : WrappedTree
            The left-contour node of the current subtree.
        modsumcl : float
            The accumulated modifier sum along the left contour.
        """
        li = t.children[0].extreme_left
        li.thread_left = cl
        diff = (modsumcl - cl.mod) - t.children[0].mod_sum_extreme_left
        li.mod += diff
        li.prelim -= diff
        t.children[0].extreme_left = t.children[i].extreme_left
        t.children[0].mod_sum_extreme_left = t.children[i].mod_sum_extreme_left

    def set_right_thread(self, t: WrappedTree, i: int, sr: WrappedTree, modsumsr: float):
        """Set the right thread for a subtree whose right contour is exhausted.

        Parameters
        ----------
        t : WrappedTree
            The parent node.
        i : int
            Index of the current subtree.
        sr : WrappedTree
            The right-contour node of the current subtree.
        modsumsr : float
            The accumulated modifier sum along the right contour.
        """
        ri = t.children[i].extreme_right
        ri.thread_right = sr
        diff = (modsumsr - sr.mod) - t.children[i].mod_sum_extreme_right
        ri.mod += diff
        ri.prelim -= diff
        t.children[i].extreme_right = t.children[i - 1].extreme_right
        t.children[i].mod_sum_extreme_right = t.children[i - 1].mod_sum_extreme_right

    def position_root(self, t: WrappedTree):
        """Place the root of a subtree halfway between its first and last children.

        Parameters
        ----------
        t : WrappedTree
            The subtree root.
        """
        t.prelim = (
            t.children[0].prelim + t.children[0].mod + t.children[-1].mod + t.children[-1].prelim 
        ) / 2

    def second_walk(self, t: WrappedTree, modsum: float):
        """Second traversal: accumulate prelim and mod into final coordinates.

        Parameters
        ----------
        t : WrappedTree
            The subtree root.
        modsum : float
            Sum of all ancestor mod values from the root to the current node.
        """
        modsum += t.mod
        if self.is_horizontal:
            t.x = -t.prelim - modsum
        else:
            t.x = t.prelim + modsum
        self.add_child_spacing(t)

        for child in t.children:
            self.second_walk(child, modsum)

    def add_child_spacing(self, t: WrappedTree):
        """Apply accumulated shift and change values to children's mod.

        Parameters
        ----------
        t : WrappedTree
            The parent node whose children are updated.
        """
        d = 0
        modsumdelta = 0
        for child in t.children:
            d += child.shift
            modsumdelta += d + child.change
            child.mod += modsumdelta

    def compute_connectors(self):
        """Compute connectors."""
        def compute_node(node:Any):
            """Compute the connector path from a node to its parent.

            Parameters
            ----------
            node : Any
                The child node.

            Returns
            -------
            VMobject
                The connector line/curve.
            """
            parent = node.parent
            match self.direction:
                case LayoutDirection.TopToBottom:
                    xs,ys = parent.x, parent.y - parent.height/2
                    xe,ye = node.x, node.y + node.height/2
                    points = ((xs, ys),(xs, (ys + ye) / 2),(xe, (ys + ye) / 2),(xe, ye))
                case LayoutDirection.BottomToTop:
                    xs,ys = parent.x, parent.y + parent.height/2
                    xe,ye = node.x, node.y - node.height/2
                    points = ((xs, ys),(xs, (ys + ye) / 2),(xe, (ys + ye) / 2),(xe, ye))
                case LayoutDirection.LeftToRight:
                    xs,ys = parent.x + parent.width/2, parent.y
                    xe,ye = node.x - node.width/2, node.y
                    points = ((xs, ys),((xs + xe) / 2, ys),((xs + xe) / 2, ye),(xe, ye))
                case LayoutDirection.RightToLeft:
                    xs,ys = parent.x - parent.width/2, parent.y
                    xe,ye = node.x + node.width/2, node.y
                    points = ((xs, ys),((xs + xe) / 2, ys),((xs + xe) / 2, ye),(xe, ye))
            node.connector_points = points

            for child in node.children:
                compute_node(child)

        for child in self.root.children:
            compute_node(child)