# SPDX-FileCopyrightText: 2026 manim-straightedge-compass contributors
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""The straightedge: an unmarked-in-principle ruler body (drawn with
decorative tick marks only for visual flavour) along whose edge a pencil
slides to draw a straight segment."""

from __future__ import annotations
from typing import Any

from manim import (
    VGroup,
    Line,
    Rectangle,
    Dot,
    Polygon,
    Animation,
    ORIGIN,
    LEFT,
    RIGHT,
)

from .geometry import as_point, P, angle_of

BODY_COLOR = "#3E5360"
BODY_FILL = "#46606E"
EDGE_COLOR = "#D7DEE5"
TICK_COLOR = "#C7D0D8"
PENCIL_COLOR = "#FFD54F"
PENCIL_LEAD = "#2B2F36"

RULER_LENGTH = 6.5
RULER_WIDTH = 0.62


class Straightedge(VGroup):
    """A long ruler whose lower edge (local ``y = 0``) is the working edge.

    Use :meth:`~manim_extensions.straightedge_compass.straightedge.Straightedge.pose` to align the edge with two points, then play
    :class:`~manim_extensions.straightedge_compass.straightedge.RulerDraw` to run a pencil along it.

    Parameters
    ----------
    ruler_length
        Length of the ruler.
    ruler_width
        Width of the ruler body.
    **kwargs
        Keyword arguments forwarded to the vector group.

    Examples
    --------
    .. manim:: StraightedgeScene
       :save_last_frame:

       from manim import Scene
       from manim_extensions.straightedge_compass import Straightedge

       class StraightedgeScene(Scene):
           def construct(self):
               ruler = Straightedge()
               ruler.pose([-2, 0, 0], [2, 0, 0])
               ruler.scale(1.4)
               self.add(ruler)
    """

    def __init__(
        self,
        ruler_length: float = RULER_LENGTH,
        ruler_width: float = RULER_WIDTH,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        # names deliberately avoid Mobject.width / .length properties
        self.ruler_length = float(ruler_length)
        self.ruler_width = float(ruler_width)
        self.become(self._canonical())

    def _canonical(self) -> VGroup:
        """Build the ruler in its home pose.

        Returns
        -------
        A group with the body, tick marks, and working edge aligned
        horizontally through the origin.
        """
        body = Rectangle(
            width=self.ruler_length,
            height=self.ruler_width,
            fill_color=BODY_FILL,
            fill_opacity=0.55,
            stroke_color=BODY_COLOR,
            stroke_width=2,
        ).move_to(P(0, self.ruler_width / 2))
        edge = Line(
            self.ruler_length / 2 * LEFT,
            self.ruler_length / 2 * RIGHT,
            color=EDGE_COLOR,
            stroke_width=3,
            z_index=12,
        )
        ticks = VGroup()
        step = 0.25
        x = -self.ruler_length / 2 + 0.2
        while x <= self.ruler_length / 2 - 0.2:
            k = round((x + self.ruler_length / 2) / step)
            if k % 4 == 0:
                tlen, w = 0.22, 1.6
            elif k % 2 == 0:
                tlen, w = 0.15, 1.3
            else:
                tlen, w = 0.09, 1.0
            ticks.add(
                Line(
                    P(x, 0.02),
                    P(x, 0.02 + tlen),
                    color=TICK_COLOR,
                    stroke_width=w,
                )
            )
            x += step
        return VGroup(body, ticks, edge)

    def pose(self, p1: Any, p2: Any) -> Any:
        """Align the working edge with the line through two points.

        Parameters
        ----------
        p1
            First point on the line.
        p2
            Second point on the line.

        Returns
        -------
        This ruler, allowing the call to be chained or animated.
        """
        p1, p2 = as_point(p1), as_point(p2)
        mid = (p1 + p2) / 2.0
        theta = angle_of(p1, p2)
        canonical = self._canonical()
        canonical.rotate(theta, about_point=ORIGIN)
        canonical.shift(mid)
        self.become(canonical)
        return self


class PencilTip(VGroup):
    """A small pencil that rides along the ruler edge while drawing.

    Parameters
    ----------
    point
        Initial position of the pencil tip.
    **kwargs
        Keyword arguments forwarded to the vector group.

    Examples
    --------
    .. manim:: PencilTipScene
       :save_last_frame:

       from manim import Scene
       from manim_extensions.straightedge_compass import PencilTip

       class PencilTipScene(Scene):
           def construct(self):
               tip = PencilTip([0, 0, 0])
               tip.scale(16.0)
               self.add(tip)
    """

    def __init__(self, point: Any = ORIGIN, **kwargs) -> None:
        super().__init__(**kwargs)
        lead = Dot(ORIGIN, radius=0.05, color=PENCIL_LEAD, z_index=20)
        body = Polygon(
            P(0, 0),
            P(0.16, 0.30),
            P(-0.16, 0.30),
            fill_color=PENCIL_COLOR,
            fill_opacity=1,
            stroke_color=PENCIL_LEAD,
            stroke_width=1,
            z_index=19,
        )
        self.add(body, lead)
        self.move_to(as_point(point))


class RulerDraw(Animation):
    """Slide a :class:`~manim_extensions.straightedge_compass.straightedge.PencilTip` from ``p1`` to ``p2`` while the target
    :class:`~manim.mobject.geometry.line.Line` grows underneath it.

    Parameters
    ----------
    line
        Line that grows during the animation.
    tip
        The pencil that slides along the line.
    p1
        Start point of the line.
    p2
        End point of the line.
    run_time
        Duration of the animation.
    **kwargs
        Keyword arguments forwarded to the animation.
    """

    def __init__(
        self,
        line: Line,
        tip: PencilTip,
        p1: Any,
        p2: Any,
        run_time: float = 1.4,
        **kwargs,
    ) -> None:
        self.line = line
        self.tip = tip
        self.p1 = as_point(p1)
        self.p2 = as_point(p2)
        super().__init__(VGroup(line, tip), run_time=run_time, **kwargs)
        self.line.set_points_as_corners([self.p1, self.p1])
        self.tip.move_to(self.p1)

    def interpolate_mobject(self, alpha: float) -> Any:
        """Slide the pencil and grow the line.

        Parameters
        ----------
        alpha
            Animation progress between zero and one.

        Returns
        -------
        ``None``; the line and pencil are updated in place.
        """
        pos = self.p1 + alpha * (self.p2 - self.p1)
        self.line.set_points_as_corners([self.p1, pos])
        self.tip.move_to(pos)
