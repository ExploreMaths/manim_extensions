# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
"""Pin joint constraint for Pymunk.

This module provides the VPinJoint class for creating pin joint constraints in physics simulations.

"""

from __future__ import annotations

from manim import Dot, Line, Mobject, ORIGIN, RED, YELLOW, np
from typing import Optional, TYPE_CHECKING
from . import VConstraint

from ...utils.deps import require

if TYPE_CHECKING:
    from pymunk import Space
    from pymunk.constraints import PinJoint


class VPinJoint(VConstraint):
    """A pin joint keeps a fixed distance between two anchor points on two rigid bodies.
    It acts like a solid, weightless rod connecting two points, allowing them
    to rotate freely around the anchors while maintaining the specified `distance`.

    Parameters
    ----------
    a_mob
        The first Mobject to be connected.
    b_mob
        The second Mobject to be connected.
    anchor_a_local
        The local anchor point on `a_mob` where the pin is attached,
        relative to the Mobject's center.
    anchor_b_local
        The local anchor point on `b_mob` where the pin is attached,
        relative to the Mobject's center.
    distance
        The fixed distance to maintain between the two anchors. If `None`,
        it is automatically calculated as the initial distance between anchors.
    anchor_a_appearance
        The Mobject used to visually represent the anchor point on `a_mob`
        (e.g., a red `Dot`).
    anchor_b_appearance
        The Mobject used to visually represent the anchor point on `b_mob`
        (e.g., a red `Dot`).
    connect_line_class
        The class used to draw the connecting rod (e.g., `Line`).
        Defaults to `None` for no visible connection.
    connect_line_config
        A dictionary defining the visual style of the connecting line,
        such as `color` and `stroke_width`.
    **kwargs
        Forwarded to the parent :class:`~manim_extensions.pymunk.constraints.constraint.VConstraint`.

    Examples
    --------
    .. manim:: VPinJointExample

        from manim import *
        from manim_extensions.pymunk import *

        class VPinJointExample(SpaceScene):
            def construct(self):
                # a pin joint acts like a rigid rod between two anchors
                static_dot = Dot(ORIGIN)
                square = Square().move_to(static_dot)
                square2 = Square().move_to(static_dot.get_center() + UP * 2).scale(0.5)

                constraints = [
                    VPinJoint(static_dot, square),
                    VPinJoint(
                        square,
                        square2,
                        anchor_a_local=square.get_corner(UR) - square.get_center(),
                        distance=2,
                        connect_line_class=Line,
                    ),
                ]

                self.play(FadeIn(static_dot), FadeIn(square), FadeIn(square2))
                self.add_static_body(static_dot)
                self.add_dynamic_body(square, square2, angular_velocity=PI * 2)
                self.add_shapes_filter(static_dot, square, square2, group=2)
                self.add_constraints(*constraints)
                self.wait(3)

    """

    def __init__(
        self,
        a_mob: Mobject,
        b_mob: Mobject,
        anchor_a_local: list[float, float, float] = ORIGIN,
        anchor_b_local: list[float, float, float] = ORIGIN,
        distance: Optional[float] = None,
        anchor_a_appearance: Mobject = Dot(color=RED),
        anchor_b_appearance: Mobject = Dot(color=RED),
        connect_line_class: Optional[Line] = None,
        connect_line_config: dict = {
            "color": YELLOW,
            "stroke_width": 2,
        },
        **kwargs,
    ):
        """Initialize a pin joint constraint with two bodies, local anchor
        points, optional fixed distance, and visual anchor/line indicators.
        """

        super().__init__(a_mob=a_mob, b_mob=b_mob, **kwargs)

        self.anchor_a_local = anchor_a_local
        self.anchor_b_local = anchor_b_local

        self.anchor_a_appearance = anchor_a_appearance
        self.anchor_b_appearance = anchor_b_appearance

        self.connect_line_class = connect_line_class
        self.connect_line_config = connect_line_config
        self.connect_line = None

        self.constraint: Optional[PinJoint] = None
        self.init_distance = distance
        self.__check_data()

    def __check_data(self):
        """Verify the validity of constraint parameters."""
        if self.a_mob is None or self.b_mob is None:
            raise ValueError(
                "Constraints cannot be created without both a_mob and b_mob."
            )

        dist = np.linalg.norm(self.a_mob.get_center() - self.b_mob.get_center())

        if dist < 0.000001:
            if self.connect_line_class is not None:
                raise ValueError(
                    f"Points {self.a_mob} and {self.b_mob} are at the same location ({dist:.8f}). "
                    "Connecting them with a line makes no sense."
                )

    def install(self, space: Space):
        """Create the Pymunk PinJoint constraint, initialize visual anchor
        markers and connecting line, add the constraint to the space, and
        register the per-frame updater.

        Parameters
        ----------
        space : Space
            The Pymunk space to add the constraint to.
        """

        PinJoint = require("physics", "pymunk").constraints.PinJoint

        a_body, b_body = self._get_bodies(
            "VPinJoint 连接的物体必须先执行 add_dynamic_body"
        )

        # 1. 创建约束
        self.constraint = PinJoint(
            a_body,
            b_body,
            tuple(self.anchor_a_local[:2]),
            tuple(self.anchor_b_local[:2]),
        )

        if self.init_distance is not None:
            self.constraint.distance = self.init_distance

        pos_a = a_body.local_to_world(tuple(self.anchor_a_local[:2]))
        pos_b = b_body.local_to_world(tuple(self.anchor_b_local[:2]))
        p1 = [pos_a.x, pos_a.y, 0]
        p2 = [pos_b.x, pos_b.y, 0]

        if self.connect_line_class:
            self.connect_line = self.connect_line_class(
                p1, p2, **self.connect_line_config
            )
            self.add(self.connect_line)

        self.anchor_a_appearance.move_to(p1)
        self.anchor_b_appearance.move_to(p2)

        self.add(self.anchor_a_appearance, self.anchor_b_appearance)

        self._finalize_install(space)

    def mob_updater(self, mob: Mobject, dt: float):
        """Visual control updater.

        Parameters
        ----------
        mob : Mobject
            The constraint mobject being updated.
        dt : float
            Time step since the last frame, in seconds.
        """
        if not self.constraint:
            return
        a_body = self.constraint.a
        b_body = self.constraint.b
        wa = a_body.local_to_world(self.constraint.anchor_a)
        wb = b_body.local_to_world(self.constraint.anchor_b)

        p1 = [wa.x, wa.y, 0]
        p2 = [wb.x, wb.y, 0]

        self.anchor_a_appearance.move_to(p1)
        self.anchor_b_appearance.move_to(p2)

        if isinstance(self.connect_line, Line):
            self.connect_line.put_start_and_end_on(p1, p2)