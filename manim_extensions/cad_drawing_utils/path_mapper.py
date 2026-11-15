# SPDX-FileCopyrightText: 2020 GarryBGoode
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""path_mapper module."""

from __future__ import annotations
from typing import Any
import numpy as np
from manim import (
    Circle,
    PI,
    VDict,
    VGroup,
    VMobject,
    angle_of_vector,
    bezier,
    normalize,
    rotate_vector,
)


class PathMapper(VMobject):
    """Map arc length and proportion along an arbitrary path.

    Parameters
    ----------
    path_source
        Path whose length and point positions are queried.
    num_of_path_points
        Number of samples used to build the length table.
    **kwargs
        Keyword arguments forwarded to the vector mobject.

    Examples
    --------
    .. manim:: PathMapperScene
       :save_last_frame:

        from manim import Scene, Circle
        from manim_extensions.cad_drawing_utils.path_mapper import PathMapper

        class PathMapperScene(Scene):
            def construct(self):
                path = Circle(radius=2)
                mapper = PathMapper(path)
                dot = Dot(mapper.point_from_proportion(0.25))
                self.add(path, dot)
    """

    def __init__(
        self, path_source: VMobject, num_of_path_points: Any = 100, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.num_of_path_points = num_of_path_points
        self.path = path_source
        self.generate_length_map()

    def generate_length_map(self) -> Any:
        """Rebuild the cumulative length table for the path.

        Returns
        -------
        ``None``; the length and alpha tables are stored on the instance.
        """
        norms = np.array(0)
        for k in range(self.path.get_num_curves()):
            norms = np.append(
                norms, self.path.get_nth_curve_length_pieces(k, sample_points=11)
            )
        # add up length-pieces in array form
        self.pathdata_lengths = np.cumsum(norms)
        self.pathdata_alpha = np.linspace(0, 1, self.pathdata_lengths.size)

    def cubic_to_quads(self, cubic_points: Any) -> Any:
        """Approximate one cubic Bezier segment with two quadratic ones.

        Parameters
        ----------
        cubic_points
            Four control points of the cubic segment.

        Returns
        -------
        Six control points forming two consecutive quadratic segments.
        """
        # based on https://ttnghia.github.io/pdf/QuadraticApproximation.pdf
        q_points = np.empty((0, 3))
        gamma = 0.5
        q1 = cubic_points[0, :] + 3 / 2 * gamma * (
            cubic_points[1, :] - cubic_points[0, :]
        )
        q3 = cubic_points[3, :] + 3 / 2 * (1 - gamma) * (
            cubic_points[2, :] - cubic_points[3, :]
        )
        q2 = (1 - gamma) * q1 + gamma * q3
        q0 = cubic_points[0, :]
        q4 = cubic_points[3, :]
        q_points = np.append(q_points, (q0, q1, q2, q2, q3, q4), axis=0)
        return q_points

    def calc_len_bezier_quad(self, points: Any) -> Any:
        """Compute the exact arc length of a quadratic Bezier segment.

        Parameters
        ----------
        points
            Three control points of the quadratic segment.

        Returns
        -------
        The arc length.
        """

        a = points[0, :]
        b = points[1, :]
        c = points[2, :]

        B = b - a
        F = c - b
        A = F - B
        nF = np.linalg.norm(F)
        nA = np.linalg.norm(A)
        nB = np.linalg.norm(B)
        if nA > 1e-8:
            L = (nF * np.dot(A, F) - nB * np.dot(A, B)) / (nA**2) + (
                nA**2 * nB**2 - np.dot(A, B) ** 2
            ) / (nA**3) * (
                np.log(nA * nF + np.dot(A, F)) - np.log(nA * nB + np.dot(A, B))
            )
            return L
        else:
            return np.linalg.norm(a - c)

    def calc_len_with_quads(self) -> Any:
        """Estimate the path length from quadratic approximations.

        Returns
        -------
        The summed length of all quadratic segments.
        """
        L = 0
        for k in range(self.path.get_num_curves()):
            points = self.path.get_nth_curve_points(k)
            quads = self.cubic_to_quads(points)
            L0 = self.calc_len_bezier_quad(quads[:3, :])
            L1 = self.calc_len_bezier_quad(quads[3:, :])
            L += L0 + L1
        return L

    def get_path_length(self) -> Any:
        """Return the total length of the path.

        Returns
        -------
        The cumulative length at the final sample.
        """
        return self.pathdata_lengths[-1]

    def alpha_from_length(self, s: Any) -> Any:
        """Convert arc length to normalized path proportion.

        Parameters
        ----------
        s
            Arc length, or an iterable of arc lengths.

        Returns
        -------
        A proportion, or a list of proportions for iterable input.
        """
        if hasattr(s, "__iter__"):
            return [np.interp(t, self.pathdata_lengths, self.pathdata_alpha) for t in s]
        else:
            return np.interp(s, self.pathdata_lengths, self.pathdata_alpha)

    def length_from_alpha(self, a: Any) -> Any:
        """Convert normalized path proportion to arc length.

        Parameters
        ----------
        a
            Proportion, or an iterable of proportions.

        Returns
        -------
        An arc length, or a list of arc lengths for iterable input.
        """
        if hasattr(a, "__iter__"):
            return [np.interp(t, self.pathdata_alpha, self.pathdata_lengths) for t in a]
        else:
            return np.interp(a, self.pathdata_alpha, self.pathdata_lengths)

    def equalize_alpha(self, a: Any) -> Any:
        """Invert the alpha behaviour by mapping through path length.

        Parameters
        ----------
        a
            Input proportion.

        Returns
        -------
        The length-based proportion at the same path position.
        """
        return self.alpha_from_length(a * self.get_path_length())

    def equalize_rate_func(self, rate_func: Any) -> Any:
        """Wrap a rate function so motion follows constant arc length.

        Parameters
        ----------
        rate_func
            Rate function to be equalized.

        Returns
        -------
        A callable rate function that compensates for path length.

        Example:

        .. code-block:: python

            class TestPathMapperAnim(Scene):
                def construct(self):
                    mob1 = round_corners(
                        Triangle(fill_color=TEAL, fill_opacity=0).scale(3), 0.5
                    )
                    path_mapper = PathMapper(mob1)
                    mob2 = mob1.copy()
                    mob1.shift(LEFT * 2.5)
                    mob2.shift(RIGHT * 2.5)
                    self.play(
                        Create(mob1, rate_func=path_mapper.equalize_rate_func(smooth)),
                        Create(mob2),
                        run_time=5,
                    )
                    self.wait()
        """

        def eq_func(t: float) -> Any:
            """eq_func."""
            return self.equalize_alpha(rate_func(t))

        return eq_func

    def point_from_proportion(self, alpha: float) -> np.ndarray:
        """Return the point at a normalized path position.

        This overrides the base implementation with a precomputed length
        table for speed.

        Parameters
        ----------
        alpha
            Normalized path position, or an iterable of positions.

        Returns
        -------
        The point coordinates, or a stacked array of points for iterable
        input.
        """
        if hasattr(alpha, "__iter__"):
            values = self.alpha_from_length(alpha * self.get_path_length())
            ret = np.empty((0, 3))
            for a in values:
                if a == 1:
                    index = self.path.get_num_curves() - 1
                    remainder = 1
                else:
                    index = int(a * self.path.get_num_curves() // 1)
                    remainder = (a * self.path.get_num_curves()) % 1
                p = self.path.get_nth_curve_function(index)(remainder)
                ret = np.concatenate([ret, np.reshape(p, (1, 3))], axis=0)
            return ret
        else:
            a = self.alpha_from_length(alpha * self.get_path_length())
            if a == 1:
                index = self.path.get_num_curves() - 1
                remainder = 1
            else:
                index = int(a * self.path.get_num_curves() // 1)
                remainder = (a * self.path.get_num_curves()) % 1
            return self.path.get_nth_curve_function(index)(remainder)

    def get_length_between_points(self, b: Any, a: Any) -> Any:
        """Return the signed arc length between two path positions.

        Parameters
        ----------
        b
            Second position.
        a
            First position.

        Returns
        -------
        The signed length from ``a`` to ``b``.
        """
        return self.length_from_alpha(b) - self.length_from_alpha(a)

    def get_length_between_points_wrapped(self, b: Any, a: Any) -> Any:
        """Return the shortest wrapped distance between two positions.

        Parameters
        ----------
        b
            Second position.
        a
            First position.

        Returns
        -------
        The distance wrapped into the range minus half the path length to
        plus half the path length.
        """
        AB = self.get_length_between_points(b, a)
        L = self.get_path_length()
        return (AB % L - L / 2) % L - L / 2

    def get_length_between_points_tuple(self, b: Any, a: Any) -> Any:
        """Return both absolute lengths between two positions.

        Parameters
        ----------
        b
            Second position.
        a
            First position.

        Returns
        -------
        A tuple of the shorter and longer absolute lengths.
        """

        AB = abs(self.get_length_between_points(b, a))
        L = self.get_path_length()
        if AB > L / 2:
            return (L - AB), AB
        else:
            return AB, (L - AB)

    def get_bezier_index_from_length(self, s: Any) -> Any:
        """Locate the Bezier curve containing an arc length.

        Parameters
        ----------
        s
            Arc length.

        Returns
        -------
        The curve index and the local parameter within that curve.
        """
        a = self.alpha_from_length(s)
        nc = self.path.get_num_curves()
        indx = int(a * nc // 1)
        bz_a = a * nc % 1
        if indx == nc:
            indx = nc - 1
            bz_a = 1
        return (indx, bz_a)

    def get_tangent_unit_vector(self, s: Any) -> Any:
        """Return the unit tangent vector at an arc length.

        Parameters
        ----------
        s
            Arc length.

        Returns
        -------
        The normalized tangent direction.
        """
        # diff_bez_points = 1/3*(self.path.points[1:,:]-self.path.points[:-1,:])
        indx, bz_a = self.get_bezier_index_from_length(s)
        points = self.path.get_nth_curve_points(indx)
        dpoints = (points[1:, :] - points[:-1, :]) / 3
        bzf = bezier(dpoints)
        point = bzf(bz_a)
        return normalize(point)

    def get_tangent_angle(self, s: Any) -> Any:
        """Return the tangent angle at an arc length.

        Parameters
        ----------
        s
            Arc length.

        Returns
        -------
        The tangent direction as an angle in radians.
        """
        tv = self.get_tangent_unit_vector(s)
        return angle_of_vector(tv)

    def get_normal_unit_vector(self, s: Any) -> Any:
        """Return the unit normal vector at an arc length.

        Parameters
        ----------
        s
            Arc length.

        Returns
        -------
        The tangent rotated ninety degrees counter-clockwise.
        """
        tv = self.get_tangent_unit_vector(s)
        return rotate_vector(tv, PI / 2)

    def get_curvature_vector(self, s: Any) -> Any:
        """Return the curvature vector at an arc length.

        Parameters
        ----------
        s
            Arc length.

        Returns
        -------
        The curvature vector from the first and second derivatives.
        """
        indx, bz_a = self.get_bezier_index_from_length(s)
        points = self.path.get_nth_curve_points(indx)
        dpoints = (points[1:, :] - points[:-1, :]) * 3
        ddpoints = (dpoints[1:, :] - dpoints[:-1, :]) * 2
        deriv = bezier(dpoints)(bz_a)
        dderiv = bezier(ddpoints)(bz_a)
        curv = np.cross(deriv, dderiv) / (np.linalg.norm(deriv) ** 3)
        return curv

    def get_curvature(self, s: Any) -> Any:
        """Return the scalar curvature at an arc length.

        Parameters
        ----------
        s
            Arc length.

        Returns
        -------
        The magnitude of the curvature vector.
        """
        return np.linalg.norm(self.get_curvature_vector(s))


# DashedVMobject


class DashedLineMobject(VDict):
    """A dashed copy of a target mobject.

    Parameters
    ----------
    target_mobject
        Path that is split into dashes.
    num_dashes
        Number of dashes along the path.
    dashed_ratio
        Fraction of each dash period that is drawn.
    dash_offset
        Shift of the dash pattern along the path.
    **kwargs
        Keyword arguments forwarded to the dashed group.
    """

    def __init__(
        self,
        target_mobject: VMobject,
        num_dashes: Any = 15,
        dashed_ratio: Any = 0.5,
        dash_offset: Any = 0.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.path = PathMapper(
            target_mobject, num_of_path_points=10 * target_mobject.get_num_curves()
        )
        # self.path.add_updater(lambda mob: mob.generate_length_map())

        dshgrp = self.generate_dash_mobjects(
            **self.generate_dash_pattern_dash_distributed(
                num_dashes, dash_ratio=dashed_ratio, offset=dash_offset
            )
        )
        self.add({"dashes": dshgrp})
        self["dashes"].match_style(target_mobject)

    def generate_dash_pattern_metric(
        self, dash_len: Any, space_len: Any, num_dashes: Any, offset: Any = 0
    ) -> Any:
        """Build a dash pattern in metric curve-length space.

        Parameters
        ----------
        dash_len
            Length of each dash.
        space_len
            Length of each gap.
        num_dashes
            Number of dashes to generate.
        offset
            Offset of the pattern along the path.

        Returns
        -------
        Start and end lengths of the dashes.
        """
        period = dash_len + space_len
        n = num_dashes
        full_len = self.path.get_path_length()
        dash_starts = [(i * period + offset) for i in range(n)]
        dash_ends = [(i * period + dash_len + offset) for i in range(n)]
        k = 0
        while k < len(dash_ends):
            if dash_ends[k] < 0:
                dash_ends.pop(k)
                dash_starts.pop(k)
            k += 1

        k = 0
        while k < len(dash_ends):
            if dash_starts[k] > full_len:
                dash_ends.pop(k)
                dash_starts.pop(k)
            k += 1
        return {"dash_starts": dash_starts, "dash_ends": dash_ends}

    def generate_dash_pattern_dash_distributed(
        self, num_dashes: Any, dash_ratio: Any = 0.5, offset: Any = 0.0
    ) -> Any:
        """Distribute dashes evenly along the whole path.

        Parameters
        ----------
        num_dashes
            Number of dashes.
        dash_ratio
            Fraction of each period occupied by the dash.
        offset
            Pattern offset as a fraction of one period.

        Returns
        -------
        Start and end lengths of the dashes.
        """
        full_len = self.path.get_path_length()
        period = full_len / num_dashes
        dash_len = period * dash_ratio
        space_len = period * (1 - dash_ratio)
        n = num_dashes + 2

        return self.generate_dash_pattern_metric(
            dash_len, space_len, n, offset=(offset - 1) * period
        )

    def generate_dash_mobjects(
        self, dash_starts: Any = [0], dash_ends: Any = [1]
    ) -> Any:
        """Create mobjects for each dash interval.

        Parameters
        ----------
        dash_starts
            Start lengths of the dashes.
        dash_ends
            End lengths of the dashes.

        Returns
        -------
        A group containing one partial path per dash.
        """
        ref_mob = self.path.path
        a_list = self.path.alpha_from_length(dash_starts)
        b_list = self.path.alpha_from_length(dash_ends)
        ret = []
        for i in range(len(dash_starts)):
            mobcopy = VMobject().match_points(ref_mob)
            ret.append(mobcopy.pointwise_become_partial(ref_mob, a_list[i], b_list[i]))
        return VGroup(*ret)


class DashDotMobject(DashedLineMobject):
    """A dash-dot copy of a target mobject.

    Parameters
    ----------
    target_mobject
        Path that is split into dashes and dots.
    num_dashes
        Number of dash periods along the path.
    dashed_ratio
        Fraction of each period that is drawn.
    dash_offset
        Shift of the dash pattern along the path.
    dot_scale
        Size multiplier for the dots.
    **kwargs
        Keyword arguments forwarded to the dashed group.

    Examples
    --------
    .. manim:: DashDotMobjectScene
       :save_last_frame:

        from manim import Scene, VMobject, LEFT, UP, RIGHT, DOWN, BLUE
        from manim_extensions.cad_drawing_utils.path_mapper import DashDotMobject

        class DashDotMobjectScene(Scene):
            def construct(self):
                path = VMobject().set_points_smoothly(
                    [LEFT * 3, UP * 2, RIGHT * 3, DOWN * 2]
                )
                path.set_stroke(BLUE, 4)
                self.add(DashDotMobject(path, num_dashes=8, dashed_ratio=0.45))
    """

    def __init__(
        self,
        target_mobject: VMobject,
        num_dashes: Any = 15,
        dashed_ratio: Any = 0.35,
        dash_offset: Any = 0.0,
        dot_scale: Any = 1,
        **kwargs,
    ) -> None:
        super().__init__(
            target_mobject, num_dashes, dashed_ratio, dash_offset, **kwargs
        )
        dot = Circle(
            radius=target_mobject.get_stroke_width() / 100 * dot_scale,
            fill_opacity=1,
            stroke_opacity=0,
            num_components=6,
            fill_color=target_mobject.get_stroke_color(),
        )
        dash_marks = self.generate_dash_pattern_dash_distributed(
            num_dashes, dashed_ratio, dash_offset
        )

        full_len = self.path.get_path_length()
        if dash_marks["dash_starts"][0] < dash_marks["dash_ends"][0]:
            dot_marks = (
                np.array(
                    (
                        np.array(dash_marks["dash_starts"])[1:]
                        + np.array(dash_marks["dash_ends"])[:-1]
                    )
                )
                / 2
            )
        else:
            dot_marks = (
                np.array(
                    (
                        np.array(dash_marks["dash_starts"])
                        + np.array(dash_marks["dash_ends"])
                    )
                )
                / 2
            )

        dot_marks = dot_marks % full_len
        dots = VGroup(
            *[
                dot.copy().move_to(self.path.point_from_proportion(m / full_len))
                for m in dot_marks
            ]
        )
        self["dots"] = dots


class PathOffsetMobject(VMobject):
    """Offset a path along its normal vectors by a scalar function.

    Parameters
    ----------
    target_mobject
        Path to offset.
    ofs_func
        Function returning the offset distance at a path parameter.
    ofs_func_kwargs
        Keyword arguments forwarded to ``ofs_func``.
    num_of_samples
        Number of samples along the path.
    discontinuities
        Parameters where the offset function jumps.
    **kwargs
        Keyword arguments forwarded to the vector mobject.

    Examples
    --------
    .. manim:: PathOffsetScene
       :save_last_frame:

        from manim import Scene, Circle
        from manim_extensions.cad_drawing_utils.path_mapper import PathOffsetMobject

        class PathOffsetScene(Scene):
            def construct(self):
                base = Circle(radius=2)
                offset = PathOffsetMobject(base, lambda t: 0.3)
                self.add(base, offset)
    """

    def __init__(
        self,
        target_mobject: Any,
        ofs_func: Any,
        ofs_func_kwargs: Any = {},
        num_of_samples: Any = 100,
        discontinuities: Any = [],
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.ofs_func_kwargs = ofs_func_kwargs
        self.PM = PathMapper(target_mobject)
        self.PM.add_updater(lambda mob: mob.generate_length_map())
        self.discontinuities = discontinuities

        self.t_range = np.linspace(0, 1, num_of_samples)
        if discontinuities != []:
            t_disc = np.sort(
                np.concatenate(
                    (
                        np.array(self.discontinuities) + 1e-7,
                        np.array(self.discontinuities) - 1e-7,
                    )
                )
            )
            self.t_range = np.sort(np.concatenate((self.t_range, t_disc)))
        self.ofs_func = ofs_func
        self.s_scaling_factor = 1 / self.PM.get_path_length()
        self.points = self.generate_offset_paths()

    # this can be useful in lambdas for updaters
    def set_ofs_function_kwargs(self, ofs_func_kwargs: Any) -> Any:
        """Replace the keyword arguments passed to the offset function.

        Parameters
        ----------
        ofs_func_kwargs
            New keyword arguments.

        Returns
        -------
        ``None``; the arguments are stored on the instance.
        """
        self.ofs_func_kwargs = ofs_func_kwargs

    def generate_bezier_points(
        self, input_func: Any, t_range: Any, Smoothing: Any = True
    ) -> Any:
        """Sample a function and build cubic Bezier control points.

        Parameters
        ----------
        input_func
            Function sampled over ``t_range``.
        t_range
            Parameters at which the function is evaluated.
        Smoothing
            Whether to derive tangents from finite differences.

        Returns
        -------
        A list of four-point control sets, one per interval.
        """
        # generate bezier 4-lets with numerical difference
        out_data = []
        for k in range(len(t_range) - 1):
            t = t_range[k]
            t2 = t_range[k + 1]
            val1 = input_func(t)
            val2 = input_func(t2)
            p1 = val1
            p4 = val2
            if Smoothing:
                diff1 = (input_func(t + 1e-6) - input_func(t)) / 1e-6
                diff2 = (input_func(t2) - input_func(t2 - 1e-6)) / 1e-6
                p2 = val1 + diff1 * (t2 - t) / 3
                p3 = val2 - diff2 * (t2 - t) / 3
            else:
                p2 = (val1 * 2 + val2) / 3
                p3 = (val1 + val2 * 2) / 3
            out_data.append([p1, p2, p3, p4])
        return out_data

    def generate_ref_curve(self) -> Any:
        """Build the sampled reference curve from the source path.

        Returns
        -------
        ``None``; the curve and its path mapper are stored on the instance.
        """
        self.ref_curve = VMobject()
        bez_point = self.generate_bezier_points(
            self.PM.point_from_proportion, self.t_range
        )
        for point in bez_point:
            self.ref_curve.append_points(point)
        self.ref_curve_path = PathMapper(self.ref_curve)

    def generate_offset_func_points(self, Smoothing: Any = True) -> Any:
        """Sample the offset function and build Bezier control points.

        Parameters
        ----------
        Smoothing
            Whether to derive tangents from finite differences.

        Returns
        -------
        A list of four-point control sets for the offset curve.
        """
        points = self.generate_bezier_points(
            lambda t: self.ofs_func(t, **self.ofs_func_kwargs),
            self.t_range,
            Smoothing=Smoothing,
        )
        return points

    def generate_normal_vectors(self) -> Any:
        """Build normal vectors at every sampled path position.

        Returns
        -------
        A list of four-vector sets, one per sampled Bezier curve.
        """
        s_range = self.t_range * self.PM.get_path_length()
        # generate normal vectors from tangent angles and turning them 90°
        # the angles can be interpolated with bezier, unit normal vectors would not remain 'unit' under interpolation
        angles = self.generate_bezier_points(self.PM.get_tangent_angle, s_range)
        out = []
        for angle in angles:
            out.append([np.array([-np.sin(a), np.cos(a), 0]) for a in angle])
        return out

    def generate_offset_paths(
        self, gen_ofs_point: Any = True, gen_ref_curve: Any = True
    ) -> Any:
        """Build the offset path points.

        Parameters
        ----------
        gen_ofs_point
            Whether to regenerate the sampled offset points.
        gen_ref_curve
            Whether to regenerate the reference curve and normals.

        Returns
        -------
        The point array of the offset path.
        """
        if gen_ref_curve:
            self.generate_ref_curve()
            self.norm_vectors = self.generate_normal_vectors()
        if gen_ofs_point:
            self.ofs_points = self.generate_offset_func_points()

        n = self.ref_curve.get_num_curves()
        ofs_vectors = np.empty((n * 4, 3))
        for k in range(len(self.ofs_points)):
            for j in range(len(self.ofs_points[k])):
                ofs_vectors[k * 4 + j, :] = (
                    self.norm_vectors[k][j] * self.ofs_points[k][j]
                )

        return self.ref_curve.points + ofs_vectors

    def default_updater(
        self, gen_ofs_point: Any = True, gen_ref_curve: Any = True
    ) -> Any:
        """Refresh the offset path points for an updater callback.

        Parameters
        ----------
        gen_ofs_point
            Whether to regenerate the sampled offset points.
        gen_ref_curve
            Whether to regenerate the reference curve and normals.

        Returns
        -------
        ``None``; the points are replaced in place.
        """
        self.points = self.generate_offset_paths(gen_ofs_point, gen_ref_curve)


class CurveWarp(VMobject):
    """Wrap a source path onto another curve at an anchor point.

    Parameters
    ----------
    warp_source
        Path whose local coordinates are mapped onto the warp curve.
    warp_curve
        Curve that receives the warped path.
    anchor_point
        Proportion of the warp curve used as the origin.
    **kwargs
        Keyword arguments forwarded to the vector mobject.

    Examples
    --------
    .. manim:: CurveWarpScene
       :save_last_frame:

        from manim import Scene, Circle, Line
        from manim_extensions.cad_drawing_utils.path_mapper import CurveWarp

        class CurveWarpScene(Scene):
            def construct(self):
                source = Line(LEFT, RIGHT)
                guide = Circle(radius=2)
                warped = CurveWarp(source, guide)
                self.add(guide, warped)
    """

    def __init__(
        self,
        warp_source: VMobject,
        warp_curve: VMobject,
        anchor_point: Any = 0.5,
        **kwargs,
    ) -> None:

        self.warp_curve = warp_curve
        self.warp_source = warp_source
        self.PM = PathMapper(self.warp_curve)
        self.anchor_point = anchor_point
        super().__init__(**kwargs)
        self.match_style(warp_source)

    def generate_points(self) -> Any:
        """Map the source path points onto the warp curve.

        Returns
        -------
        ``None``; the mapped points are stored on the instance.
        """
        s0 = self.PM.length_from_alpha(self.anchor_point)
        x_points = self.warp_source.points[:, 0] + s0
        y_points = self.warp_source.points[:, 1]
        L = self.PM.get_path_length()

        if self.warp_curve.is_closed():
            # if the curve is closed, out-of-bound x values can wrap around to the beginning
            x_points = x_points % L
            x_curve_points = self.PM.point_from_proportion(x_points / L)
            nv = [self.PM.get_normal_unit_vector(x) for x in x_points]
            y_curve_points = np.array(
                [tuplie[0] * tuplie[1] for tuplie in zip(nv, y_points)]
            )
            self.points = x_curve_points + y_curve_points
        else:
            self.points = np.empty((0, 3))
            for x, y in zip(x_points, y_points):
                if 0 < x <= L:
                    p = (
                        self.PM.point_from_proportion(x / L)
                        + self.PM.get_normal_unit_vector(x) * y
                    )
                    self.points = np.append(self.points, np.reshape(p, (1, 3)), axis=0)
                elif x > L:
                    endpoint = self.PM.point_from_proportion(1)
                    tanv = self.PM.get_tangent_unit_vector(L)
                    nv = rotate_vector(tanv, PI / 2)
                    x_1 = x - L
                    p = endpoint + x_1 * tanv + y * nv
                    self.points = np.append(self.points, np.reshape(p, (1, 3)), axis=0)
                else:
                    startpoint = self.PM.point_from_proportion(0)
                    tanv = self.PM.get_tangent_unit_vector(0)
                    nv = rotate_vector(tanv, PI / 2)
                    x_1 = x
                    p = startpoint + x_1 * tanv + y * nv
                    self.points = np.append(self.points, np.reshape(p, (1, 3)), axis=0)
