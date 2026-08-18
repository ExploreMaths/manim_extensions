# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *
__all__ = [
    'Node',
    'NodeSate',
    'NodeStyle',
    'dfs_walker',
    'bfs_walker'
]
from enum import Enum
from collections import deque
from typing import Generator,List,Dict

from manim.utils.color import *
import numpy as np

from ..algorithms import LayoutType,LayoutDirection
    
class NodeSate(Enum):
    """Node state.

    Examples
    --------
    .. manim:: NodeSateExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.nodes.node import NodeSate

       class NodeSateExample(Scene):
           def construct(self):
               state = NodeSate.DISPLAY
               label = Text(f"State: {state.name}", font_size=24)
               self.add(label)
"""
    INSERT = 0  # newly inserted
    REMOVE = 1  # pending removal
    DISPLAY = 2  # already displayed
    SCALE = 3  # pending scale
    ALTER = 4  # replace node content

class NodeStyle:
    """Overall layout parameters and a list of node-style dicts indexed by node level.

    Parameters
    ----------
    node_style : list of dict or None, optional
        List of style dictionaries for node boxes, indexed by level.
        Each dict may contain keys like ``'color'`` and ``'stroke_width'``.
    line_style : list of dict or None, optional
        List of style dictionaries for connector lines, indexed by level.
    text_style : list of dict or None, optional
        List of style dictionaries for node text, indexed by level.
        Each dict may contain keys like ``'color'`` and ``'font_size'``.

    Examples
    --------
    .. manim:: NodeStyleExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.nodes.node import NodeStyle

       class NodeStyleExample(Scene):
           def construct(self):
               style = NodeStyle()
               label = Text("NodeStyle with default colors", font_size=24)
               self.add(label)
"""
    def __init__(
        self,
        node_style: List[Dict[str, object]] | None = [
            {'color': RED, 'stroke_width': 8},
            {'color': BLUE, 'stroke_width': 6},
            {'color': PURE_YELLOW, 'stroke_width': 4},
            {'color': GREEN, 'stroke_width': 4}
        ],
        line_style: List[Dict[str, object]] | None = [
            {'color': RED, 'stroke_width': 8},
            {'color': BLUE, 'stroke_width': 6},
            {'color': PURE_YELLOW, 'stroke_width': 4},
            {'color': GREEN, 'stroke_width': 4}
        ],
        text_style: List[Dict[str, object]] | None = [
            {'color': RED, 'font_size': 64},
            {'color': PURE_YELLOW, 'font_size': 56},
            {'color': GREEN, 'font_size': 48},
            {'color': WHITE, 'font_size': 36}
        ],
    ) -> None:
        """Initialize the NodeStyle instance."""
        self.node_num = len(node_style)
        if self.node_num:
            self.node_style = node_style
        else:
            self.node_style = [{'color':PURE_YELLOW, 'stroke_width':4}]
            self.node_num = 1

        self.line_num = len(line_style)
        if self.line_num:
            self.line_style = line_style
        else:
            self.line_style = [{'color':PURE_YELLOW, 'stroke_width':4}]
            self.line_num = 1

        self.text_num = len(text_style)
        if self.text_num: 
            self.text_style = text_style
        else:
            self.text_style = [{'color':PURE_YELLOW, 'font_size':36}]
            self.text_num = 1

    def get_node_style(self,level:int) -> Dict:
        """Return the style dictionary for the requested node level.

        Parameters
        ----------
        level : int
            Hierarchy level whose style definition should be returned.
        """
        if level < self.node_num:
            return self.node_style[level]
        return self.node_style[-1]
    
    def get_line_style(self,level:int) -> Dict:
        """Return the line style for the requested hierarchy level.

        Parameters
        ----------
        level : int
            Hierarchy level whose connector style should be returned.
        """
        if level < self.line_num:
            return self.line_style[level]
        return self.line_style[-1]
    
    def get_text_style(self,level:int) -> Dict:
        """Return the text style for the requested hierarchy level.

        Parameters
        ----------
        level : int
            Hierarchy level whose text style should be returned.
        """
        if level < self.text_num:
            return self.text_style[level]
        return self.text_style[-1]

def dfs_walker(root: 'Node') -> Generator:
    """Yield the tree in depth-first pre-order using a stack.

    Parameters
    ----------
    root : 'Node'
        Root node of the tree to traverse.
    """
    if not root:
        return []
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        for child in reversed(node.children):
            stack.append(child)

def bfs_walker(root: 'Node') -> Generator:
    """Yield the tree in breadth-first level order using a queue.

    Parameters
    ----------
    root : 'Node'
        Root node of the tree to traverse.
    """
    if not root:
        return []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        yield node
        for child in node.children:
            queue.append(child)

class Node:
    r"""Tree-node class.

    .. manim:: NodeDocExample
       :save_last_frame:
        
       from manim import *
       from manim_extensions.mindmap import Node

       class NodeDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36))
               root.add_child(Node(MathTex(r"\text{Child}", font_size=36)))
               self.add(root.vmobject, root.surr_rect)
    """
    def __init__(
        self,
        vmobject: VMobject | None = None,
        buff: float = 0.2,
        **kwargs: object,
    ) -> None:
        """Initialize the Node instance."""
        self.vmobject = vmobject
        self.height = self.vmobject.height + 2*buff
        self.width = self.vmobject.width + 2*buff
        self.buff = buff
        self.surr_rect = Rectangle(
            width = self.width,
            height = self.height,
            **kwargs
        )
        self.x = 0
        self.y = 0
        self.level = 0
        self.parent = None
        self.neighbor = None  # neighbouring node
        self.children = []
        self.node_state = NodeSate.INSERT  # node state
        self.side = None
    
    def scale(self, scale_factor: float) -> None:
        """Scale the node around its current center.

        Parameters
        ----------
        scale_factor : float
            Uniform scaling factor applied to the node dimensions.
        """
        self.node_state = NodeSate.SCALE
        self.scale_factor = scale_factor
        self.width *= scale_factor
        self.height *= scale_factor
    
    def add_child(self, child: 'Node') -> None:
        """Attach a child node to the current node.

        Parameters
        ----------
        child : 'Node'
            Child node to insert beneath the current parent.
        """
        if self.children:
            child.neighbor = self.children[-1]
            child.node_state = NodeSate.INSERT
        self.children.append(child)
        child.parent = self

    def remove_child(self, child: 'Node') -> None:
        """Mark a child node for removal from the current node.

        Parameters
        ----------
        child : 'Node'
            Child node scheduled for removal from the tree.
        """
        if child not in self.children:
            raise ValueError(f"Node {child} is not a child of {self}")
        child.node_state = NodeSate.REMOVE

    def alter_content(self, vmobject: VMobject) -> None:
        """Replace the displayed content of the node.

        Parameters
        ----------
        vmobject : VMobject
            New mobject used to render the node content.
        """
        self.node_state = NodeSate.ALTER
        self.alter_vmobject = vmobject
        self.width = self.alter_vmobject.width + 2*self.buff
        self.height = self.alter_vmobject.height + 2*self.buff

    def _get_mindmap_connector(self, direction: np.ndarray, **kwargs: object) -> Line:
        """Return the connector line for a mind-map node.

    Parameters
    ----------
    direction : np.ndarray
    The direction of the operation.
    """
        if np.array_equal(direction,UP):
            start,end = self.parent.surr_rect.get_top(),self.surr_rect.get_bottom()
        elif np.array_equal(direction,DOWN):
            start,end = self.parent.surr_rect.get_bottom(),self.surr_rect.get_top()
        elif np.array_equal(direction,LEFT):
            start,end = self.parent.surr_rect.get_left(),self.surr_rect.get_right()
        else:
            start,end = self.parent.surr_rect.get_right(),self.surr_rect.get_left()
        vec = np.dot(end - start,direction) * direction*0.5
        return Line(start,start+vec,**kwargs).add_line_to(end-vec).add_line_to(end)
        
    def _get_timeline_connector(self, **kwargs: object) -> Line:
        """Return the connector line for a timeline node.

    Parameters
    ----------
    kwargs
    Kwargs processed by this operation.
    """
        if self.level == 1:
            if (neighbor:=self.neighbor) is not None:
                start = neighbor.surr_rect.get_right()
            else:
                start = self.parent.surr_rect.get_right()
            end = self.surr_rect.get_left()
            return Line(start,end,**kwargs)

        if self.side == LayoutDirection.BottomToTop:
            start = self.parent.surr_rect.get_top()
        elif self.side == LayoutDirection.TopToBottom:
            start = self.parent.surr_rect.get_bottom()
        start +=  0.25*self.parent.width*LEFT
        end = self.surr_rect.get_left()
        middle = np.array([start[0],end[1],0])
        return Line(start,middle,**kwargs).add_line_to(end)
    
    def _get_catalog_connector(self, **kwargs: object) -> Line:
        """Return the connector line for a catalog node.

    Parameters
    ----------
    kwargs
    Kwargs processed by this operation.
    """
        start = self.parent.surr_rect.get_bottom()
        if self.level == 1:
            end = self.surr_rect.get_top()
            vec = np.dot(end - start,DOWN) * DOWN*0.5
            return Line(start,start+vec,**kwargs).add_line_to(end-vec).add_line_to(end)
        start +=  0.25*self.parent.width*LEFT
        end = self.surr_rect.get_left()
        middle = np.array([start[0],end[1],0])
        return Line(start,middle,**kwargs).add_line_to(end)

    def get_connector(
        self,
        layout_type: LayoutType,
        direction: np.ndarray,
        **kwargs: object,
    ) -> Line:
        """Return the connector from this node to its parent based on layout type.

    Parameters
    ----------
    layout_type
    Layout type parameter for this operation.
    direction
    The direction of the operation.
    kwargs
    Kwargs processed by this operation.
    """
        match layout_type:
            case LayoutType.MindMap:
                return self._get_mindmap_connector(direction,**kwargs)
            case LayoutType.Standard:
                return self._get_mindmap_connector(
                    -direction if self.is_flip else direction,
                    **kwargs
                )
            case LayoutType.TimeLine:
                return self._get_timeline_connector(**kwargs)
            case LayoutType.Catalog:
                return self._get_catalog_connector(**kwargs)
            
    
    def set_connector(self, layout_type: LayoutType, direction: np.ndarray = RIGHT, **kwargs: object) -> None:
        """Set the connector line.

    Parameters
    ----------
    layout_type
    Layout type parameter for this operation.
    direction
    The direction of the operation.
    kwargs
    Kwargs processed by this operation.
    """
        if self.parent is not None and not hasattr(self,'connector'):
            self.connector_style = kwargs
            self.connector = self.get_connector(layout_type,direction,**kwargs)
            self.connector.add_updater(
                lambda m: m.become(
                    self.get_connector(layout_type,direction,**kwargs)
                )
            )
    
    def change_connector(
        self,
        change_dir: bool,
        change_layout: bool,
        layout_type: LayoutType,
        direction: np.ndarray = RIGHT,
        **kwargs: object,
    ) -> None:
        """Change the connector line.

    Parameters
    ----------
    change_dir : bool
    Change dir parameter for this operation.
    change_layout : bool
    Change layout parameter for this operation.
    layout_type : LayoutType
    Layout type parameter for this operation.
    direction : np.ndarray
    The direction of the operation.
    """
        current_style = getattr(self, 'connector_style', None)
        if hasattr(self,'connector') and (
            change_layout or change_dir or kwargs != current_style
        ):
            self.connector.remove_updater(*self.connector.get_updaters())
            self.connector_style = kwargs
            self.connector.add_updater(
                lambda m: m.become(
                    self.get_connector(layout_type,direction,**kwargs)
                )
            )

    def get_node_and_line_without_updater(self) -> Group:
        """Return the node and its connector, removing the connector updater."""
        node_mobj = Group(self.surr_rect,self.vmobject)
        if hasattr(self,'connector'):
            self.connector.remove_updater(*self.connector.get_updaters())
            node_mobj.add(self.connector)
            del self.connector
        return node_mobj
    
    def get_children(self) -> List['Node']:
        """Return all child nodes."""
        return self.children
    
    def get_descendants(self) -> List['Node']:
        """Return all descendant nodes."""
        def descendants_of_node(
            node: Node,
            descendants: list[Node] = []
        ) -> list[Node]:
            """Recursively collect all descendant nodes of a given node.

            Parameters
            ----------
            node : Node
                The starting node.
            descendants : list of Node
                Accumulator list for the result (mutated in place).

            Returns
            -------
            list of Node
                All descendant nodes (children, grandchildren, ...).
            """
            if node.children:
                descendants.extend(node.children)
            for node_ in node.children:
                descendants_of_node(node_,descendants)
            return descendants
        return descendants_of_node(self)
    
    def get_children_mobjects(self) -> Group:
        """Return mobjects for all child nodes."""
        group = Group()
        for node in self.children:
            group.add(node.vmobject,node.surr_rect)
        return group
    
    def get_descendants_mobjects(self) -> Group:
        """Return mobjects for all descendant nodes."""
        def descendants_mobjects_of_node(
            node: Node,
            descendants: Group = Group()
        ) -> Group:
            """Recursively collect all mobjects for descendants of a given node.

            Parameters
            ----------
            node : Node
                The starting node.
            descendants : Group
                Accumulator group for the result (mutated in place).

            Returns
            -------
            Group
                A group containing the mobjects of all descendant nodes.
            """
            for node_ in node.children:
                descendants.add(node_.vmobject,node_.surr_rect)
                descendants_mobjects_of_node(node_,descendants)
            return descendants
        return descendants_mobjects_of_node(self)
    
    def get_root(self) -> 'Node':
        """Return the root node."""
        if self.parent is None:
            return self
        return self.parent.get_root()