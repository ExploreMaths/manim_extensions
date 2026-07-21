"""
Catalog / organisation-chart layout algorithm - Python implementation

Layout characteristics:
- Root node is centred
- Second-level nodes are arranged horizontally below the root
- Third-level and deeper nodes are arranged vertically below their parent (vertical tree)
- Sibling offsets are automatically adjusted to avoid overlaps
"""
__all__ = [
    'CatalogLayout'
]
from dataclasses import dataclass, field
from typing import List, Optional, Any, Callable, Tuple
from .layout_config import LayoutDirection
from .layout import Layout

@dataclass
class CatalogNode:
    """
    Organisation-chart layout node.

    Input attributes:
        width, height: node dimensions
        children: list of child nodes

    Output attributes (filled by the algorithm):
        left, top: top-left coordinates of the node on the canvas
        layer_index: layer index (root is 0)
        parent: reference to the parent node
        children_area_width: total width of the root's children (used for horizontal arrangement)
    

    .. manim:: CatalogNodeDocExample
        :save_last_frame:
        
        from manim import *
        from manim_extensions.mindmap.algorithms.alg_catalog import CatalogNode
        
        class CatalogNodeDocExample(Scene):
            def construct(self):
                node = CatalogNode(width=2.0, height=1.0)
                info = Text(f"CatalogNode {node.width:.1f}x{node.height:.1f}", font_size=36)
                self.add(info)
    """
    data: Any = None
    width: float = 0.0
    height: float = 0.0
    children: List["CatalogNode"] = field(default_factory=list)

    # Layout results
    left: float = 0.0
    top: float = 0.0
    layer_index: int = 0
    parent: Optional["CatalogNode"] = None
    children_area_width: float = 0.0

    @classmethod
    def from_data(cls, node: Any) -> "CatalogNode":
        """Recursively create a node tree from raw data."""
        org_node = cls()
        org_node.node = node
        org_node.width = getattr(node, 'width', 0)
        org_node.height = getattr(node, 'height', 0)

        children = getattr(node, 'children', [])
        org_node.children = [cls.from_data(child) for child in children]
        return org_node

class CatalogLayout(Layout):
    """Organisation-chart layout algorithm.

    .. manim:: CatalogLayoutDocExample
        :save_last_frame:
        
        from manim import *
        from manim_extensions.mindmap import Node
        from manim_extensions.mindmap.algorithms.alg_catalog import CatalogLayout
        
        class CatalogLayoutDocExample(Scene):
            def construct(self):
                root = Node(Text("Root", font_size=24))
                root.add_child(Node(Text("A", font_size=24)))
                root.add_child(Node(Text("B", font_size=24)))
                CatalogLayout(root).layout()
                self.add(Text("CatalogLayout applied", font_size=36))
    """
    def __init__(
        self,
        root: Any,
        node_spacing: float = 0.5,
        level_spacing: float = 0.5
    ):
        """
        Parameters
        ----------
        root
            The root node.
        node_spacing
            Vertical distance from root to second-level nodes, and horizontal spacing among second-level nodes.
        level_spacing
            Vertical spacing among third-level and deeper nodes.
        """
        self.root = CatalogNode.from_data(root)
        self.margin_root_child = node_spacing
        self.margin_vertical = level_spacing

    def _get_margin_x(self, layer_index: int) -> float:
        """Horizontal spacing:
            + children of the root use margin_root_child
            + other layers use margin_vertical
            + only second-level nodes use horizontal spacing
        """
        return self.margin_root_child if layer_index == 1 else self.margin_vertical

    def _get_margin_y(self, layer_index: int) -> float:
        """Vertical spacing: children of the root use margin_root_child, other layers use margin_vertical."""
        return self.margin_root_child if layer_index == 1 else self.margin_vertical

    def _update_children(self, nodes: List[CatalogNode], prop: str, offset: float):
        """Recursively update a child-node attribute (left or top)."""
        for node in nodes:
            setattr(node, prop, getattr(node, prop) + offset)
            if node.children:
                self._update_children(node.children, prop, offset)

    def _update_children_pro(self, nodes: List[CatalogNode], props: dict):
        """Recursively update multiple child-node attributes."""
        for node in nodes:
            for k, v in props.items():
                setattr(node, k, getattr(node, k) + v)
            if node.children:
                self._update_children_pro(node.children, props)

    def _walk(
        self,
        node: CatalogNode,
        pre_cb: Optional[Callable] = None,
        post_cb: Optional[Callable] = None,
        layer: int = 0,
        index: int = 0
    ):
        """Traverse the tree, executing pre-order and post-order callbacks."""
        if pre_cb:
            pre_cb(node, layer, index)
        for i, child in enumerate(node.children):
            child.layer_index = layer + 1
            child.parent = node
            self._walk(child, pre_cb, post_cb, layer + 1, i)
        if post_cb:
            post_cb(node, layer, index)

    def _get_node_boundaries_horizontal(self, node: CatalogNode) -> Tuple[float, float]:
        """Return the horizontal boundaries (min_left, max_right) of a node and all its descendants."""
        left = node.left
        right = node.left + node.width
        for child in node.children:
            cl, cr = self._get_node_boundaries_horizontal(child)
            left = min(left, cl)
            right = max(right, cr)
        return left, right

    def _get_node_area_width(self, node: CatalogNode) -> float:
        """
        Recursively compute the maximum width of a subtree (horizontal span from root to rightmost leaf).
        The total width of every path is computed recursively and the maximum is taken.
        Note: this width is used to adjust horizontal offsets among siblings.
        """
        min_l, max_r = self._get_node_boundaries_horizontal(node)
        return max_r - min_l

    def _get_node_area_height(self, node: CatalogNode) -> float:
        """Recursively compute the total height of a node's subtree (used for vertical adjustment)."""
        total = node.height
        if node.children:
            margin_y = self._get_margin_y(node.layer_index + 1)
            for i, child in enumerate(node.children):
                total += margin_y
                total += self._get_node_area_height(child)
        return total

    def _update_brothers_left(self, node: CatalogNode, add_width: float):
        """Shift sibling nodes to the right by add_width."""
        if node.parent is None:
            return
        siblings = node.parent.children
        idx = siblings.index(node)
        for i, sibling in enumerate(siblings):
            if i > idx:
                sibling.left += add_width
                if sibling.children:
                    self._update_children(sibling.children, "left", add_width)
        # Propagate adjustment upward
        self._update_brothers_left(node.parent, add_width)

    def _update_brothers_top(self, node: CatalogNode, add_height: float):
        """Shift sibling nodes downward by add_height."""
        if node.parent and not node.parent.layer_index == 0:  # parent is not the root
            siblings = node.parent.children
            idx = siblings.index(node)
            for i, sibling in enumerate(siblings):
                if i > idx:
                    sibling.top += add_height
                    if sibling.children:
                        self._update_children(sibling.children, "top", add_height)
            self._update_brothers_top(node.parent, add_height)

    # ------------------------------------------------------------------
    # Core layout steps
    # ------------------------------------------------------------------
    def _compute_base_value(self):
        """
        Step 1: create nodes, set the root position, and set the initial top of second-level nodes.
        """
        def pre_cb(node: CatalogNode, layer: int, _idx: int):
            if layer:
                # Non-root node: second-level nodes (parent is root) are placed below the root
                if node.parent and node.parent.layer_index == 0:
                    margin_y = self._get_margin_y(layer)
                    node.top = node.parent.top + node.parent.height + margin_y

        # Post-order traversal: compute children_area_width (total width of children) for the root
        def post_cb(node: CatalogNode, layer: int, _idx: int):
            if layer == 0:
                child_count = len(node.children)
                if child_count == 0:
                    node.children_area_width = 0
                else:
                    children_width = sum(child.width for child in node.children)
                    margin_x = self._get_margin_x(layer + 1)
                    node.children_area_width = children_width + (child_count + 1) * margin_x

        self._walk(self.root, pre_cb=pre_cb, post_cb=post_cb)

    def _compute_left_top_value(self):
        """
        Step 2: compute left and top of child nodes.
        - Children of the root are arranged horizontally
        - Children of non-root nodes are arranged vertically
        """
        def pre_cb(node: CatalogNode, layer: int, _idx: int):
            margin_x = self._get_margin_x(layer + 1)
            margin_y = self._get_margin_y(layer + 1)

            if layer == 0:  # root node
                # Centre children horizontally
                start_left = node.left + node.width / 2 - node.children_area_width / 2
                current_left = start_left + margin_x
                for child in node.children:
                    child.left = current_left
                    current_left += child.width + margin_x
            else:
                # Non-root node: children are arranged vertically
                start_top = node.top + node.height + margin_y
                current_top = start_top
                for child in node.children:
                    child.left = node.left + node.width * 0.5  # horizontally centred on parent
                    child.top = current_top
                    current_top += child.height + margin_y

        self._walk(self.root, pre_cb=pre_cb)

    def _adjust_left_top_value(self):
        """
        Step 3: adjust positions (handle subtree width/height offsets).
        - Pre-order: for second-level nodes, if their subtree width exceeds their own width, shift following siblings
        - Pre-order: for non-root nodes with children, adjust vertical offset
        - Post-order: for the root, shift all children horizontally to centre the whole subtree
        """
        # Pre-order callback
        def pre_cb(node: CatalogNode, layer: int, _idx: int):
            # Horizontal adjustment (second-level nodes and their descendants)
            if node.parent and node.parent.layer_index == 0:
                area_width = self._get_node_area_width(node)
                diff = area_width - node.width
                if diff > 0:
                    self._update_brothers_left(node, diff)
            # Vertical adjustment (non-root nodes with children)
            if node.parent and node.parent.layer_index != 0 and node.children:
                margin_y = self._get_margin_y(layer + 1)
                total_height = sum(
                    child.height + margin_y
                    for child in node.children
                )
                self._update_brothers_top(node, total_height)

        # Post-order callback: centre the whole subtree under the root
        def post_cb(node: CatalogNode, layer: int, _idx: int):
            if layer == 0:
                left_bound, right_bound = self._get_node_boundaries_horizontal(node)
                children_width = right_bound - left_bound
                # Compute the offset so the subtree is horizontally centred on the root
                target_center = node.left + node.width / 2
                current_center = left_bound + children_width / 2
                offset = target_center - current_center
                if abs(offset) > 1e-6:
                    self._update_children(node.children, "left", offset)

        self._walk(self.root, pre_cb=pre_cb, post_cb=post_cb)

    def _applay_coords(self):
        """Apply the computed results to the original nodes."""
        def _applay_coords_for_node(node: CatalogNode):
            node.node.x = node.left + node.width / 2
            node.node.y = -node.top - node.height / 2
            node.node.level = node.layer_index
            for child in node.children:
                _applay_coords_for_node(child)

        _applay_coords_for_node(self.root)

    def layout(self) -> Any:
        """Run the full layout and return the root node (with coordinates filled in)."""
        self._compute_base_value()
        self._compute_left_top_value()
        self._adjust_left_top_value()
        self._applay_coords()
        return self.root.node