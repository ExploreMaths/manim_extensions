# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from typing import List, TypeAlias
from manim import *
from manim.typing import ManimFloat, Point3D, Vector3D
from manim.utils.color import ManimColor
from .utils.numpy_helper import NumpyHelper

NodeValue: TypeAlias = str | int | float | None
NodeBoxType: TypeAlias = type[Square] | type[Circle]


class NodeConfig:
    """Default visual settings shared by algorithm nodes.

    These class attributes hold the default visual configuration that every
    :class:`~manim_extensions.mindmap.nodes.node.Node` (and the data structures built on top of it) reads when an
    argument is not supplied explicitly.  Changing an attribute here changes the
    default appearance of *all* subsequently created nodes, which is the natural
    way to switch the overall look of an algorithm scene.

    .. rubric:: See Also

    :class:`~manim_extensions.mindmap.nodes.node.Node`

    Examples
    --------
    .. manim:: NodeConfigExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.node import Node, NodeConfig

       class NodeConfigExample(Scene):
           def construct(self):
               default_node = Node("default")
               selection_node = Node("selected", box_color=NodeConfig.SELECT_COLOR)
               group = VGroup(default_node, selection_node).arrange(RIGHT, buff=1)
               self.add(group)
    """
    WIDTH = 2
    BOX_TYPE = Square
    BOX_COLOR = WHITE
    SELECT_COLOR = RED
    SELECT_OPACITY = 0.5


class NodeSolt:
    """Convenience container for slot positions around a node.

    Examples
    --------
    .. manim:: NodeSoltExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.node import Node, NodeSolt

       class NodeSoltExample(Scene):
           def construct(self):
               node = Node("A")
               self.add(node)
               direction, _ = NodeSolt.DOWN_MID
               tip = Dot(node.get_critical_point(direction), color=YELLOW)
               self.add(tip)
    """

    SPLIT_PARTS = 12
    MID = SPLIT_PARTS // 2
    LEFT_MID = (LEFT, MID)
    RIGHT_MID = (RIGHT, MID)
    UP_MID = (UP, MID)
    DOWN_MID = (DOWN, MID)
    LEFT_UP = (LEFT, SPLIT_PARTS // 3 * 2)
    LEFT_DOWN = (LEFT, SPLIT_PARTS // 3)
    RIGHT_UP = (RIGHT, SPLIT_PARTS // 3)
    RIGHT_DOWN = (RIGHT, SPLIT_PARTS // 3 * 2)
    UP_LEFT = (UP, SPLIT_PARTS // 3)
    UP_RIGHT = (UP, SPLIT_PARTS // 3 * 2)
    DOWN_LEFT = (DOWN, SPLIT_PARTS // 3 * 2)
    DOWN_RIGHT = (DOWN, SPLIT_PARTS // 3)
    CORNER_LU = (LEFT, SPLIT_PARTS)
    CORNER_LD = (LEFT, 0)
    CORNER_RU = (RIGHT, 0)
    CORNER_RD = (RIGHT, SPLIT_PARTS)


class Node(VMobject):
    """A visual node used in algorithm animations.

    The node is rendered as a box with an optional value label and can be used as
    a building block for arrays, trees, graphs, and queue-like visualisations.

    Parameters
    ----------
    value : str | int | float | None, optional
        Value displayed inside the node. If the value is empty, a zero-radius dot
        is displayed as a placeholder.
    width : float, optional
        Width of the node box. Defaults to ``2``.
    text_scale : float, optional
        Scale factor applied to the displayed text. Defaults to ``1.0``.
    box_type : type, optional
        Shape used for the node box. Must be :class:`~manim.mobject.geometry.polygram.Square` or :class:`~manim.mobject.geometry.arc.Circle`.
    box_color : ManimColor, optional
        Fill color of the node box. Defaults to ``WHITE``.
    **kwargs
        Forwarded to the parent :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Raises
    ------
    ValueError
        Raised when the provided ``box_type`` is not :class:`~manim.mobject.geometry.polygram.Square` or :class:`~manim.mobject.geometry.arc.Circle`.

    Examples
    --------
    .. manim:: NodeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.node import Node

       class NodeExample(Scene):
           def construct(self):
               square_node = Node("42")
               circle_node = Node("?", box_type=Circle, box_color=YELLOW)
               empty_node = Node(None, box_color=BLUE)
               group = VGroup(square_node, circle_node, empty_node).arrange(RIGHT, buff=1)
               self.add(group)
    """

    def __init__(
        self,
        value: NodeValue = None,
        width: float = NodeConfig.WIDTH,
        text_scale:float = 1.0,
        box_type: NodeBoxType = NodeConfig.BOX_TYPE,
        box_color: ManimColor = NodeConfig.BOX_COLOR,
        **kwargs,
    ):
        """Initialize Node."""

        super().__init__(**kwargs)
        self.set_box(box_type, width, box_color)
        self.text_scale = text_scale
        self.set_value(value)
        self.width = width
    
    def set_box(self, box_type: NodeBoxType, width: float, color: ManimColor) -> 'Node':
        """Set the shape and fill colour of the node's box.

        If the node already has a box it is removed first; the new box
        is then added and coloured.

        Parameters
        ----------
        box_type : type
            Box shape, either :class:`~manim.mobject.geometry.polygram.Square`
            or :class:`~manim.mobject.geometry.arc.Circle`.
        width : float
            Width of the box (diameter for :class:`~manim.mobject.geometry.arc.Circle`).
        color : ManimColor
            Fill colour applied to the box.

        Returns
        -------
        Node
            The modified node instance.

        Raises
        ------
        ValueError
            If *box_type* is not :class:`~manim.mobject.geometry.polygram.Square` or :class:`~manim.mobject.geometry.arc.Circle`.
        """
        if hasattr(self, 'box'):
            self.remove(self.box)
        if box_type not in [Square, Circle]:
            raise ValueError("box_type must be Square or Circle")
        if box_type == Square:
            self.box = Square(width)
        elif box_type == Circle:
            self.box = Circle(width / 2)
        self.box.set_color(color)
        self.add(self.box)
        return self

    def get_box(self) -> Mobject:
        """Return the underlying visual box for the node."""
        return self.box

    def set_value(self, value: NodeValue) -> 'Node':
        """Replace the node's displayed content and update the internal value.

        Parameters
        ----------
        value : NodeValue
            The value to display inside the node.
        """
        if hasattr(self, 'text'):
            self.remove(self.text)
        self.value = value
        if value is None or not str(value).strip():
            self.text = Dot(radius=0)
        else:
            self.text = Tex(str(value)).scale(self.text_scale)
        self.text.move_to(self)
        self.add(self.text)
        return self

    def get_value(self) -> NodeValue:
        """Return the underlying data value of the node."""
        return self.value

    def set_fill(self,
        color: ParsableManimColor | None = None,
        opacity: float | None = None,
        family: bool = True,
    ) -> 'Node':
        """Set the fill color and transparency for the node box.

        Parameters
        ----------
        color : ParsableManimColor | None
            The fill color to apply.
        opacity : float | None
            The desired opacity to use.
        family : bool
            Whether to apply the fill to the whole family of mobjects.
        """
        super().set_fill(color, opacity, False)
        if hasattr(self, 'box'):
            self.box.set_fill(color, opacity, family)
        return self

    def get_fill_color(self) -> ManimColor:
        """Return the fill color of the node box."""
        return self.box.get_fill_color()

    def get_fill_opacity(self) -> ManimFloat:
        """Return the fill opacity of the node box."""
        return self.box.get_fill_opacity()

    def get_slot(self, direction: Vector3D, index) -> Point3D:
        """Return a point on the node's boundary at the given slot index.

        The slot numbering scheme divides each edge of the box into
        :attr:`~manim_extensions.algorithm.node.NodeSolt.SPLIT_PARTS` (12) equal segments, numbered
        clockwise from ``0`` to :attr:`~manim_extensions.algorithm.node.NodeSolt.SPLIT_PARTS`.  For circular boxes
        the same mapping is applied to the corresponding quarter-arc.

        Parameters
        ----------
        direction : Vector3D
            One of :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.LEFT`, :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.RIGHT`, :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.UP`, or :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.DOWN`.
        index : int
            Slot number in the range ``0`` to :attr:`~manim_extensions.algorithm.node.NodeSolt.SPLIT_PARTS`.

        Returns
        -------
        Point3D
            The point on the node's boundary at the requested slot.

        Raises
        ------
        ValueError
            If *direction* is not one of the four principal directions
            or if the box type is not supported.
        """

        proportion = 0
        if NumpyHelper.is_same_direction(direction, RIGHT):
            proportion = 0
        elif NumpyHelper.is_same_direction(direction, LEFT):
            proportion = 0.5
        elif NumpyHelper.is_same_direction(direction, UP):
            proportion = 0.75
        elif NumpyHelper.is_same_direction(direction, DOWN):
            proportion = 0.25
        else:
            raise ValueError("direction must be LEFT or RIGHT or UP or DOWN")
        proportion = proportion + index / NodeSolt.SPLIT_PARTS / 4
        if isinstance(self.box, Square):
            pass
        elif isinstance(self.box, Circle):
            proportion -= 0.125
        else:
            raise ValueError("box_type must be Square or Circle")
        proportion = 1 - proportion
        if proportion > 1:
            proportion -= 1
        if proportion < 0:
            proportion += 1
        return self.box.point_from_proportion(proportion)

    def __str__(self) -> str:
        """Return a compact readable representation of the node."""
        return f"Node({repr(self.value)})"

    def __repr__(self) -> str:
        """Return the same value as ``__str__`` for debugging output."""
        return self.__str__()

    class Select(Succession):
        """Highlight one or more nodes by changing their fill color.

        Parameters
        ----------
        *nodes : Node
            One or more :class:`~manim_extensions.mindmap.nodes.node.Node` instances to highlight.
        color : ManimColor, optional
            Fill color used for highlighting. Defaults to
            :attr:`~manim_extensions.algorithm.node.NodeConfig.SELECT_COLOR` (``RED``).
        opacity : float, optional
            Opacity applied to the highlight color. Defaults to
            :attr:`~manim_extensions.algorithm.node.NodeConfig.SELECT_OPACITY` (``0.5``).

        Examples
        --------
        .. manim:: SelectExample

           from manim import *
           from manim_extensions.algorithm.node import Node

           class SelectExample(Scene):
               def construct(self):
                   a = Node("1")
                   b = Node("2").next_to(a, RIGHT)
                   self.add(a, b)
                   self.play(Node.Select(a, b, color=YELLOW, opacity=0.6))
                   self.wait(0.5)
        """

        def __init__(
            self,
            *nodes: List["Node"],
            color: ManimColor = NodeConfig.SELECT_COLOR,
            opacity: float = NodeConfig.SELECT_OPACITY,
            **kwargs,
        ):
            """Initialize Select."""
            
            super().__init__(AnimationGroup(*[node.animate.set_fill(color, opacity) for node in nodes]), **kwargs)

    class Unselect(Succession):
        """Clear the highlight from one or more nodes.

        The animation restores the original fill color of each selected node
        by setting its opacity back to ``0``.

        Parameters
        ----------
        *nodes : Node
            One or more :class:`~manim_extensions.mindmap.nodes.node.Node` instances to unselect.

        Examples
        --------
        .. manim:: UnselectExample

           from manim import *
           from manim_extensions.algorithm.node import Node

           class UnselectExample(Scene):
               def construct(self):
                   a = Node("1")
                   b = Node("2").next_to(a, RIGHT)
                   self.add(a, b)
                   self.play(Node.Select(a, b))
                   self.play(Node.Unselect(a))
                   self.wait(0.5)
        """

        def __init__(self, *nodes: List["Node"], **kwargs):
            """Clear the highlight from one or more nodes.

            Restores each node's original fill colour with zero opacity,
            effectively undoing a previous :class:`~manim_extensions.algorithm.node.Node.Select` animation.
            """
            super().__init__(AnimationGroup(*[node.animate.set_fill(node.get_fill_color(), 0) for node in nodes]), **kwargs)

    class UpdateValue(Succession):
        """Replace the value shown by a node through an animation.

        Parameters
        ----------
        node : Node
            The node whose value will be updated.
        value : NodeValue
            New value to display inside the node.

        Examples
        --------
        .. manim:: UpdateValueExample

           from manim import *
           from manim_extensions.algorithm.node import Node

           class UpdateValueExample(Scene):
               def construct(self):
                   node = Node("1")
                   self.add(node)
                   self.play(Node.UpdateValue(node, "9"))
                   self.wait(0.5)
        """

        def __init__(self, node: "Node", value: NodeValue, **kwargs):
            """Initialize UpdateValue."""
            super().__init__(*[node.animate.set_value(value)], **kwargs)
        
        
    class MoveAndOverWrite(Succession):
        """Move a node into place and overwrite the destination value.

        The animation moves ``node`` to the position of ``target``, then
        replaces the target's displayed value with the source's value and
        fades the source node out.

        Parameters
        ----------
        node : Node
            The node that will be moved and whose value will be copied.
        target : Node
            The destination node that will receive the new value.
        select_color : ManimColor, optional
            If provided, highlights the moving node during the animation.
        select_opacity : float, optional
            Opacity of the selection highlight. Defaults to ``0.2``.

        Examples
        --------
        .. manim:: MoveAndOverWriteExample

           from manim import *
           from manim_extensions.algorithm.node import Node

           class MoveAndOverWriteExample(Scene):
               def construct(self):
                   a = Node("1")
                   b = Node("2").next_to(a, RIGHT)
                   self.add(a, b)
                   self.play(Node.MoveAndOverWrite(a, b))
                   self.wait(0.5)
        """

        def __init__(self, node: "Node", target: "Node", select_color:ManimColor=None, select_opacity:float=0.2, **kwargs):
            """Initialize MoveAndOverWrite."""
            steps = []
            if select_color is not None:
                steps.append(Node.Select(node, color=select_color, opacity=select_opacity))
          
            steps.extend([
                node.animate.move_to(target),
                AnimationGroup(
                    Node.UpdateValue(target, node.value), 
                    FadeOut(node)
                )
            ])
            
            super().__init__(*steps, **kwargs)
        
    class CopyAndOverWrite(Succession):
        """Copy a node into a target location and overwrite its value.

        Unlike :class:`~manim_extensions.algorithm.node.Node.MoveAndOverWrite`, the source node remains in place:
        a copy is created, animated to the target, and then used to
        overwrite the target's value before fading out.

        Parameters
        ----------
        node : Node
            The node whose value will be copied.
        target : Node
            The destination node that will receive the new value.
        select_color : ManimColor, optional
            If provided, highlights the copied node during the animation.
        select_opacity : float, optional
            Opacity of the selection highlight. Defaults to ``0.2``.

        Examples
        --------
        .. manim:: CopyAndOverWriteExample

           from manim import *
           from manim_extensions.algorithm.node import Node

           class CopyAndOverWriteExample(Scene):
               def construct(self):
                   a = Node("1")
                   b = Node("2").next_to(a, RIGHT)
                   self.add(a, b)
                   self.play(Node.CopyAndOverWrite(a, b))
                   self.wait(0.5)
        """

        def __init__(self, node: "Node", target: "Node", select_color:ManimColor=None, select_opacity:float=0.2, **kwargs):
            """Initialize CopyAndOverWrite."""
            copied_node = node.copy().move_to(node)
            steps = [
                FadeIn(copied_node),
                Node.MoveAndOverWrite(copied_node, target, select_color, select_opacity)
            ]
            
            super().__init__(*steps, **kwargs)
    
    class SwapAndOverWrite(Succession):
        """Swap the values of two nodes while preserving the animation sequence.

        Creates temporary copies of both nodes, swaps them visually, and
        then updates the original nodes with the swapped values before
        fading the copies out.

        Parameters
        ----------
        node1 : Node
            First node to swap.
        node2 : Node
            Second node to swap.
        select_color : ManimColor, optional
            If provided, highlights the temporary copies during the swap.
        select_opacity : float, optional
            Opacity of the selection highlight. Defaults to ``0.2``.

        Examples
        --------
        .. manim:: SwapAndOverWriteExample

           from manim import *
           from manim_extensions.algorithm.node import Node

           class SwapAndOverWriteExample(Scene):
               def construct(self):
                   a = Node("1")
                   b = Node("2").next_to(a, RIGHT)
                   self.add(a, b)
                   self.play(Node.SwapAndOverWrite(a, b))
                   self.wait(0.5)
        """

        def __init__(self, node1: "Node", node2: "Node", select_color:ManimColor=None, select_opacity:float=0.2, **kwargs):
            """Initialize SwapAndOverWrite."""
            copied_node1 = node1.copy().move_to(node1)
            copied_node2 = node2.copy().move_to(node2)
            steps = [
                FadeIn(copied_node1, copied_node2),
            ]
            if select_color is not None:
                steps.append(Node.Select(copied_node1, copied_node2, select_color=select_color, select_opacity=select_opacity))
            steps.append(Swap(copied_node1, copied_node2))
            steps.append(AnimationGroup(
                Node.UpdateValue(node1, copied_node2.value),
                Node.UpdateValue(node2, copied_node1.value),
                FadeOut(copied_node1, copied_node2)
            ))
            super().__init__(*steps, **kwargs)