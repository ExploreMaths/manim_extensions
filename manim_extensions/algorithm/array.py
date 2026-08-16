# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from .node import *
from typing import List, Iterable, Union

class Array(VMobject):
    """A horizontal array of nodes rendered as a single Manim mobject.

    The array keeps a fixed number of entries and displays each item as a
    :class:`~manim_extensions.algorithm.node.Node` with consistent sizing.

    Parameters
    ----------
    data : list
        Values to display in the array.
    total_width : float or Node, optional
        Total width of the array. If omitted, it is derived from the configured
        node width times the number of elements.
    box_type
        Shape of each node box.
    box_color
        Fill color used for each node.
    text_scale : float, optional
        Scale applied to each node label.
    **kwargs
        Additional arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: ArrayExample

       from manim import *
       from manim_extensions.algorithm.array import Array
       from manim_extensions.algorithm.node import Node

       class ArrayExample(Scene):
           def construct(self):
               data = [10, -5, 3.14, "x"]
               arr = Array(data, total_width=10)
               circle_arr = Array(
                   data, total_width=10, box_type=Circle,
                   box_color=YELLOW, text_scale=1.2,
               ).next_to(arr, DOWN, buff=1)
               self.add(arr, circle_arr)
               self.play(Node.Select(arr[1]))
               self.wait(0.5)
               self.play(Node.Unselect(arr[1]))
               self.play(Node.UpdateValue(arr[0], 42))
               self.wait(1)
       """

    def __init__(
        self,
        data:List[NodeValue],
        total_width:float|Node=None,
        box_type=NodeConfig.BOX_TYPE,
        box_color=NodeConfig.BOX_COLOR,
        text_scale:float = 1.0,
        **kwargs
    ):
        """Initialize Array."""
        super().__init__(**kwargs)
        if total_width is None:
            total_width = NodeConfig.WIDTH * len(data)
   
        item_width = total_width / len(data)
        self.array = [
            Node(item, width=item_width, text_scale=text_scale, box_type=box_type, box_color=box_color)
            for item in data
        ]
        self.add(*self.array)
        self.arrange(buff=0)

    @property
    def values(self) -> List[NodeValue]:
        """Return the stored values from each node in the array."""
        return [item.value for item in self.array]

    def __getitem__(self, key: Union[int, slice]) -> Node:
        """Return the node at *key* or a slice of nodes.

        Parameters
        ----------
        key : int or slice
            The index or slice selecting the target node or nodes.

        Returns
        -------
        Node
            The selected node or a new array slice.
        """
        if isinstance(key, slice):
            return Array(self.array[key])
        return self.array[key]

    def __len__(self) -> int:
        """Return the number of elements stored in the array."""
        return len(self.array)