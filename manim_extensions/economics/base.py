# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Base classes for economic diagrams.

This module provides the base classes for economic diagram visualizations.

"""

from manim import *
import numpy as np


def find_intersection(func_a, func_b, x_range):
    """Find the x where func_a(x) == func_b(x) by sampling."""
    xs = np.linspace(x_range[0] + 0.01, x_range[1] - 0.01, 1000)
    diffs = np.array([func_a(x) - func_b(x) for x in xs])
    sign_changes = np.where(np.diff(np.sign(diffs)))[0]
    if len(sign_changes) == 0:
        return None
    idx = sign_changes[0]
    # linear interpolation between the two bracketing samples
    x0, x1 = xs[idx], xs[idx + 1]
    d0, d1 = diffs[idx], diffs[idx + 1]
    x_cross = x0 - d0 * (x1 - x0) / (d1 - d0)
    return x_cross


class EconDiagram(VGroup):
    """Base class for economics diagrams built on manim Axes.

    Parameters
    ----------
    x_label
        Label for the x-axis (default ``"X"``).
    y_label
        Label for the y-axis (default ``"Y"``).
    x_range
        Range of the x-axis as ``[min, max, step]`` (default ``[0, 10, 1]``).
    y_range
        Range of the y-axis as ``[min, max, step]`` (default ``[0, 10, 1]``).
    x_length
        Length of the x-axis in scene units (default 6).
    y_length
        Length of the y-axis in scene units (default 4).
    **kwargs
        Additional keyword arguments passed to ``VGroup``.
    """

    def __init__(self, x_label="X", y_label="Y",
                 x_range=None, y_range=None,
                 x_length=6, y_length=4, **kwargs):
        super().__init__(**kwargs)

        x_range = x_range or [0, 10, 1]
        y_range = y_range or [0, 10, 1]

        self.axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=x_length,
            y_length=y_length,
            axis_config={"include_numbers": False},
        )

        self.axis_labels = VGroup(
            Text(x_label, font_size=24).next_to(self.axes.x_axis, RIGHT),
            Text(y_label, font_size=24).next_to(self.axes.y_axis, UP),
        )

        self.curves = {}
        self._curve_funcs = {}
        self._curve_x_ranges = {}
        self._curve_labels = {}
        self._eq_group = VGroup()
        self._eq_curve_names = None
        self._eq_label_x = ""
        self._eq_label_y = ""
        self._eq_numbered = False
        self._eq_count = 0

        self.add(self.axes, self.axis_labels)

    def add_curve(self, name, func, x_range, color, label_text=None):
        """Plot a curve on the axes and store it by name."""
        curve = self.axes.plot(func, x_range=x_range, color=color)
        self.curves[name] = curve
        self._curve_funcs[name] = func
        self._curve_x_ranges[name] = x_range
        self.add(curve)

        if label_text:
            label = Text(label_text, font_size=20, color=color)
            label.next_to(curve.get_end(), RIGHT, buff=0.15)
            self._curve_labels[name] = label
            self.add(label)

        return curve

    def add_vertical_line(self, name, x, color, label_text=None):
        """Add a vertical line at a given x position."""
        y_min = self.axes.y_range[0]
        y_max = self.axes.y_range[1]
        start = self.axes.c2p(x, y_min)
        end = self.axes.c2p(x, y_max)
        line = Line(start, end, color=color)
        self.curves[name] = line
        self.add(line)

        if label_text:
            label = Text(label_text, font_size=20, color=color)
            label.next_to(line, UP, buff=0.15)
            self._curve_labels[name] = label
            self.add(label)

        return line

    _SUBSCRIPTS = "₁₂₃₄₅₆₇₈₉"

    def _sub(self, n):
        """Return a unicode subscript for n (1-indexed)."""
        if 1 <= n <= 9:
            return self._SUBSCRIPTS[n - 1]
        return str(n)

    def _build_eq_parts(self, curve_a, curve_b, label_x="", label_y="",
                        subscript=None):
        """Build equilibrium geometry and labels separately.

        Returns (geometry_group, labels_group) or (None, None).
        geometry_group contains the dot and dashed lines.
        labels_group contains the axis text labels.
        """
        func_a = self._curve_funcs[curve_a]
        func_b = self._curve_funcs[curve_b]
        x_range = self.axes.x_range

        x_eq = find_intersection(func_a, func_b, x_range)
        if x_eq is None:
            return None, None

        y_eq = func_a(x_eq)
        point = self.axes.c2p(x_eq, y_eq)

        dot = Dot(point, color=YELLOW, radius=0.06)
        h_line = DashedLine(
            self.axes.c2p(0, y_eq), point, color=WHITE, dash_length=0.08
        )
        v_line = DashedLine(
            self.axes.c2p(x_eq, 0), point, color=WHITE, dash_length=0.08
        )
        geom = VGroup(dot, h_line, v_line)

        suffix = self._sub(subscript) if subscript else ""
        labels = VGroup()
        if label_x:
            lx = Text(label_x + suffix, font_size=18).next_to(
                self.axes.c2p(x_eq, 0), DOWN, buff=0.15
            )
            labels.add(lx)
        if label_y:
            ly = Text(label_y + suffix, font_size=18).next_to(
                self.axes.c2p(0, y_eq), LEFT, buff=0.15
            )
            labels.add(ly)

        return geom, labels

    def _build_eq_group(self, curve_a, curve_b, label_x="", label_y="",
                        subscript=None):
        """Build a combined equilibrium VGroup (geometry + labels)."""
        geom, labels = self._build_eq_parts(curve_a, curve_b, label_x,
                                            label_y, subscript)
        if geom is None:
            return None
        return VGroup(geom, labels)

    def mark_equilibrium(self, curve_a, curve_b, label_x="", label_y="",
                         numbered=False):
        """Mark the intersection of two curves with a dot and dashed lines.

        Parameters:
            numbered: If True, labels use subscripts (P₁/Y₁) that
                increment on each shift, and old markers stay visible.
        """
        self._eq_curve_names = (curve_a, curve_b)
        self._eq_label_x = label_x
        self._eq_label_y = label_y
        self._eq_numbered = numbered
        self._eq_count = 1 if numbered else 0

        sub = 1 if numbered else None
        eq_group = self._build_eq_group(curve_a, curve_b, label_x, label_y,
                                        subscript=sub)
        if eq_group is None:
            return None

        self._eq_group = eq_group
        self.add(eq_group)
        return eq_group

    def _get_eq_coords(self):
        """Return (x, y) of the current equilibrium, or None."""
        if not self._eq_curve_names:
            return None
        a, b = self._eq_curve_names
        func_a = self._curve_funcs[a]
        func_b = self._curve_funcs[b]
        x_eq = find_intersection(func_a, func_b, self.axes.x_range)
        if x_eq is None:
            return None
        return x_eq, func_a(x_eq)

    @staticmethod
    def _make_single_arrow(start, end, color, tip_size=0.08):
        """Create a line with a small triangle at the end only."""
        direction = end - start
        norm = np.linalg.norm(direction)
        if norm < 1e-6:
            return VGroup()
        unit = direction / norm
        perp = np.array([-unit[1], unit[0], 0])

        shaft = Line(start, end - unit * tip_size, color=color, stroke_width=3)
        tip = Polygon(
            end,
            end - unit * tip_size * 2 + perp * tip_size,
            end - unit * tip_size * 2 - perp * tip_size,
            color=color,
            fill_color=color,
            fill_opacity=1,
            stroke_width=0,
        )
        return VGroup(shaft, tip)

    def _build_axis_arrows(self, old_xy, new_xy, arrow_color=WHITE):
        """Build arrows near the axes between old and new equilibrium values.

        Returns a VGroup with up to two arrows (x-axis and y-axis).
        """
        old_x, old_y = old_xy
        new_x, new_y = new_xy
        group = VGroup()

        if abs(new_x - old_x) > 0.05:
            x_offset = DOWN * 0.5
            start = self.axes.c2p(old_x, 0) + x_offset
            end = self.axes.c2p(new_x, 0) + x_offset
            group.add(self._make_single_arrow(start, end, arrow_color))

        if abs(new_y - old_y) > 0.05:
            y_offset = LEFT * 0.5
            start = self.axes.c2p(0, old_y) + y_offset
            end = self.axes.c2p(0, new_y) + y_offset
            group.add(self._make_single_arrow(start, end, arrow_color))

        return group

    def get_shift_animation(self, curve_name, new_func, new_x_range=None,
                            run_time=1, show_arrows=False, arrow_color=WHITE):
        """Return a Transform animation that shifts a curve to a new function.

        Parameters:
            show_arrows: If True, draw arrows on the axes showing
                the direction of equilibrium change.
            arrow_color: Color for the axis arrows (default WHITE).
        """
        old_eq = self._get_eq_coords() if show_arrows else None

        old_curve = self.curves[curve_name]
        x_range = new_x_range or self._curve_x_ranges[curve_name]
        new_curve = self.axes.plot(
            new_func, x_range=x_range, color=old_curve.get_color()
        )

        self._curve_funcs[curve_name] = new_func
        self.curves[curve_name] = new_curve

        anims = [ReplacementTransform(old_curve, new_curve, run_time=run_time)]

        if curve_name in self._curve_labels:
            old_label = self._curve_labels[curve_name]
            new_label = old_label.copy().next_to(new_curve.get_end(), RIGHT, buff=0.15)
            anims.append(ReplacementTransform(old_label, new_label, run_time=run_time))

        if self._eq_curve_names and curve_name in self._eq_curve_names:
            if self._eq_numbered:
                self._eq_count += 1
                new_geom, new_labels = self._build_eq_parts(
                    *self._eq_curve_names, self._eq_label_x, self._eq_label_y,
                    subscript=self._eq_count,
                )
                if new_geom is not None:
                    old_group = self._eq_group
                    old_geom = old_group[0]
                    new_eq_group = VGroup(new_geom, new_labels)
                    self._eq_group = new_eq_group
                    anims.append(ReplacementTransform(
                        old_geom, new_geom, run_time=run_time
                    ))
                    anims.append(FadeIn(new_labels, run_time=run_time))
            else:
                new_eq_group = self._build_eq_group(
                    *self._eq_curve_names, self._eq_label_x, self._eq_label_y
                )
                if new_eq_group is not None:
                    old_eq_group = self._eq_group
                    self._eq_group = new_eq_group
                    anims.append(ReplacementTransform(
                        old_eq_group, new_eq_group, run_time=run_time
                    ))

        if show_arrows and old_eq is not None:
            new_eq = self._get_eq_coords()
            if new_eq is not None:
                arrows = self._build_axis_arrows(old_eq, new_eq, arrow_color)
                if len(arrows) > 0:
                    self._axis_arrows = arrows
                    anims.append(FadeIn(arrows, run_time=run_time))

        return AnimationGroup(*anims)

    def clear_arrows(self):
        """Return a FadeOut animation for any existing axis arrows.

        Returns ``None`` if there are no arrows to clear.
        """
        if hasattr(self, '_axis_arrows') and self._axis_arrows is not None:
            old = self._axis_arrows
            self._axis_arrows = None
            return FadeOut(old, run_time=0.3)
        return None