# SPDX-FileCopyrightText: 2026 manim-straightedge-compass contributors
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""The compass: a V-shaped drafting tool that pivots around its needle
tip while the pencil leg sweeps out an arc."""

from __future__ import annotations
from typing import Any

import numpy as np
from manim import (
    VGroup,
    Line,
    Dot,
    Polygon,
    Arc,
    Animation,
    RIGHT,
    ORIGIN,
)

from .geometry import as_point, P, unit

# Default palette
LEG_COLOR = "#B7BCC4"  # brushed metal legs
HINGE_COLOR = "#6B727B"
NEEDLE_COLOR = "#E5484D"  # red needle point
PENCIL_COLOR = "#FFD54F"  # yellow pencil
PENCIL_LEAD = "#2B2F36"

LEG_LENGTH = 2.1  # length of each compass leg (scene units)
HANDLE_LENGTH = 0.34


class Compass(VGroup):
    """A top-down stylised compass.

    The needle tip sits at the centre of the circle; the pencil tip is one
    radius away.  Call :meth:`~manim_extensions.straightedge_compass.compass.Compass.pose` (also usable with ``.animate``) to place
    the tool, then play a :class:`~manim_extensions.straightedge_compass.compass.CompassDrawArc` animation to draw.

    Parameters
    ----------
    radius
        Opening of the compass.
    start_angle
        Orientation of the pencil leg.
    center
        Needle position.
    leg_width
        Stroke width of the compass legs.
    **kwargs
        Keyword arguments forwarded to the vector group.

    Examples
    --------
    .. manim:: CompassScene
       :save_last_frame:

       from manim import Scene
       from manim_extensions.straightedge_compass import Compass

       class CompassScene(Scene):
           def construct(self):
               compass = Compass(radius=1.5, center=[0, 0, 0])
               self.add(compass)
    """

    def __init__(
        self,
        radius: float = 1.5,
        start_angle: float = 0.0,
        center: Any = ORIGIN,
        leg_width: float = 7.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = float(radius)
        self.start_angle = float(start_angle)
        self.center = as_point(center)
        self.leg_width = leg_width

        self.needle_leg = Line(
            ORIGIN, RIGHT, stroke_width=leg_width, color=LEG_COLOR, z_index=10
        )
        self.pencil_leg = Line(
            ORIGIN, RIGHT, stroke_width=leg_width, color=LEG_COLOR, z_index=10
        )
        self.handle = Line(
            ORIGIN, RIGHT, stroke_width=leg_width + 3, color=HINGE_COLOR, z_index=11
        )
        self.hinge = Dot(ORIGIN, radius=0.10, color=HINGE_COLOR, z_index=12)
        self.needle_tip = Dot(ORIGIN, radius=0.055, color=NEEDLE_COLOR, z_index=13)
        self.pencil_lead = Dot(ORIGIN, radius=0.045, color=PENCIL_LEAD, z_index=13)
        # little yellow pencil body at the end of the pencil leg
        self.pencil_body = Polygon(
            ORIGIN,
            RIGHT,
            RIGHT,
            fill_color=PENCIL_COLOR,
            fill_opacity=1,
            stroke_width=1,
            stroke_color=PENCIL_LEAD,
            z_index=12,
        )
        self.add(
            self.needle_leg,
            self.pencil_leg,
            self.handle,
            self.hinge,
            self.needle_tip,
            self.pencil_body,
            self.pencil_lead,
        )
        self.pose(self.center, self.radius, self.start_angle)

    # -- geometry ------------------------------------------------------------

    def _layout(self, center: Any, radius: Any, theta: Any) -> Any:
        """Compute the compass joint and tip positions.

        Parameters
        ----------
        center
            Needle position.
        radius
            The compass opening.
        theta
            Orientation of the pencil leg.

        Returns
        -------
        The needle, pencil tip, hinge, handle end, and two pencil-body
        corners.
        """
        r = float(np.clip(radius, 0.05, 2 * LEG_LENGTH - 0.05))
        h = np.sqrt(max(LEG_LENGTH**2 - (r / 2.0) ** 2, 1e-6))
        n = as_point(center)
        needle = P(0, 0)
        pencil = P(r, 0)
        hinge = P(r / 2.0, h)

        def tr(q: Any) -> Any:
            """tr."""
            c, s = np.cos(theta), np.sin(theta)
            rot = P(c * q[0] - s * q[1], s * q[0] + c * q[1])
            return n + rot

        n_t, p_t, h_t = tr(needle), tr(pencil), tr(hinge)
        # handle points away from the needle, continuing past the hinge
        h_dir = unit(h_t - n_t)
        handle_end = h_t + HANDLE_LENGTH * h_dir
        # pencil body: small triangle hugging the pencil tip, pointing to lead
        leg_dir = unit(h_t - p_t)
        perp = P(-leg_dir[1], leg_dir[0])
        b1 = p_t + 0.30 * leg_dir + 0.075 * perp
        b2 = p_t + 0.30 * leg_dir - 0.075 * perp
        return n_t, p_t, h_t, handle_end, b1, b2

    def pose(self, center: Any, radius: float = None, start_angle: float = 0.0) -> Any:
        """Place the compass at a centre, opening, and orientation.

        Parameters
        ----------
        center
            Needle position.
        radius
            The compass opening; the current radius is kept when omitted.
        start_angle
            Orientation of the pencil leg.

        Returns
        -------
        This compass, allowing the call to be chained or animated.
        """
        if radius is not None:
            self.radius = float(radius)
        self.center = as_point(center)
        self.start_angle = float(start_angle)

        n_t, p_t, h_t, handle_end, b1, b2 = self._layout(
            self.center, self.radius, self.start_angle
        )
        self.needle_leg.put_start_and_end_on(n_t, h_t)
        self.pencil_leg.put_start_and_end_on(p_t, h_t)
        self.handle.put_start_and_end_on(h_t, handle_end)
        self.hinge.move_to(h_t)
        self.needle_tip.move_to(n_t)
        self.pencil_lead.move_to(p_t)
        self.pencil_body.set_points_as_corners([p_t, b1, b2])
        return self

    def pencil_point(self, theta: float = None) -> Any:
        """Return the world position of the pencil tip.

        Parameters
        ----------
        theta
            Sweep angle; the current start angle is used when omitted.

        Returns
        -------
        The pencil tip coordinates.
        """
        if theta is None:
            theta = self.start_angle
        return self.center + self.radius * P(np.cos(theta), np.sin(theta))

    # -- animation helpers ---------------------------------------------------

    def rotated_copy(self, theta: float) -> Compass:
        """Return a copy rotated to an absolute pencil angle.

        Parameters
        ----------
        theta
            Absolute orientation of the pencil leg.

        Returns
        -------
        The rotated compass copy.
        """
        return self.copy().pose(self.center, self.radius, theta)


class CompassDrawArc(Animation):
    """Sweep the compass pencil leg around the needle while an :class:`~manim.mobject.geometry.arc.Arc` grows
    on the paper.  The finished arc is part of the animation's mobject group,
    so it stays on screen afterwards.

    Parameters
    ----------
    compass
        The compass whose pencil sweeps the arc.
    arc
        Arc that grows under the pencil.
    sweep
        Sweep angle in radians.
    run_time
        Duration of the animation.
    **kwargs
        Keyword arguments forwarded to the animation.
    """

    def __init__(
        self, compass: Compass, arc: Arc, sweep: float, run_time: float = 2.2, **kwargs
    ) -> None:
        self.compass = compass
        self.arc = arc
        self.sweep = float(sweep)
        self.start = float(arc.start_angle)
        self.radius = float(arc.radius)
        # NB: use the stored arc_center attribute; Arc.get_arc_center()
        # reconstructs the centre from tangents and is numerically unstable
        # for the near-degenerate seed arc.
        self.center = as_point(arc.arc_center)
        group = VGroup(compass, arc)
        super().__init__(group, run_time=run_time, **kwargs)

    def interpolate_mobject(self, alpha: float) -> Any:
        """Advance the compass sweep and grow the arc.

        Parameters
        ----------
        alpha
            Animation progress between zero and one.

        Returns
        -------
        ``None``; the compass and arc are updated in place.
        """
        theta = self.start + alpha * self.sweep
        # rotate the whole rigid compass about the needle tip
        self.compass.pose(self.center, self.radius, theta)
        # grow the arc underneath the pencil
        swept = max(alpha * self.sweep, 1e-6)
        partial = Arc(
            radius=self.radius,
            start_angle=self.start,
            angle=swept,
            arc_center=self.center,
        )
        partial.match_style(self.arc)
        self.arc.set_points(partial.points)
