# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Mindmap base classes for Manim.

This module provides base classes for mindmap visualizations.
"""

from collections.abc import Generator
from typing import Any, cast

from manim import (
    Group,
    Line,
    ORIGIN,
    Rectangle,
    Tex,
    TexTemplateLibrary,
    VMobject,
)

__all__ = ["NodeMobject", "generate_tree", "AbstractMap"]

import numpy as np

from ..nodes import Node, NodeStyle, bfs_walker, dfs_walker
from ..algorithms.layout import Layout


class NodeMobject:
    """Wrapper for the components of a mind-map node.

    Parameters
    ----------
    vmobject
        The main visual mobject for the node.
    surr_rect
        Surrounding rectangle for the node.
    connector
        Connector line to the parent node.
    text
        Text content of the node.

    Examples
    --------
    .. manim:: NodeMobjectScene
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.mindmap.base import NodeMobject

       class NodeMobjectScene(Scene):
           def construct(self):
               rect = Rectangle(width=2.5, height=1.2, color=BLUE)
               rect.to_edge(LEFT, buff=1.0)
               line = Line(rect.get_right(), rect.get_right() + 2 * RIGHT, color=GREY)
               tex = Tex("x", font_size=48).move_to(rect)
               nm = NodeMobject(vmobject=tex, surr_rect=rect, connector=line, text="the letter x")
               caption = Text(f"nm.text = {nm.text!r}", font_size=24).to_edge(DOWN)
               self.add(nm.connector, nm.surr_rect, nm.vmobject, caption)
    """

    __slots__ = ["vmobject", "surr_rect", "connector", "text"]

    def __init__(
        self,
        vmobject: VMobject,
        surr_rect: Rectangle,
        connector: Line | None,
        text: str | None,
    ) -> None:
        self.vmobject = vmobject
        self.surr_rect = surr_rect
        self.connector = connector
        self.text = text


def generate_tree(
    Map: dict[Any, Any] | None = None,
    node_style: NodeStyle = NodeStyle(),
    buff: float = 0.2,
) -> Node:
    """Recursively traverse ``Map`` and return the root node of the generated tree.

    ``text``: narration text that can be used for text-to-speech synthesis.

    Parameters
    ----------
    Map
        Dictionary describing the tree: a ``"node"`` mobject (or a string
        rendered with the ctex template) and an optional ``"child"`` list of
        nested dictionaries.
    node_style
        :class:`~manim_extensions.mindmap.nodes.node.Node` style parameter for this operation.
    buff
        Buff parameter for this operation.

    Returns
    -------
        The root node of the generated tree.

    Raises
    ------
    ValueError
        Raised when ``Map`` is not a dictionary.
    """

    def _generate_tree(
        ID: tuple[Any, ...] = (0,), current_map: dict[Any, Any] | None = None
    ) -> Node:
        """Recursively build a :class:`~manim_extensions.mindmap.nodes.node.Node` tree from a dictionary map.

        Parameters
        ----------
        ID
            Hierarchical index tuple for the current node.
        current_map
            Dictionary describing the node and its children.

        Returns
        -------
            The root of the generated subtree.

        Raises
        ------
        ValueError
            Raised when ``current_map`` is not a dictionary.
        """
        if current_map is None:
            raise ValueError("current_map must be a dictionary describing the node")
        level = len(ID)
        mobj = _generate_node(Mobj=current_map["node"], level=level)
        current_node = Node(mobj, buff, **node_style.get_node_style(level=level))
        cast(Any, current_node).ID = ID
        cast(Any, current_node).text = cast(Any, current_map).get("text", None)

        if "child" in current_map:
            for index, child_map in enumerate(current_map["child"]):
                child_node = _generate_tree(ID=(*ID, index), current_map=child_map)
                current_node.add_child(child_node)

        return current_node

    def _generate_node(Mobj: VMobject | str, level: int = 1) -> VMobject:
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

    if Map is None:
        raise ValueError("Map must be a dictionary describing the tree")
    return _generate_tree(ID=(0,), current_map=Map)


class AbstractMap(Group):
    """Abstract base class for mind maps, timelines, etc.

    .. doc-example-covers: bfs_walker, custom_walker, dfs_walker, get_all_mindmap, get_children, get_connector, get_descendants, get_node, get_node_component, get_submindmap


    Parameters
    ----------
    layout_method
        :class:`~manim_extensions.mindmap.algorithms.layout.Layout` algorithm used to position nodes.

    Examples
    --------
    .. manim:: AbstractMapScene
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import bfs_walker
       from manim_extensions.mindmap.mindmap.base import AbstractMap, NodeMobject, generate_tree
       from manim_extensions.mindmap.algorithms import LayoutConfig, TidyTreeLayout

       class AbstractMapScene(Scene):
           def construct(self):
               class SimpleMap(AbstractMap):
                   def _set_connectors(self):
                       for node in bfs_walker(self.root):
                           self.node_data_dict[node.ID] = NodeMobject(
                               node.vmobject, node.surr_rect, None, node.text)
               data = {
                   "node": Tex("Root"),
                   "child": [{"node": Tex("A")}, {"node": Tex("B")}],
               }
               root = generate_tree(Map=data)
               config = LayoutConfig(direction=RIGHT).mindmap
               mind_map = SimpleMap(TidyTreeLayout(root, **config))
               mind_map.scale_to_fit_width(10)
               self.add(mind_map)
    """

    node_style: NodeStyle

    def __init__(self, layout_method: Layout = Layout()) -> None:
        super().__init__()
        self.node_data_dict: dict[Any, NodeMobject] = {}
        self.root: Node = cast(Node, layout_method.layout())
        self._set_node_position(self.root)
        self._set_connectors()
        self.add(*self.get_all_mindmap())
        self.move_to(ORIGIN)

    def _set_node_position(self, node: Node) -> Any:
        """Recursively position a node and all its descendants.

        Parameters
        ----------
        node
            The root of the subtree to position.


        Returns
        -------
                The resulting value.
        """
        pos = np.array([node.x, node.y, 0])
        cast(Any, node.vmobject).move_to(pos)
        node.surr_rect.move_to(pos)
        for child in node.children:
            self._set_node_position(child)

    def _set_connectors(self) -> Any:
        """Set connection lines.


        Returns
        -------
            The resulting value.

        Raises
        ------
        NotImplementedError
            Always, because subclasses must implement this method.
        """
        raise NotImplementedError

    def get_node_component(self, ID: Any) -> NodeMobject | None:
        """Return the full component object of the node with the given ID.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            The component wrapper of the node, or ``None`` if no node with
            the given ID exists.
        """
        return self.node_data_dict.get(ID, None)

    def get_node(self, ID: Any) -> Group | None:
        """Return the VMobject and surrounding rectangle for a node ID.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            A group of the node's VMobject and surrounding rectangle, or
            ``None`` if no node with the given ID exists.
        """
        node = self.node_data_dict.get(ID, None)
        if node is not None:
            return Group(node.vmobject, node.surr_rect)
        return None

    def get_text(self, ID: Any) -> str | None:
        """Return the narration text for a node ID.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            The narration text of the node, or ``None`` if no node with the
            given ID exists.
        """
        node = self.node_data_dict.get(ID, None)
        if node is not None:
            return node.text
        return None

    def get_connector(self, ID: Any) -> Line | None:
        """Return the connector line for a node ID.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            The connector line of the node, or ``None`` if no node with the
            given ID exists.
        """
        node = self.node_data_dict.get(ID, None)
        if node is not None:
            return node.connector
        return None

    def get_all_mindmap(self) -> Group:
        """Return all node and connector mobjects in the mind map.

        Returns
        -------
            A group of every node's VMobject and surrounding rectangle,
            including connector lines where present.
        """
        all_mobjects = Group()
        for node in self.node_data_dict.values():
            if node.connector is not None:
                all_mobjects.add(node.vmobject, node.surr_rect, node.connector)
            else:
                all_mobjects.add(node.vmobject, node.surr_rect)
        return all_mobjects

    def bfs_walker(self) -> Generator[NodeMobject, None, None]:
        """Breadth-first traversal.

        Yields
        -------
            A generator yielding the :class:`~manim_extensions.mindmap.mindmap.base.NodeMobject` of each node in
            breadth-first order.
        """
        for node in bfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def dfs_walker(self) -> Generator[NodeMobject, None, None]:
        """Depth-first traversal.

        Yields
        -------
            A generator yielding the :class:`~manim_extensions.mindmap.mindmap.base.NodeMobject` of each node in
            depth-first pre-order.
        """
        for node in dfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def custom_walker(
        self, id_list: list[Any]
    ) -> Generator[NodeMobject | None, None, None]:
        """Custom traversal.

        Parameters
        ----------
        id_list
            Id list parameter for this operation.

        Yields
        -------
            A generator yielding the :class:`~manim_extensions.mindmap.mindmap.base.NodeMobject` of each node in
            ``id_list`` order, or ``None`` for unknown IDs.
        """
        for id in id_list:
            yield self.node_data_dict.get(id, None)

    def _get_origin_node(self, ID: Any) -> Node | None:
        """Find the node with the given ID in the original tree.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            The original node with that ID, or ``None`` when it is absent.
        """
        for node in dfs_walker(self.root):
            if node.ID == ID:
                return node
        return None

    def _get_connector_style(self, level: int) -> dict[Any, Any]:
        """Return the line style for the given level.

        Parameters
        ----------
        level
            Level parameter for this operation.

        Returns
        -------
            The connector style dictionary for that level.
        """
        return self.node_style.get_line_style(level=level)

    def get_children(self, ID: Any) -> Group:
        """Return the child nodes of the node with the given ID.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            A group of the children's VMobjects and surrounding rectangles,
            or an empty group if no node with the given ID exists.
        """
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_children_mobjects()

    def get_submindmap(self, ID: Any) -> Group:
        """Return the subtree rooted at the node with the given ID.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            A group of the VMobjects and surrounding rectangles of the node
            and all its descendants, including connector lines where
            present, or an empty group if no node with the given ID exists.
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

    def get_descendants(self, ID: Any) -> Group:
        """Return all descendants of the node with the given ID.

        Parameters
        ----------
        ID
            Id parameter for this operation.

        Returns
        -------
            A group of the descendants' VMobjects and surrounding
            rectangles, or an empty group if no node with the given ID
            exists.
        """
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_descendants_mobjects()
