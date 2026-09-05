# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Queue data structure for algorithm visualization."""

from typing import List
from manim import *
from manim.typing import Point3D
from .node import Node


class Queue(VMobject):
    """Visual queue data structure for algorithm demonstrations.

    Parameters
    ----------
    capacity : int
        Maximum number of entries that may be stored.
    init_data : list, optional
        Initial values to render inside the queue.
    total_width : int, optional
        Total width occupied by the queue visualisation.
    font_size : int, optional
        Text size used for embedded nodes.
    box_type
        Shape used for each node box.
    bound_color
        Color applied to the queue boundaries.
    **kwargs
        Additional arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: QueueExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.queue import Queue

       class QueueExample(Scene):
           def construct(self):
               q = Queue(capacity=5, init_data=[1, 2, 3], total_width=8)
               self.add(q)
    """

    def __init__(
        self,
        capacity: int,
        init_data: List[Node] = None,
        total_width: int = 12,
        font_size: int = 48,
        box_type=Square,
        bound_color=RED,
        **kwargs,
    ):
        """Initialize the Queue instance."""
        super().__init__(**kwargs)
        self.capacity = capacity
        self.total_width = total_width
        self.item_width = total_width / capacity
        self.font_size = font_size
        self.upbound = Line(
            LEFT * total_width / 2 + UP / 2 * self.item_width,
            RIGHT * total_width / 2 + UP / 2 * self.item_width,
        ).set_color(bound_color)
        self.downbound = Line(
            LEFT * total_width / 2 + DOWN / 2 * self.item_width,
            RIGHT * total_width / 2 + DOWN / 2 * self.item_width,
        ).set_color(bound_color)
        self.add(self.upbound, self.downbound)
        self.data: List[Node] = []
        if init_data:
            for item in init_data:
                if not isinstance(item, Node):
                    item = Node(item, width=self.item_width, box_type=box_type)
                item.move_to(
                    (self.data[-1].get_right() if self.data else self.get_left())
                    + self.item_width / 2 * RIGHT
                )
                self.add(item)
                self.data.append(item)

    class Enqueue(Succession):
        """Animate an item entering the queue from the right edge.

        The item slides along the queue's interior until it reaches the
        slot right after the last occupied position, and is then appended
        to the queue's internal data.

        Parameters
        ----------
        queue : Queue
            The queue that will receive the new item.
        item : Node
            The node to enqueue. It is placed to the right of the queue
            before the animation starts.

        Examples
        --------
        .. manim:: EnqueueExample

           from manim import *
           from manim_extensions.algorithm.queue import Queue
           from manim_extensions.algorithm.node import Node

           class EnqueueExample(Scene):
               def construct(self):
                   q = Queue(capacity=4, init_data=[1, 2], total_width=8)
                   item = Node("3").next_to(q, RIGHT, buff=1.5)
                   self.add(q, item)
                   self.play(Queue.Enqueue(q, item))
                   self.wait(0.5)
        """

        def __init__(self, queue: "Queue", item: Node, **kwargs):
            """Initialize the Enqueue instance."""
            path = [
                item.get_center(),
                queue.get_right() + queue.item_width / 2 * RIGHT,
                (queue.data[-1].get_right() if queue.data else queue.get_left())
                + queue.item_width / 2 * RIGHT,
            ]
            polyline = VMobject()
            polyline.set_points_as_corners(path)
            super().__init__(
                *[
                    MoveAlongPath(item, path=polyline, rate_func=linear, run_time=2),
                ]
            )
            queue.add(item)
            queue.data.append(item)

    class Dequeue(Succession):
        """Animate the front item leaving the queue.

        The front node slides out from the left side while the remaining
        items shift one position to the left to fill the gap. When no
        target position is provided the item fades out after leaving the
        queue; otherwise it is moved to ``target_pos``.

        Parameters
        ----------
        queue : Queue
            The queue from which the front item will be removed.
        target_pos : Point3D, optional
            Destination point for the dequeued item. When omitted the
            item simply leaves the queue and fades out.

        Examples
        --------
        .. manim:: DequeueExample

           from manim import *
           from manim_extensions.algorithm.queue import Queue

           class DequeueExample(Scene):
               def construct(self):
                   q = Queue(capacity=4, init_data=[10, 20, 30], total_width=8)
                   self.add(q)
                   self.wait(0.5)
                   self.play(Queue.Dequeue(q))
                   self.wait(0.5)
        """

        def __init__(self, queue: "Queue", target_pos: Point3D = None, **kwargs):
            """Initialize the Dequeue instance."""
            if not queue.data:
                return
            item = queue.data[0]
            need_fadout = False
            if target_pos is None:
                target_pos = (
                    item.get_center()
                    + DOWN * queue.item_width
                    + LEFT * queue.item_width
                )
                need_fadout = True
            path = [queue.get_left() + queue.item_width / 2 * LEFT, target_pos]
            polyline = VMobject()
            polyline.set_points_as_corners(path)
            animations = [
                AnimationGroup(
                    *[item.animate.shift(LEFT * item.width) for item in queue.data]
                ),
                MoveAlongPath(item, path=polyline, rate_func=linear, run_time=2),
            ]
            if need_fadout:
                animations.append(FadeOut(item))
            super().__init__(*animations)
            queue.remove(item)
            queue.data.pop(0)