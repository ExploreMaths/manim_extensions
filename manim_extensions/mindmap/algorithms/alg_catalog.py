# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
Catalog / organisation-chart layout algorithm - Python implementation

Layout characteristics:
- Root node is centred
- Second-level nodes are arranged horizontally below the root
- Third-level and deeper nodes are arranged vertically below their parent (vertical tree)
- Sibling offsets are automatically adjusted to avoid overlaps
"""

__all__ = ["CatalogLayout"]
from dataclasses import dataclass, field
from typing import List, Optional, Any, Callable, Tuple
from .layout import Layout


@dataclass
class CatalogNode:
    """Organisation-chart layout node.

    Input attributes:
        width, height: node dimensions
        children: list of child nodes

    Output attributes (filled by the algorithm):
        left, top: top-left coordinates of the node on the canvas
        layer_index: layer index (root is 0)
        parent: reference to the parent node
        children_area_width: total width of the root's children (used for horizontal arrangement)

    Examples
    --------
    .. manim:: CatalogNodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.alg_catalog import CatalogNode

       class CatalogNodeExample(Scene):
           def construct(self):
               cn = CatalogNode()
               label = Text(f"CatalogNode: {cn.width}x{cn.height}", font_size=24)
               self.add(label)
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
        """Recursively create a node tree from raw data.

        Parameters
        ----------
        node : Any
            Raw data object used to build the catalog node tree.
        """
        org_node = cls()
        org_node.node = node
        org_node.width = getattr(node, "width", 0)
        org_node.height = getattr(node, "height", 0)

        children = getattr(node, "children", [])
        org_node.children = [cls.from_data(child) for child in children]
        return org_node


class CatalogLayout(Layout):
    """Organisation-chart layout algorithm.

    Parameters
    ----------
        root
            The root node.
        node_spacing
            Vertical distance from root to second-level nodes, and horizontal spacing among second-level nodes.
        level_spacing
            Vertical spacing among third-level and deeper nodes.

    Examples
    --------
    .. manim:: CatalogLayoutExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.alg_catalog import CatalogLayout

       class CatalogLayoutExample(Scene):
           def construct(self):
               label = Text("CatalogLayout algorithm", font_size=24)
               self.add(label)
    """

    def __init__(
        self, root: Any, node_spacing: float = 0.5, level_spacing: float = 0.5
    ):
        """Initialize CatalogLayout."""
        self.root = CatalogNode.from_data(root)
        self.margin_root_child = node_spacing
        self.margin_vertical = level_spacing

    def _get_margin_x(self, layer_index: int) -> float:
        """Horizontal spacing used for node placement.

        Parameters
        ----------
        layer_index : int
            Layer depth whose spacing rule should be selected.
        """
        return self.margin_root_child if layer_index == 1 else self.margin_vertical

    def _get_margin_y(self, layer_index: int) -> float:
        """Vertical spacing used between layers in the catalog layout.

        Parameters
        ----------
        layer_index : int
            Layer depth whose vertical spacing rule should be selected.
        """
        return self.margin_root_child if layer_index == 1 else self.margin_vertical

    def _update_children(self, nodes: List[CatalogNode], prop: str, offset: float):
        """Recursively update a child-node attribute such as left or top.

        Parameters
        ----------
        nodes : List[CatalogNode]
            Child nodes to shift together.
        prop : str
            Attribute name to update, such as left or top.
        offset : float
            Amount added to each node coordinate.
        """
        for node in nodes:
            setattr(node, prop, getattr(node, prop) + offset)
            if node.children:
                self._update_children(node.children, prop, offset)

    def _update_children_pro(self, nodes: List[CatalogNode], props: dict):
        """Recursively update multiple child-node attributes in one pass.

        Parameters
        ----------
        nodes : List[CatalogNode]
            Child nodes whose attributes should be adjusted.
        props : dict
            Mapping of attribute names to offset values.
        """
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
        index: int = 0,
    ):
        """Traverse the tree while running pre-order and post-order callbacks.

        Parameters
        ----------
        node : CatalogNode
            Current node in the tree traversal.
        pre_cb : Optional[Callable]
            Callback invoked before visiting each child subtree.
        post_cb : Optional[Callable]
            Callback invoked after visiting each child subtree.
        layer : int
            Current depth of the node in the tree.
        index : int
            Position of the node within its parent children list.
        """
        if pre_cb:
            pre_cb(node, layer, index)
        for i, child in enumerate(node.children):
            child.layer_index = layer + 1
            child.parent = node
            self._walk(child, pre_cb, post_cb, layer + 1, i)
        if post_cb:
            post_cb(node, layer, index)

    def _get_node_boundaries_horizontal(self, node: CatalogNode) -> Tuple[float, float]:
        """Return the horizontal boundaries of a node and all descendants.

        Parameters
        ----------
        node : CatalogNode
            Root node of the subtree whose horizontal bounds should be computed.
        """
        left = node.left
        right = node.left + node.width
        for child in node.children:
            cl, cr = self._get_node_boundaries_horizontal(child)
            left = min(left, cl)
            right = max(right, cr)
        return left, right

    def _get_node_area_width(self, node: CatalogNode) -> float:
        """Return the maximum horizontal span of a subtree.

        Parameters
        ----------
        node : CatalogNode
            Root node of the subtree whose width should be measured.
        """
        min_l, max_r = self._get_node_boundaries_horizontal(node)
        return max_r - min_l

    def _get_node_area_height(self, node: CatalogNode) -> float:
        """Recursively compute the total height of a node's subtree.

        Parameters
        ----------
        node : CatalogNode
            The root of the subtree.

        Returns
        -------
        float
            The cumulative area height.
        """
        total = node.height
        if node.children:
            margin_y = self._get_margin_y(node.layer_index + 1)
            for i, child in enumerate(node.children):
                total += margin_y
                total += self._get_node_area_height(child)
        return total

    def _update_brothers_left(self, node: CatalogNode, add_width: float):
        """Shift elder sibling nodes to the right by *add_width*.

        Also propagates the adjustment upward to the parent's siblings.

        Parameters
        ----------
        node : CatalogNode
            The node whose younger siblings must shift.
        add_width : float
            The horizontal offset to apply.
        """
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
        """Shift elder sibling nodes downward by *add_height*.

        Parameters
        ----------
        node : CatalogNode
            The node whose younger siblings must shift.
        add_height : float
            The vertical offset to apply.
        """
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
            """Pre-order callback: set initial top position for second-level nodes.

            Parameters
            ----------
            node : CatalogNode
                The current node.
            layer : int
                The depth of the current node.
            _idx : int
                The index of the current node within its parent's children.
            """
            if layer:
                # Non-root node: second-level nodes (parent is root) are placed below the root
                if node.parent and node.parent.layer_index == 0:
                    margin_y = self._get_margin_y(layer)
                    node.top = node.parent.top + node.parent.height + margin_y

        # Post-order traversal: compute children_area_width (total width of children) for the root
        def post_cb(node: CatalogNode, layer: int, _idx: int):
            """Post-order callback: compute children area width for the root.

            Parameters
            ----------
            node : CatalogNode
                The current node.
            layer : int
                The depth of the current node.
            _idx : int
                The index of the current node within its parent's children.
            """
            if layer == 0:
                child_count = len(node.children)
                if child_count == 0:
                    node.children_area_width = 0
                else:
                    children_width = sum(child.width for child in node.children)
                    margin_x = self._get_margin_x(layer + 1)
                    node.children_area_width = (
                        children_width + (child_count + 1) * margin_x
                    )

        self._walk(self.root, pre_cb=pre_cb, post_cb=post_cb)

    def _compute_left_top_value(self):
        """
        Step 2: compute left and top of child nodes.
        - Children of the root are arranged horizontally
        - Children of non-root nodes are arranged vertically
        """

        def pre_cb(node: CatalogNode, layer: int, _idx: int):
            """Pre-order callback: compute left and top positions for child nodes.

            Parameters
            ----------
            node : CatalogNode
                The current node.
            layer : int
                The depth of the current node.
            _idx : int
                The index of the current node within its parent's children.
            """
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
                    child.left = (
                        node.left + node.width * 0.5
                    )  # horizontally centred on parent
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
            """Pre-order callback: adjust left/top values to avoid overlapping.

            Parameters
            ----------
            node : CatalogNode
                The current node.
            layer : int
                The depth of the current node.
            _idx : int
                The index of the current node within its parent's children.
            """
            if node.parent and node.parent.layer_index == 0:
                area_width = self._get_node_area_width(node)
                diff = area_width - node.width
                if diff > 0:
                    self._update_brothers_left(node, diff)
            # Vertical adjustment (non-root nodes with children)
            if node.parent and node.parent.layer_index != 0 and node.children:
                margin_y = self._get_margin_y(layer + 1)
                total_height = sum(child.height + margin_y for child in node.children)
                self._update_brothers_top(node, total_height)

        # Post-order callback: centre the whole subtree under the root
        def post_cb(node: CatalogNode, layer: int, _idx: int):
            """Post-order callback: centre the root's children horizontally.

            Parameters
            ----------
            node : CatalogNode
                The current node.
            layer : int
                The depth of the current node.
            _idx : int
                The index of the current node within its parent's children.
            """
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
            """Apply computed ``left``/``top`` coordinates to a node and its descendants.

            Parameters
            ----------
            node : CatalogNode
                The root of the subtree to update.
            """
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
