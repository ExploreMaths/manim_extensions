# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Mindmap animations for Manim.

This module provides animations for mindmap visualizations.

"""

from manim import *

__all__ = [
    "LayoutAnimation",
    "RemoveNode",
    "InsertNode",
    "ScaleNode",
    "AlterNode",
]
from typing import List, Dict

from manim.utils.color import *
from manim.constants import *
import numpy as np

from ..algorithms import LayoutFactory, LayoutType, LayoutConfig
from ..nodes import Node, bfs_walker, NodeSate, NodeStyle


def fadeout_of_subtrees(nodes: List[Node] = None) -> FadeOut:
    """FadeOut the given nodes and their subtrees.

    .. manim:: FadeoutOfSubtreesDocExample

       from manim import *
       from manim_extensions.mindmap import Node, InsertNode
       from manim_extensions.mindmap.animations.animations import fadeout_of_subtrees

       class FadeoutOfSubtreesDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               root.add_child(a1)
               self.play(InsertNode(self, {root: [a1]}))
               self.play(fadeout_of_subtrees([a1]))
               self.wait()

    Parameters
    ----------
    nodes : List[Node]
    Nodes processed by this operation.
    """
    mobjs = []
    for node in nodes:
        for node_ in bfs_walker(node):
            node_.x = node_.y = node_.level = 0
            mobjs.extend([*node_.get_node_and_line_without_updater()])

            if node_.node_state == NodeSate.REMOVE:
                node_.parent = None
            node_.node_state = NodeSate.INSERT
    return FadeOut(*mobjs)


def animate_of_create(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles: Dict,
    node_styles: Dict,
    layout_type: LayoutType,
) -> List[Animation]:
    """Create-node animation.

    .. manim:: AnimateOfCreateDocExample

       from manim import *
       from manim_extensions.mindmap import Node
       from manim_extensions.mindmap.algorithms import LayoutType
       from manim_extensions.mindmap.animations.animations import animate_of_create

       class AnimateOfCreateDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               anims = animate_of_create(
                   root, root.vmobject.get_center(), RIGHT,
                   {'color': WHITE, 'stroke_width': 4},
                   {'color': BLUE, 'stroke_width': 2},
                   LayoutType.MindMap
               )
               self.play(*anims)
               self.wait()

    Parameters
    ----------
    node : Node
    Node parameter for this operation.
    pos : np.ndarray
    Position value used by this operation.
    direction : np.ndarray
    The direction of the operation.
    line_styles : Dict
    Line styles processed by this operation.
    node_styles : Dict
    Node styles processed by this operation.
    layout_type : LayoutType
    Layout type parameter for this operation.
    """
    anims = []
    node.set_connector(layout_type, direction, **line_styles)
    if isinstance(node.vmobject, ImageMobject):
        AnimateClass = FadeIn
    elif isinstance(node.vmobject, (Tex, MathTex)):
        AnimateClass = Write
    else:
        AnimateClass = Create
    anims.extend(
        [
            AnimateClass(node.vmobject.move_to(pos)),
            Create(
                node.surr_rect.become(
                    Rectangle(
                        height=node.height, width=node.width, **node_styles
                    ).move_to(pos)
                )
            ),
        ]
    )
    if hasattr(node, "connector"):
        anims.append(Create(node.connector))
    node.node_state = NodeSate.DISPLAY
    return anims


def animate_of_display(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles: Dict,
    node_styles: Dict,
    layout_type: LayoutType,
    change_dir: bool,
    change_layout: bool,
) -> List[Animation]:
    """Animation for a node already on the scene: update its position and style.

    .. manim:: AnimateOfDisplayDocExample

       from manim import *
       from manim_extensions.mindmap import Node
       from manim_extensions.mindmap.nodes import NodeSate
       from manim_extensions.mindmap.algorithms import LayoutType
       from manim_extensions.mindmap.animations.animations import animate_of_display

       class AnimateOfDisplayDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               self.add(root.vmobject, root.surr_rect)
               root.node_state = NodeSate.DISPLAY
               anims = animate_of_display(
                   root, root.vmobject.get_center() + RIGHT, RIGHT,
                   {'color': WHITE, 'stroke_width': 4},
                   {'color': BLUE, 'stroke_width': 2},
                   LayoutType.MindMap, False, False
               )
               self.play(*anims)
               self.wait()

    Parameters
    ----------
    node : Node
    Node parameter for this operation.
    pos : np.ndarray
    Position value used by this operation.
    direction : np.ndarray
    The direction of the operation.
    line_styles : Dict
    Line styles processed by this operation.
    node_styles : Dict
    Node styles processed by this operation.
    layout_type : LayoutType
    Layout type parameter for this operation.
    change_dir : bool
    Change dir parameter for this operation.
    change_layout : bool
    Change layout parameter for this operation.
    """
    anims = [
        node.vmobject.animate.move_to(pos),
        node.surr_rect.animate.become(
            Rectangle(height=node.height, width=node.width, **node_styles).move_to(pos)
        ),
    ]
    node.change_connector(
        change_dir, change_layout, layout_type, direction, **line_styles
    )
    return anims


def animate_of_scale(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles: Dict,
    node_styles: Dict,
    layout_type: LayoutType,
    change_dir: bool,
    change_layout: bool,
) -> List[Animation]:
    """Animation for a node already on the scene: scale it up or down.

    .. manim:: AnimateOfScaleDocExample

       from manim import *
       from manim_extensions.mindmap import Node, InsertNode
       from manim_extensions.mindmap.nodes import NodeSate
       from manim_extensions.mindmap.algorithms import LayoutType
       from manim_extensions.mindmap.animations.animations import animate_of_scale

       class AnimateOfScaleDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               self.play(InsertNode(self, {root: [a1]}))
               a1.node_state = NodeSate.SCALE
               a1.scale(1.5)
               anims = animate_of_scale(
                   a1, a1.vmobject.get_center(), RIGHT,
                   {'color': WHITE, 'stroke_width': 4},
                   {'color': BLUE, 'stroke_width': 2},
                   LayoutType.MindMap, False, False
               )
               self.play(*anims)
               self.wait()

    Parameters
    ----------
    node : Node
    Node parameter for this operation.
    pos : np.ndarray
    Position value used by this operation.
    direction : np.ndarray
    The direction of the operation.
    line_styles : Dict
    Line styles processed by this operation.
    node_styles : Dict
    Node styles processed by this operation.
    layout_type : LayoutType
    Layout type parameter for this operation.
    change_dir : bool
    Change dir parameter for this operation.
    change_layout : bool
    Change layout parameter for this operation.
    """
    anims = [
        node.vmobject.animate.scale(node.scale_factor).move_to(pos),
        node.surr_rect.animate.become(
            Rectangle(height=node.height, width=node.width, **node_styles).move_to(pos)
        ),
    ]
    node.change_connector(
        change_dir, change_layout, layout_type, direction, **line_styles
    )
    node.node_state = NodeSate.DISPLAY
    return anims


def animate_of_alter(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles: Dict,
    node_styles: Dict,
    layout_type: LayoutType,
    change_dir: bool,
    change_layout: bool,
) -> List[Animation]:
    """Animation for a node already on the scene: replace its vmobject.

    .. manim:: AnimateOfAlterDocExample

       from manim import *
       from manim_extensions.mindmap import Node, InsertNode
       from manim_extensions.mindmap.nodes import NodeSate
       from manim_extensions.mindmap.algorithms import LayoutType
       from manim_extensions.mindmap.animations.animations import animate_of_alter

       class AnimateOfAlterDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               self.play(InsertNode(self, {root: [a1]}))
               a1.node_state = NodeSate.ALTER
               a1.alter_content(MathTex(r"\text{Updated}", font_size=36))
               anims = animate_of_alter(
                   a1, a1.vmobject.get_center(), RIGHT,
                   {'color': WHITE, 'stroke_width': 4},
                   {'color': BLUE, 'stroke_width': 2},
                   LayoutType.MindMap, False, False
               )
               self.play(*anims)
               self.wait()

    Parameters
    ----------
    node : Node
    Node parameter for this operation.
    pos : np.ndarray
    Position value used by this operation.
    direction : np.ndarray
    The direction of the operation.
    line_styles : Dict
    Line styles processed by this operation.
    node_styles : Dict
    Node styles processed by this operation.
    layout_type : LayoutType
    Layout type parameter for this operation.
    change_dir : bool
    Change dir parameter for this operation.
    change_layout : bool
    Change layout parameter for this operation.
    """
    anims = [
        node.vmobject.animate.become(node.alter_vmobject.move_to(pos)),
        node.surr_rect.animate.become(
            Rectangle(height=node.height, width=node.width, **node_styles).move_to(pos)
        ),
    ]
    node.node_state = NodeSate.DISPLAY
    node.change_connector(
        change_dir, change_layout, layout_type, direction, **line_styles
    )
    return anims


def animate_of_node(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles: Dict,
    node_styles: Dict,
    layout_type: LayoutType,
    change_dir: bool,
    change_layout: bool,
) -> List[Animation]:
    """Return the appropriate animation for node based on its state.

    .. manim:: AnimateOfNodeDocExample

       from manim import *
       from manim_extensions.mindmap import Node
       from manim_extensions.mindmap.algorithms import LayoutType
       from manim_extensions.mindmap.animations.animations import animate_of_node

       class AnimateOfNodeDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               anims = animate_of_node(
                   root, root.vmobject.get_center(), RIGHT,
                   {'color': WHITE, 'stroke_width': 4},
                   {'color': BLUE, 'stroke_width': 2},
                   LayoutType.MindMap, False, False
               )
               self.play(*anims)
               self.wait()

    Parameters
    ----------
    node : Node
    Node parameter for this operation.
    pos : np.ndarray
    Position value used by this operation.
    direction : np.ndarray
    The direction of the operation.
    line_styles : Dict
    Line styles processed by this operation.
    node_styles : Dict
    Node styles processed by this operation.
    layout_type : LayoutType
    Layout type parameter for this operation.
    change_dir : bool
    Change dir parameter for this operation.
    change_layout : bool
    Change layout parameter for this operation.
    """
    args = (node, pos, direction, line_styles, node_styles, layout_type)
    match node.node_state:
        case NodeSate.INSERT:
            anims = animate_of_create(*args)
        case NodeSate.DISPLAY:
            anims = animate_of_display(*args, change_dir, change_layout)
        case NodeSate.SCALE:
            anims = animate_of_scale(*args, change_dir, change_layout)
        case NodeSate.ALTER:
            anims = animate_of_alter(*args, change_dir, change_layout)
    return anims


def is_layout_change(root: Node, layout_type: LayoutType) -> bool:
    """
    Check whether the layout algorithm has changed.

    Parameters
    ----------
    root : Node
        The root node (before first layout, or after a layout has been applied)
    layout_type : LayoutType
        The layout method to be used
    Returns (bool): Whether the layout algorithm has changed


    """
    origin_layout = getattr(root, "layout_type", None)
    if origin_layout is not None:
        return origin_layout != layout_type
    return False


def is_direction_change(root: Node, direction=RIGHT) -> bool:
    """
    Check whether the layout direction has changed.

    Parameters
    ----------
    root : Node
        The root node (before first layout, or after a layout has been applied)
    direction
        The layout direction to be used
    Returns (bool): Whether the layout direction has changed


    """
    origin_dir = getattr(root, "direction", None)
    if origin_dir is not None:
        return not np.array_equal(origin_dir, direction)
    return False


def animate_of_layout(
    root: Node,
    remove_nodes: List[Node] = None,
    layout_type: LayoutType = LayoutType.MindMap,
    layout_config: LayoutConfig = LayoutConfig(),
    node_style: NodeStyle = NodeStyle(),
) -> List[Animation]:
    """Core animation method: run the full Layout algorithm and generate animations.

    .. manim:: AnimateOfLayoutDocExample

       from manim import *
       from manim_extensions.mindmap import Node
       from manim_extensions.mindmap.algorithms import LayoutConfig, LayoutType
       from manim_extensions.mindmap.animations.animations import animate_of_layout

       class AnimateOfLayoutDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               root.add_child(a1)
               anims = animate_of_layout(root, layout_type=LayoutType.MindMap, layout_config=LayoutConfig())
               self.play(*anims)
               self.wait()

    Parameters
    ----------
    root : Node
    Root parameter for this operation.
    remove_nodes : List[Node]
    Remove nodes processed by this operation.
    layout_type : LayoutType
    Layout type parameter for this operation.
    layout_config : LayoutConfig
    Layout config parameter for this operation.
    node_style : NodeStyle
    Node style parameter for this operation.
    """
    direction = layout_config.direction
    change_dir = is_direction_change(root, direction)
    change_layout = is_layout_change(root, layout_type)
    current_x, current_y, _ = root.vmobject.get_center()
    layout = LayoutFactory.create_layout(layout_type, root, layout_config)
    root = layout.layout()
    setattr(root, "layout_type", layout_type)
    setattr(root, "direction", direction)
    x_offset = current_x - root.x
    y_offset = current_y - root.y
    anims = [fadeout_of_subtrees(remove_nodes)] if remove_nodes else []

    for node in bfs_walker(root):
        node.x += x_offset
        node.y += y_offset
        node_styles = node_style.get_node_style(node.level)
        line_styles = node_style.get_line_style(node.level)
        pos = np.array([node.x, node.y, 0])
        anims.extend(
            animate_of_node(
                node,
                pos,
                direction,
                line_styles,
                node_styles,
                layout_type,
                change_dir,
                change_layout,
            )
        )
        node.x = node.y = 0
    return anims


class AbstractLayoutAnimation(AnimationGroup):
    """Abstract base class for layout animations: collect node states and generate the full layout animation.

    .. manim:: AbstractLayoutAnimationDocExample

       from manim import *
       from manim_extensions.mindmap import Node
       from manim_extensions.mindmap.animations.animations import AbstractLayoutAnimation

       class AbstractLayoutAnimationDocExample(Scene):
           def construct(self):
               class DemoAnimation(AbstractLayoutAnimation):
                   def collect_animations(self):
                       return []

               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               self.play(DemoAnimation(self, root))
               self.wait()

    Parameters
    ----------
        scene : Scene
            The current scene
        root : Node
            The root node
        layout_type : LayoutType, optional
            Layout type. Defaults to LayoutType.MindMap.
        layout_config : LayoutConfig, optional
            Layout parameters. Defaults to LayoutConfig().
        node_style : NodeStyle, optional
            Layout and node styles. Defaults to NodeStyle()."""

    def __init__(
        self,
        scene: Scene,
        root: Node,
        layout_type: LayoutType = LayoutType.MindMap,
        layout_config: LayoutConfig = LayoutConfig(),
        node_style: NodeStyle = NodeStyle(),
        **kwargs,
    ):
        """Initialize AbstractLayoutAnimation."""
        self.scene = scene
        self.root = root
        self.layout_type = layout_type
        self.layout_config = layout_config
        self.node_style = node_style
        anims = self.collect_animations()
        super().__init__(*anims, **kwargs)

    def _check_node_state(self) -> List[Node]:
        """Check the state of each node and return the nodes to be removed."""
        remove_nodes = []
        for node in bfs_walker(self.root):
            if node.vmobject not in self.scene.get_mobject_family_members():
                match node.node_state:
                    case NodeSate.INSERT:
                        pass
                    case NodeSate.DISPLAY:
                        node.node_state = NodeSate.INSERT
                    case NodeSate.REMOVE:
                        raise Exception(
                            f"{node.vmobject} is not on current scene,the animation of remove node is not supported"
                        )
                    case NodeSate.SCALE:
                        raise Exception(
                            f"{node.vmobject} is not on current scene,the animation of scale node is not supported"
                        )
                    case _:
                        raise Exception(
                            f"{node.vmobject} is not on current scene,the animation of alter node is not supported"
                        )
            else:
                match node.node_state:
                    case NodeSate.INSERT:
                        node.node_state = NodeSate.DISPLAY
                    case NodeSate.REMOVE:
                        parent = node.parent
                        if parent is None:
                            remove_nodes.append(node)
                            continue
                        try:
                            idx = parent.children.index(node)
                            if (child_num := len(parent.children)) > 1:
                                if idx == 0:
                                    parent.children[1].neighbor = None
                                elif idx < child_num - 1:
                                    parent.children[idx + 1].neighbor = parent.children[
                                        idx - 1
                                    ]
                            parent.children.remove(node)
                            node.neighbor = None
                            remove_nodes.append(node)
                        except ValueError:
                            raise ValueError(f"Node {node} is not a child of {parent}")
                    case NodeSate.SCALE | NodeSate.DISPLAY | NodeSate.ALTER:
                        pass
        return remove_nodes

    def collect_animations(self) -> List[Animation]:
        """Collect animations: must be implemented by subclasses."""
        raise NotImplementedError

    def get_common_root(self, nodes: List[Node]) -> Node:
        """Return the common root of nodes.

        Parameters
        ----------
        nodes : List[Node]
        Nodes processed by this operation.
        """
        root = nodes[0].get_root()
        if len(nodes) == 1:
            return root
        if not all(node.get_root() is root for node in nodes[1::]):
            return None
        return root


class LayoutAnimation(AbstractLayoutAnimation):
    r"""General layout animation: apply a layout to the whole tree and play all change animations.

    .. manim:: LayoutAnimationDocExample

       from manim import *
       from manim_extensions.mindmap import Node, LayoutAnimation

       class LayoutAnimationDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               a2 = Node(MathTex(r"\text{A2}", font_size=36))
               root.add_child(a1)
               root.add_child(a2)
               self.play(LayoutAnimation(self, root))
               self.wait()
    """

    def __init__(
        self,
        scene: Scene,
        root: Node,
        layout_type: LayoutType = LayoutType.MindMap,
        layout_config: LayoutConfig = LayoutConfig(),
        node_style: NodeStyle = NodeStyle(),
        **kwargs,
    ):
        """Initialize the LayoutAnimation instance."""
        super().__init__(
            scene,
            root,
            layout_type=layout_type,
            layout_config=layout_config,
            node_style=node_style,
            **kwargs,
        )

    def collect_animations(self):
        """Collect the animations needed to re-layout the mind map.

        Returns
        -------
        tuple of Animation
            The layout animations.
        """
        remove_nodes = self._check_node_state()
        return animate_of_layout(
            self.root,
            remove_nodes,
            self.layout_type,
            self.layout_config,
            self.node_style,
        )


class RemoveNode(LayoutAnimation):
    r"""Remove the tree or subtree rooted at nodes; nodes may be a single node or a list of nodes.

    .. manim:: RemoveNodeDocExample

       from manim import *
       from manim_extensions.mindmap import Node, InsertNode, RemoveNode

       class RemoveNodeDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               a2 = Node(MathTex(r"\text{A2}", font_size=36))
               self.play(InsertNode(self, {root: [a1, a2]}))
               self.play(RemoveNode(self, [a1, a2]))
               self.wait()
    """

    def __init__(
        self,
        scene: Scene,
        nodes: Node | List[Node],
        layout_type: LayoutType = LayoutType.MindMap,
        layout_config: LayoutConfig = LayoutConfig(),
        node_style: NodeStyle = NodeStyle(),
        **kwargs,
    ):
        """Initialize the RemoveNode instance."""
        self.is_whole_tree = False
        if isinstance(nodes, Node):
            nodes = (nodes,)
        root = self.get_common_root(nodes)
        if root is None:
            raise Exception("nodes must be in the same tree")
        for node in nodes:
            if (parent := node.parent) is None:
                self.is_whole_tree = True
                break
            else:
                parent.remove_child(node)
        super().__init__(
            scene,
            root,
            layout_type=layout_type,
            layout_config=layout_config,
            node_style=node_style,
            **kwargs,
        )

    def collect_animations(self):
        """Collect animations for removing nodes (or the whole tree).

        Returns
        -------
        tuple of Animation
            Either a fade-out animation for the whole tree or the standard
            layout animation.
        """
        if self.is_whole_tree:
            tree = self._get_whole_tree()
            if len(tree) == 0:
                raise Exception(f"the root {self.root} is not on current scene")
            return (FadeOut(*tree),)
        else:
            return super().collect_animations()

    def _get_whole_tree(self) -> Group:
        """Collect all mobjects belonging to the whole tree for removal.

        Returns
        -------
        Group
            A group of node mobjects to fade out.
        """
        group = Group()
        for node in bfs_walker(self.root):
            if node.vmobject not in self.scene.get_mobject_family_members():
                continue
            node.node_state = NodeSate.INSERT
            group.add(*node.get_node_and_line_without_updater())
        return group


class InsertNode(LayoutAnimation):
    """Insert one or more child nodes into the mind map.

    .. manim:: InsertNodeDocExample

       from manim import *
       from manim_extensions.mindmap import Node, InsertNode

       class InsertNodeDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               a2 = Node(MathTex(r"\text{A2}", font_size=36))
               self.play(InsertNode(self, {root: [a1, a2]}))
               self.wait()

    Parameters
    ----------
        father_children : dict
            dictionary mapping parent nodes to lists of child nodes"""

    def __init__(
        self,
        scene: Scene,
        father_children: Dict[Node, List[Node]] = None,
        layout_type: LayoutType = LayoutType.MindMap,
        layout_config: LayoutConfig = LayoutConfig(),
        node_style: NodeStyle = NodeStyle(),
        **kwargs,
    ):
        """Initialize InsertNode."""
        root = None
        self.father_children = father_children
        super().__init__(
            scene,
            root,
            layout_type=layout_type,
            layout_config=layout_config,
            node_style=node_style,
            **kwargs,
        )

    def get_root(self, nodes: List[Node]):
        """Return the common root of the given nodes.

        Parameters
        ----------
        nodes : List of Node
            Nodes to find the common root for.

        Returns
        -------
        Node
            The common ancestor node.

        Raises
        ------
        Exception
            If the list is empty or the nodes share no common root.
        """
        if len(nodes) == 0:
            raise Exception("father_children is empty")
        root = self.get_common_root(nodes)
        if root is None:
            raise Exception("all fathers must be in the same tree")
        return root

    def collect_animations(self) -> List[Animation]:
        """Collect animations for inserting new nodes into the mind map.

        Returns
        -------
        list of Animation
            The layout animations after adding children.
        """
        for father, children in self.father_children.items():
            if children:
                for child in children:
                    father.add_child(child)
        self.root = self.get_root(list(self.father_children.keys()))
        return super().collect_animations()


class ScaleNode(LayoutAnimation):
    """Scale one or more nodes in the mind map.

    .. manim:: ScaleNodeDocExample

       from manim import *
       from manim_extensions.mindmap import Node, InsertNode, ScaleNode

       class ScaleNodeDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               self.play(InsertNode(self, {root: [a1]}))
               self.play(ScaleNode(self, {a1: 1.5}))
               self.wait()

    Parameters
    ----------
        node_scale : dict
            dictionary mapping Node instances to scale factors (float)"""

    def __init__(
        self,
        scene: Scene,
        node_scale: Dict[Node, float] = None,
        layout_type: LayoutType = LayoutType.MindMap,
        layout_config: LayoutConfig = LayoutConfig(),
        node_style: NodeStyle = NodeStyle(),
        **kwargs,
    ):
        """Initialize ScaleNode."""
        for node, scale in node_scale.items():
            node.scale(scale)
        root = self.get_common_root(list(node_scale.keys()))
        super().__init__(
            scene,
            root,
            layout_type=layout_type,
            layout_config=layout_config,
            node_style=node_style,
            **kwargs,
        )


class AlterNode(LayoutAnimation):
    """Replace the content of one or more nodes in the mind map.

    .. manim:: AlterNodeDocExample

       from manim import *
       from manim_extensions.mindmap import Node, InsertNode, AlterNode

       class AlterNodeDocExample(Scene):
           def construct(self):
               root = Node(MathTex(r"\text{Root}", font_size=36).to_edge(LEFT))
               a1 = Node(MathTex(r"\text{A1}", font_size=36))
               self.play(InsertNode(self, {root: [a1]}))
               self.play(AlterNode(self, {a1: MathTex(r"\text{Updated}", font_size=36)}))
               self.wait()

    Parameters
    ----------
        node_vmobject : dict
            dictionary mapping Node instances to the replacement VMobjects"""

    def __init__(
        self,
        scene: Scene,
        node_vmobject: Dict[Node, VMobject] = None,
        layout_type: LayoutType = LayoutType.MindMap,
        layout_config: LayoutConfig = LayoutConfig(),
        node_style: NodeStyle = NodeStyle(),
        **kwargs,
    ):
        """Initialize AlterNode."""
        for node, scale in node_vmobject.items():
            node.alter_content(scale)
        root = self.get_common_root(list(node_vmobject.keys()))
        super().__init__(
            scene,
            root,
            layout_type=layout_type,
            layout_config=layout_config,
            node_style=node_style,
            **kwargs,
        )