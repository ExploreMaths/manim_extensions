# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *

__all__ = ["NodeMobject", "generate_tree", "AbstractMap"]
from typing import Generator, List, Dict

import numpy as np
from manim.constants import *
from manim.utils.color import *

from ..nodes import Node, NodeStyle, bfs_walker, dfs_walker
from ..algorithms import Layout


class NodeMobject:
    """Wrapper for the components of a mind-map node.

    Parameters
    ----------
    vmobject : VMobject
        The main visual mobject for the node.
    surr_rect : Rectangle
        Surrounding rectangle for the node.
    connector : Line
        Connector line to the parent node.
    text : str
        Text content of the node.

    Examples
    --------
    .. manim:: NodeMobjectExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.mindmap.base import NodeMobject

       class NodeMobjectExample(Scene):
           def construct(self):
               rect = Rectangle()
               line = Line(LEFT, RIGHT)
               tex = Tex("x")
               nm = NodeMobject(rect, rect, line, "x")
               self.add(rect)
    """

    __slots__ = ["vmobject", "surr_rect", "connector", "text"]

    def __init__(
        self, vmobject: VMobject, surr_rect: Rectangle, connector: Line, text: str
    ):
        """Initialize the NodeMobject instance."""
        self.vmobject = vmobject
        self.surr_rect = surr_rect
        self.connector = connector
        self.text = text


def generate_tree(
    Map=None, node_style: NodeStyle = NodeStyle(), buff: float = 0.2
) -> Node:
    """Recursively traverse *Map* and return the root node of the generated tree.

    ``text``: narration text that can be used for text-to-speech synthesis.

    Parameters
    ----------
    node_style : NodeStyle
    Node style parameter for this operation.
    buff : float
    Buff parameter for this operation.
    """

    def _generate_tree(ID=(0,), current_map: Dict = None) -> Node:
        """Recursively build a :class:`~manim_extensions.mindmap.nodes.node.Node` tree from a dictionary map.

        Parameters
        ----------
        ID : tuple of int
            Hierarchical index tuple for the current node.
        current_map : Dict
            Dictionary describing the node and its children.

        Returns
        -------
        Node
            The root of the generated subtree.
        """
        level = len(ID)
        mobj = _generate_node(Mobj=current_map["node"], level=level)
        current_node = Node(mobj, buff, **node_style.get_node_style(level=level))
        current_node.ID = ID
        current_node.text = current_map.get("text", None)

        if "child" in current_map:
            for index, child_map in enumerate(current_map["child"]):
                child_node = _generate_tree(ID=(*ID, index), current_map=child_map)
                current_node.add_child(child_node)

        return current_node

    def _generate_node(Mobj, level=1) -> Mobject:
        """Generate a node mobject.

        Parameters
        ----------
        Mobj
        Mobj parameter for this operation.
        level
        Level parameter for this operation.
        """
        if isinstance(Mobj, str):
            Mobj = Tex(
                Mobj,
                tex_template=TexTemplateLibrary.ctex,
                **node_style.get_text_style(level=level),
            )
        return Mobj

    return _generate_tree(ID=(0,), current_map=Map)


class AbstractMap(Group):
    """Abstract base class for mind maps, timelines, etc.

    Parameters
    ----------
    layout_method : Layout, optional
        Layout algorithm used to position nodes. Defaults to ``Layout()``.

    Examples
    --------
    .. manim:: AbstractMapExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.mindmap.base import AbstractMap

       class AbstractMapExample(Scene):
           def construct(self):
               label = Text("AbstractMap base class", font_size=24)
               self.add(label)
    """

    def __init__(self, layout_method: Layout = Layout()):
        """Initialize the AbstractMap instance."""
        super().__init__()
        self.node_data_dict = {}
        self.root = layout_method.layout()
        self._set_node_position(self.root)
        self._set_connectors()
        self.add(*self.get_all_mindmap())
        self.move_to(ORIGIN)

    def _set_node_position(self, node: Node):
        """Recursively position a node and all its descendants.

        Parameters
        ----------
        node : Node
            The root of the subtree to position.
        """
        pos = np.array([node.x, node.y, 0])
        node.vmobject.move_to(pos)
        node.surr_rect.move_to(pos)
        for child in node.children:
            self._set_node_position(child)

    def _set_connectors(self):
        """Set connection lines."""
        raise NotImplementedError

    def get_node_component(self, ID) -> NodeMobject:
        """Return the full component object of the node with the given ID.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        return self.node_data_dict.get(ID, None)

    def get_node(self, ID) -> Group:
        """Return the VMobject and surrounding rectangle of the node with the given ID.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        node = self.node_data_dict.get(ID, None)
        if node is not None:
            return Group(node.vmobject, node.surr_rect)
        return None

    def get_text(self, ID) -> str:
        """Return the narration text of the node with the given ID.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        node = self.node_data_dict.get(ID, None)
        if node is not None:
            return node.text
        return None

    def get_connector(self, ID) -> Line:
        """Return the connector line of the node with the given ID.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        node = self.node_data_dict.get(ID, None)
        if node is not None:
            return node.connector
        return None

    def get_all_mindmap(self) -> Group:
        """Return all node and connector mobjects in the mind map."""
        all_mobjects = Group()
        for node in self.node_data_dict.values():
            if node.connector is not None:
                all_mobjects.add(node.vmobject, node.surr_rect, node.connector)
            else:
                all_mobjects.add(node.vmobject, node.surr_rect)
        return all_mobjects

    def bfs_walker(self) -> Generator:
        """Breadth-first traversal."""
        for node in bfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def dfs_walker(self) -> Generator:
        """Depth-first traversal."""
        for node in dfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def custom_walker(self, id_list: List[tuple]) -> Generator:
        """Custom traversal.

        Parameters
        ----------
        id_list : List[tuple]
        Id list parameter for this operation.
        """
        for id in id_list:
            yield self.node_data_dict.get(id, None)

    def _get_origin_node(self, ID) -> Node:
        """Find the node with the given ID in the original tree.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        for node in dfs_walker(self.root):
            if node.ID == ID:
                return node
        return None

    def _get_connector_style(self, level: int) -> dict:
        """Return the line style for the given level.

        Parameters
        ----------
        level : int
        Level parameter for this operation.
        """
        return self.node_style.get_line_style(level=level)

    def get_children(self, ID) -> Group:
        """Return the child nodes of the node with the given ID.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_children_mobjects()

    def get_submindmap(self, ID) -> Group:
        """Return the subtree rooted at the node with the given ID.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        node = self._get_origin_node(ID)
        mondmap = Group()
        if node is None:
            return mondmap
        for node_ in dfs_walker(node):
            if node_.connector is not None and len(node_.ID) > len(ID):
                mondmap.add(node_.vmobject, node_.surr_rect, node_.connector)
            else:
                mondmap.add(node_.vmobject, node_.surr_rect)
        return mondmap

    def get_descendants(self, ID) -> Group:
        """Return the descendants of the node with the given ID.

        Parameters
        ----------
        ID
        Id parameter for this operation.
        """
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_descendants_mobjects()
