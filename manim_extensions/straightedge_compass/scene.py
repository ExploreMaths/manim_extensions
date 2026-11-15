# SPDX-FileCopyrightText: 2026 manim-straightedge-compass contributors
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""High-level scene base class that turns classical compass-and-straightedge
constructions into short, declarative animations."""

from __future__ import annotations

from manim import (
    Scene,
    Arc,
    Line,
    TAU,
    FadeIn,
    FadeOut,
    Write,
    UP,
    DOWN,
    LEFT,
    linear,
    Text,
)

from .geometry import as_point, distance
from .compass import Compass, CompassDrawArc
from .straightedge import Straightedge, PencilTip, RulerDraw
from .marks import MarkedPoint, POINT_COLOR

# Palette for construction traces vs. the final highlighted result
CONSTRUCTION_COLOR = "#5B8FF9"
CONSTRUCTION_GREEN = "#5AD19A"
RESULT_COLOR = "#F7D154"
RESULT_RED = "#FF8A80"

OFFSCREEN = DOWN * 6


class EuclidScene(Scene):
    """Scene with built-in compass and straightedge.

    Typical usage::

        class MyConstruction(EuclidScene):
            def construct(self):
                A, B = P(-2, 0), P(2, 0)
                self.mark_point(A, "A"); self.mark_point(B, "B")
                self.draw_circle(A, through=B)
                self.draw_circle(B, through=A)
                C = uppermost(circle_circle_intersection(A, d, B, d))
                self.mark_point(C, "C")
                self.draw_segment(A, B)
                self.draw_segment(A, C)
                self.draw_segment(B, C)
    """

    # tool motion timing
    tool_travel_time = 0.7
    default_arc_time = 2.4
    default_segment_time = 1.3

    def setup(self):
        super().setup()
        self.compass = Compass()
        self.ruler = Straightedge()
        self._compass_away = True
        self._ruler_away = True

    # ------------------------------------------------------------------ marks

    def intro(self, title: str, font_size: int = 30):
        """Write a Chinese/English title, then shrink it to the top-left
        corner so the construction has the whole stage."""
        text = Text(title, font_size=font_size, color="#D7DEE5")
        text.to_edge(UP, buff=0.3)
        self.play(Write(text), run_time=1.2)
        self.wait(0.3)
        self.play(
            text.animate.scale(0.62).to_corner(LEFT + UP, buff=0.25), run_time=0.6
        )
        return text

    def mark_point(
        self,
        point,
        label: str = None,
        direction=0.42 * UP,
        color=POINT_COLOR,
        radius: float = 0.06,
        font_size: int = 34,
        run_time: float = 0.35,
    ):
        """Drop a coloured marker (and optional label) on a point."""
        point = as_point(point)
        marked = MarkedPoint(point, label, direction, color, radius, font_size)
        self.play(FadeIn(marked.dot, scale=0.3), run_time=run_time)
        if marked.label_mob is not None:
            self.play(Write(marked.label_mob), run_time=0.35)
        return marked

    # ---------------------------------------------------------------- compass

    def _bring_compass(self, center, radius, start_angle):
        center = as_point(center)
        if self._compass_away:
            self.compass.pose(center + OFFSCREEN, radius, start_angle)
            self.add(self.compass)
            self.play(
                self.compass.animate.pose(center, radius, start_angle),
                run_time=self.tool_travel_time,
            )
            self._compass_away = False
        else:
            self.play(
                self.compass.animate.pose(center, radius, start_angle),
                run_time=self.tool_travel_time * 0.7,
            )

    def _retire_compass(self):
        c = self.compass.center
        self.play(
            self.compass.animate.pose(
                c + OFFSCREEN, self.compass.radius, self.compass.start_angle
            ),
            run_time=self.tool_travel_time * 0.8,
        )
        self.remove(self.compass)
        self._compass_away = True

    def draw_arc(
        self,
        center,
        radius: float,
        start_angle: float = 0.0,
        angle: float = TAU,
        color=CONSTRUCTION_COLOR,
        stroke_width: float = 2.0,
        run_time: float = None,
        keep_compass: bool = False,
    ):
        """Sweep an arc with the compass and leave it on the paper."""
        center = as_point(center)
        if run_time is None:
            run_time = self.default_arc_time * abs(angle) / TAU + 0.4
        self._bring_compass(center, radius, start_angle)
        arc = Arc(
            radius=radius,
            start_angle=start_angle,
            angle=1e-6,
            arc_center=center,
            stroke_color=color,
            stroke_width=stroke_width,
        )
        self.add(arc)
        self.play(
            CompassDrawArc(self.compass, arc, angle),
            run_time=run_time,
            rate_func=linear,
        )
        if not keep_compass:
            self._retire_compass()
        return arc

    def draw_circle(
        self,
        center,
        through=None,
        radius: float = None,
        color=CONSTRUCTION_COLOR,
        stroke_width: float = 2.0,
        run_time: float = None,
        start_angle: float = 0.0,
    ):
        """Draw a full circle, either with explicit radius or radius equal to
        the distance ``center -> through`` (compass picks up that length)."""
        if radius is None:
            if through is None:
                raise ValueError("provide either radius= or through=")
            radius = distance(center, through)
        return self.draw_arc(
            center,
            radius,
            start_angle=start_angle,
            angle=TAU,
            color=color,
            stroke_width=stroke_width,
            run_time=run_time,
        )

    # ------------------------------------------------------------ straightedge

    def _bring_ruler(self, p1, p2):
        p1, p2 = as_point(p1), as_point(p2)
        if self._ruler_away:
            self.ruler.pose(p1 + OFFSCREEN, p2 + OFFSCREEN)
            self.add(self.ruler)
            self.play(self.ruler.animate.pose(p1, p2), run_time=self.tool_travel_time)
            self._ruler_away = False
        else:
            self.play(
                self.ruler.animate.pose(p1, p2), run_time=self.tool_travel_time * 0.7
            )

    def _retire_ruler(self):
        p1, p2 = self._ruler_endpoints
        self.play(
            self.ruler.animate.pose(p1 + OFFSCREEN, p2 + OFFSCREEN),
            run_time=self.tool_travel_time * 0.8,
        )
        self.remove(self.ruler)
        self._ruler_away = True

    def retire_ruler(self):
        """Send the ruler offstage after a run of keep_ruler segments."""
        self._retire_ruler()

    def draw_segment(
        self,
        p1,
        p2,
        color=RESULT_COLOR,
        stroke_width: float = 4,
        run_time: float = None,
        keep_ruler: bool = False,
        tip_fade: float = 0.25,
    ):
        """Lay the ruler along p1p2 and draw the segment with a pencil.

        Pass ``keep_ruler=True`` for consecutive segments: the ruler stays on
        stage and merely re-aligns, which reads as drawing a polygon side by
        side; call :meth:`~manim_extensions.straightedge_compass.scene.EuclidScene.retire_ruler` after the last one.
        """
        p1, p2 = as_point(p1), as_point(p2)
        self._ruler_endpoints = (p1, p2)
        if run_time is None:
            run_time = self.default_segment_time
        self._bring_ruler(p1, p2)
        line = Line(p1, p1, color=color, stroke_width=stroke_width, z_index=8)
        tip = PencilTip(p1)
        self.add(line, tip)
        self.play(
            RulerDraw(line, tip, p1, p2),
            run_time=run_time,
            rate_func=linear,
        )
        self.play(FadeOut(tip, scale=0.4), run_time=tip_fade)
        if not keep_ruler:
            self._retire_ruler()
        return line

    # --------------------------------------------------------------- utilities

    def flash_points(self, *points, color=RESULT_COLOR):
        """Briefly emphasise already-computed points."""
        dots = [MarkedPoint(as_point(q), color=color, radius=0.08).dot for q in points]
        for d in dots:
            self.add(d)
        self.play(*[FadeOut(d, scale=2.2) for d in dots], run_time=0.7)
