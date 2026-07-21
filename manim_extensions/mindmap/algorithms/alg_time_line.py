"""Timeline layout algorithm - Python implementation."""
__all__ = [
    'TimeLineLayout',
]

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable,Tuple
from .layout import Layout
from .layout_config import LayoutDirection

@dataclass
class TimelineNode:
    """
    Timeline layout node.

    Input attributes (required):
        width, height: node dimensions
        children: list of child nodes
        side_dir: growth direction (subtrees rooted at second-level nodes grow upward or downward)

    Output attributes (filled by the algorithm):
        x, y: top-left coordinates of the node on the canvas
    

    """
    node: Any = None
    width: float = 0.0
    height: float = 0.0
    children: List["TimelineNode"] = field(default_factory=list)
    side_dir: LayoutDirection = None

    # Layout result coordinates
    x: float = 0.0
    y: float = 0.0

    # Internal runtime attributes (do not set manually)
    _is_root: bool = False
    _parent: Optional["TimelineNode"] = None
    _layer_index: int = 0         # layer depth (root is 0)
    _index: int = 0               # index among siblings

    @classmethod
    def from_node(cls, node) -> 'TimelineNode':
        """Create a wrapper tree from the original node."""
        tl = cls()
        tl.node = node
        # Copy dimensions
        tl.width = float(getattr(node, 'width', 0))
        tl.height = float(getattr(node, 'height', 0))
        # Recursively create children
        children = getattr(node, 'children', [])
        tl.children = [cls.from_node(child) for child in children]
        return tl

def walk(
    node: TimelineNode,
    parent: Optional[TimelineNode],
    before_callback: Optional[Callable],
    after_callback: Optional[Callable],
    is_root: bool = False,
    layer_index: int = 0,
    index: int = 0
):
    """
    Tree traversal utility.

    Supports pre-order (before_callback) and post-order (after_callback) callbacks.
    If before_callback returns True, traversal of that node's children is skipped.
    

    """
    # Pre-order callback
    if before_callback:
        result = before_callback(node, parent, is_root, layer_index, index)
        if result is True:
            return

    # Traverse children
    if node.children:
        for i, child in enumerate(node.children):
            walk(child, node, before_callback, after_callback,False, layer_index + 1, i)

    # Post-order callback
    if after_callback:
        after_callback(node, parent, is_root, layer_index, index)

class TimeLineLayout(Layout):
    """Timeline layout engine.

    """
    def __init__(
        self,
        root: Any,
        sides: Tuple[LayoutDirection] = (
            LayoutDirection.TopToBottom,
            LayoutDirection.BottomToTop
        ),
        level_spacing: float = 0.5,
        node_spacing: float = 0.5,
    ):
        self.root = TimelineNode.from_node(root)
        self.level_spacing = level_spacing
        self.node_spacing = node_spacing
        self.sides = sides
        self.is_two_sides = (len(sides) == 2)

    # ==================== Public API ====================
    def layout(self) -> Any:
        """Run the three-stage layout algorithm."""
        self._compute_base()
        self._compute_coords()
        self._adjust()
        self._apply_coords(self.root)
        return self.root.node

    # ==================== Stage 1: base-value computation ====================
    def _compute_base(self):
        """Pre-order traversal: create nodes, set root position, compute second-level top values."""
        def before_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ) -> bool:
            node._parent = parent
            node._layer_index = layer_index
            node._index = index

            if is_root:
                node._is_root = True
            else:
                # Non-root nodes: alternate sides on the timeline
                if self.is_two_sides:
                    # Third-level and deeper nodes inherit from their parent
                    if parent and parent.side_dir and not parent._is_root:
                        node.side_dir = parent.side_dir
                    else:
                        # Growth direction: second-level nodes alternate
                        node.side_dir = self.sides[index % 2]
                else:
                    node.side_dir = self.sides[0]

                # Second-level nodes (direct children of the root) are vertically centred with the root
                if parent and parent._is_root:
                    node.y = parent.y + (parent.height - node.height) / 2
            return False

        walk(self.root, None, before_callback, None, True, 0)

    # ==================== Stage 2: precise coordinate computation ====================
    def _compute_coords(self):
        """Pre-order traversal: compute node left (x) and top (y)."""
        def before_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ) -> bool:
            if not node.children:
                return False

            level_spacing = self.level_spacing
            node_spacing = self.node_spacing

            if is_root:
                # Children of the root are arranged on the same horizontal line as the root
                left = node.x + node.width
                total_left = left + level_spacing
                for cur in node.children:
                    cur.x = total_left
                    total_left += cur.width + level_spacing
            else:
                total_top = node.y + node.height + node_spacing
                for cur in node.children:
                    cur.x = node.x + node.width * 0.5
                    cur.y = total_top
                    total_top += (cur.height + node_spacing)
            return False

        walk(self.root, None, before_callback, None, True, 0)

    # ==================== Stage 3: collision adjustment ====================
    def _adjust(self):
        """Pre-order + post-order traversal: adjust node left and top."""
        def before_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ) -> bool:
            if node._is_root:
                self._update_brothers_left(node)

            length = len(node.children)
            if parent and not parent._is_root and length > 0:
                node_spacing = self.node_spacing
                total_height = sum(item.height for item in node.children) + length * node_spacing
                self._update_brothers_top(node, total_height)
            return False

        def after_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ):
            # Special handling: mirror-flip upward-growing branches
            if (
                parent and
                parent._is_root and
                node.side_dir == LayoutDirection.BottomToTop and
                node.children
            ):
                # Mirror the children of the second-level node to above the parent
                for item in node.children:
                    total_height = self._get_node_area_height(item)
                    _top = item.y
                    item.y = node.y - (item.y - node.y) - total_height + node.height
                    self._update_children(item.children, "y", item.y - _top)

        walk(self.root, None, before_callback, after_callback, True, 0)

    # ==================== Core collision-adjustment algorithms ====================
    def _update_brothers_left(self, node: TimelineNode):
        """
        Adjust siblings' left (x coordinate).

        Logic: traverse the root's children (second-level nodes). If a node's subtree
        actually occupies more width than the node itself, all following siblings
        must shift right to avoid overlap.
        """
        children_list = node.children
        total_add_width = 0.0

        for item in children_list:
            item.x += total_add_width
            if item.children:
                self._update_children(item.children, "x", total_add_width)

            bounds = self._get_node_boundaries(item, "h")
            area_width = bounds["right"] - bounds["left"]
            difference = area_width - item.width
            if difference > 0:
                total_add_width += difference

    def _update_brothers_top(self, node: TimelineNode, add_height: float):
        """
        Adjust siblings' top (y coordinate).

        Logic: the current node's subtree is tall, so following siblings in the parent's
        child list must shift down. Then propagate upward along the parent chain.
        """
        if node._parent and not node._parent._is_root:
            children_list = node._parent.children
            try:
                idx = children_list.index(node)
            except ValueError:
                return

            for _index, item in enumerate(children_list):
                _offset = 0.0
                # Nodes below shift down
                if _index > idx:
                    _offset = add_height
                item.y += _offset
                # Synchronously update child positions
                if item.children:
                    self._update_children(item.children, "y", _offset)

            # Update parent position
            self._update_brothers_top(node._parent, add_height)

    # ==================== Helper methods ====================
    def _get_node_act_children_length(self, node: TimelineNode) -> int:
        """Return the actual number of children of the node."""
        return len(node.children)

    def _get_node_area_height(self, node: TimelineNode) -> float:
        """Recursively compute the area height of the node."""
        total_height = 0.0

        def loop(n: TimelineNode):
            nonlocal total_height
            total_height += (n.height + self.node_spacing)
            if n.children:
                for item in n.children:
                    loop(item)

        loop(node)
        return total_height

    def _get_node_boundaries(self, node: TimelineNode, dir: str) -> Dict[str, float]:
        """Return the boundary values of the node."""
        def walk_tree(root: TimelineNode):
            _left = float("inf")
            _right = float("-inf")
            _top = float("inf")
            _bottom = float("-inf")

            if root.children:
                for child in root.children:
                    bounds = walk_tree(child)
                    _left = min(_left, bounds["left"])
                    _right = max(_right, bounds["right"])
                    _top = min(_top, bounds["top"])
                    _bottom = max(_bottom, bounds["bottom"])

            cur = {
                "left": root.x,
                "right": root.x + root.width,
                "top": root.y,
                "bottom": root.y + root.height
            }
            return {
                "left": min(cur["left"], _left),
                "right": max(cur["right"], _right),
                "top": min(cur["top"], _top),
                "bottom": max(cur["bottom"], _bottom)
            }

        return walk_tree(node)

    def _update_children(self, children: List[TimelineNode], prop: str, offset: float):
        """Update a child-node attribute."""
        for item in children:
            current = getattr(item, prop)
            setattr(item, prop, current + offset)
            if item.children:
                self._update_children(item.children, prop, offset)

    # ==================== Coordinate write-back ====================
    def _apply_coords(self, node: TimelineNode):
        """Apply the computed coordinates to the original node."""
        if node.node:
            node.node.x = node.x + node.width / 2
            node.node.y = - node.y - node.height / 2
            node.node.side = node.side_dir
            node.node.level = node._layer_index
        for child in node.children:
            self._apply_coords(child)