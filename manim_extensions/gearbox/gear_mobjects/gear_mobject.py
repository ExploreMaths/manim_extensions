# SPDX-FileCopyrightText: 2020 GarryBGoode
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Gear mobject for Manim.

This module provides gear and rack visualizations.

"""

import numpy as np
from manim import *
from typing import Optional, Sequence
from scipy.optimize import fsolve
from scipy.optimize import least_squares
import warnings

__all__ = [
    "involute_func",
    "involute_deriv_func",
    "involute_height_func",
    "involute_point_gen",
    "Gear",
    "Rack",
]


def involute_func(t, r, a=0, rad_offs=0, tan_offs=0):
    """
    Returns the x-y-z values of the involute function.

    Parameters
    ----------
    t: input angle or sequence of angles.
    r: base circle radius.
    a: offset angle.
    rad_offs: radial offset.
    tan_offs: tangential offset.

    Examples
    --------
    .. manim:: InvoluteFuncExample
       :save_last_frame:

       from manim import *
       from manim_extensions.gearbox.gear_mobjects.gear_mobject import involute_func

       class InvoluteFuncExample(Scene):
           def construct(self):
               base_circle = Circle(radius=1.0, color=GREY_B)
               t = np.linspace(0, np.pi, 50)
               points = involute_func(t, 1.0)
               curve = VMobject()
               curve.set_points_smoothly(points)
               curve.set_color(PURE_YELLOW)
               self.add(base_circle, curve, Dot(points[-1], color=RED))
    """

    def involute_val(val):
        """Compute a single point on the involute tooth profile.

        Parameters
        ----------
        val : float
            The involute parameter angle.

        Returns
        -------
        numpy.ndarray
            A 3-D point ``(x, y, 0)`` on the involute curve.
        """
        x = (
            r * (np.cos(val) + (val - a) * np.sin(val - a))
            + rad_offs * np.cos(val)
            - tan_offs * np.sin(val)
        )
        y = (
            r * (np.sin(val) - (val - a) * np.cos(val - a))
            + rad_offs * np.sin(val)
            + tan_offs * np.cos(val)
        )
        z = 0
        return np.array((x, y, z))

    if hasattr(t, "__iter__"):
        ret = np.empty((0, 3))
        for u in t:
            point = involute_val(u)
            point = np.reshape(point, (1, 3))
            ret = np.concatenate((ret, point), 0)
        return ret
    else:
        return involute_val(t)


def involute_deriv_func(t, r, a=0, rad_offs=0, tan_offs=0):
    """Return the derivative of the involute function at angle t.

    Parameters
    ----------
    t: angle or sequence of angles at which to evaluate the derivative.
    r: base circle radius.
    a: offset angle.
    rad_offs: radial offset.
    tan_offs: tangential offset.

    Examples
    --------
    .. manim:: InvoluteDerivFuncExample
       :save_last_frame:

       from manim import *
       from manim_extensions.gearbox.gear_mobjects.gear_mobject import (
           involute_deriv_func,
           involute_func,
       )

       class InvoluteDerivFuncExample(Scene):
           def construct(self):
               base_circle = Circle(radius=1.0, color=GREY_B)
               t = np.linspace(0, np.pi / 2, 20)
               points = involute_func(t, 1.0)
               derivs = involute_deriv_func(t, 1.0)
               curve = VMobject()
               curve.set_points_smoothly(points)
               curve.set_color(WHITE)
               vectors = VGroup(
                   *[
                       Arrow(
                           p,
                           p + 0.25 * d / np.linalg.norm(d),
                           buff=0,
                           color=PURE_YELLOW,
                       )
                       for p, d in zip(points[1::4], derivs[1::4])
                   ]
               )
               self.add(base_circle, curve, vectors)
    """

    def diff_val(val):
        """Compute the derivative of the involute profile at a given parameter.

        Parameters
        ----------
        val : float
            The involute parameter angle.

        Returns
        -------
        numpy.ndarray
            A 3-D derivative vector ``(dx, dy, 0)``.
        """
        x = (
            r * (-np.sin(val) + (val - a) * np.cos(val - a) + np.sin(val - a))
            - rad_offs * np.sin(val)
            - tan_offs * np.cos(val)
        )
        y = (
            r * (np.cos(val) + (val - a) * np.sin(val - a) - np.cos(val - a))
            + rad_offs * np.cos(val)
            - tan_offs * np.sin(val)
        )
        z = 0
        return np.array((x, y, z))

    if hasattr(t, "__iter__"):
        ret = np.empty((0, 3))
        for u in t:
            point = diff_val(u)
            point = np.reshape(point, (1, 3))
            ret = np.concatenate((ret, point), 0)
        return ret
    else:
        return diff_val(t)


def involute_height_func(k, r, **kwargs):
    """
    Returns the radial height of the involute compared to the base circle.

    Parameters
    ----------
    k: angle or sequence of angles.
    r: base circle radius.
    **kwargs: forwarded to :func:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.involute_func`.

    Examples
    --------
    .. manim:: InvoluteHeightFuncExample
       :save_last_frame:

       from manim import *
       from manim_extensions.gearbox.gear_mobjects.gear_mobject import (
           involute_func,
           involute_height_func,
       )

       class InvoluteHeightFuncExample(Scene):
           def construct(self):
               base_circle = Circle(radius=1.0, color=GREY_B)
               k_val = np.pi / 4
               point = involute_func(k_val, 1.0)
               height = involute_height_func(k_val, 1.0)
               self.add(
                   base_circle,
                   Line(ORIGIN, point, color=PURE_YELLOW),
                   Dot(point, color=RED),
                   Tex(f"h = {height:.3f}", font_size=30).to_edge(UP),
               )
    """
    return np.linalg.norm(involute_func(k, r, **kwargs)) - r


def involute_point_gen(t, r, **kwargs):
    """
    Returns a list of points to be for cubic bezier approximation of the involute curve.
    Output is compatible with Mobject.points.
    Input t is a list where the involute shall be evaluated, it can be unevenly spaced.
    Anchors are added automatically.

    Parameters
    ----------
    t: sequence of angles at which to evaluate the involute.
    r: base circle radius.
    **kwargs: forwarded to :func:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.involute_func` and :func:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.involute_deriv_func`.

    Examples
    --------
    .. manim:: InvolutePointGenExample
       :save_last_frame:

       from manim import *
       from manim_extensions.gearbox.gear_mobjects.gear_mobject import involute_point_gen

       class InvolutePointGenExample(Scene):
           def construct(self):
               base_circle = Circle(radius=1.0, color=GREY_B)
               t = np.linspace(0, np.pi / 2, 10)
               points = involute_point_gen(t, 1.0)
               curve = VMobject()
               curve.points = points
               curve.set_stroke(PURE_YELLOW, 3)
               self.add(base_circle, curve)
    """
    end_points = involute_func(t, r, **kwargs)
    diff_points = involute_deriv_func(t, r, **kwargs)
    out_points = np.empty((0, 3))
    for i in range(len(t) - 1):
        t_ratio = (t[i + 1] - t[i]) / 3
        point1 = end_points[i, :]
        point2 = end_points[i + 1, :]
        anchor_1 = point1 + diff_points[i, :] * t_ratio
        anchor_2 = point2 - diff_points[i + 1, :] * t_ratio
        out_points = np.append(
            out_points,
            [end_points[i, :], anchor_1, anchor_2, end_points[i + 1, :]],
            axis=0,
        )

    return out_points


class Gear(VMobject):
    """A Manim mobject representing an involute gear.

    The gear is constructed from involute curves and can mesh with other
    :class:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear` objects (or :class:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Rack` objects) using :meth:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear.mesh_to`.

    Two gears mesh correctly when they share the same *module* and *alpha*
    (pressure angle). The pitch-circle radius of a gear is
    ``module * num_of_teeth / 2``.

    .. inheritance-diagram:: manim_extensions.gearbox.Gear
       :parts: 1

    Parameters
    ----------
    num_of_teeth : int
        Number of gear teeth.
    module : float, optional
        Standard size scaling parameter. ``diameter = module * num_of_teeth``.
        Defaults to ``0.2``.
    alpha : float, optional
        Pressure angle in degrees. Affects tooth curvature. Suggested values
        are between ``10`` and ``30``. Defaults to ``20``.
    h_a : float, optional
        Addendum coefficient (tooth height above the pitch circle).
        Defaults to ``1``.
    h_f : float, optional
        Dedendum coefficient (tooth height below the pitch circle).
        Defaults to ``1.2``.
    inner_teeth : bool, optional
        If ``True``, generate a ring gear with teeth pointing inward.
        Defaults to ``False``.
    profile_shift : float, optional
        Profile-shift coefficient. Changes the tooth shape and diameter
        slightly and reduces undercut. Defaults to ``0``.
    cutout_teeth_num : int, optional
        Number of teeth to omit. Defaults to ``0``.
    nppc : int, optional
        Number of points per involute curve. One tooth is built from four to
        six curve pieces depending on undercut. Defaults to ``5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: GearDocExample

       from manim import *
       from manim_extensions.gearbox import Gear

       class GearDocExample(Scene):
           def construct(self):
               gear1 = Gear(15, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
               gear2 = Gear(25, stroke_opacity=0, fill_color=RED, fill_opacity=1)
               gear1.shift(-gear1.rp * 1.5 * RIGHT)
               gear2.mesh_to(gear1)
               contact = Dot(gear1.get_center() + gear1.rp * RIGHT, color=PURE_YELLOW)

               self.add(gear1, gear2, contact)
               self.play(
                   Rotate(gear1, gear1.pitch_angle, rate_func=linear),
                   Rotate(gear2, -gear2.pitch_angle, rate_func=linear),
                   run_time=4,
               )
               self.wait()
    """

    def __init__(
        self,
        num_of_teeth,
        module=0.2,
        alpha=20,
        h_a=1,
        h_f=1.2,
        inner_teeth=False,
        profile_shift=0,
        cutout_teeth_num=0,
        nppc=5,
        **kwargs,
    ):
        """Create an involute gear. See the class docstring for parameter details."""
        self.z = num_of_teeth
        self.z_cut = cutout_teeth_num
        self.m = module

        # rp = pitch circle
        # when 2 gears mesh, their pitch circles need to be tangent
        self.rp = module * self.z / 2
        # pressure angle
        self.alpha = alpha
        # tooth height
        self.h = (h_a + h_f) * self.m
        # addendum and dedendum coefficients
        self.h_a = h_a
        self.h_f = h_f
        # arc length of a tooth-period
        self.pitch = self.m * PI
        # base circle of involute function
        self.rb = self.rp * np.cos(self.alpha * DEGREES)
        self.X = profile_shift * module

        # for inner teeth, the top / bottom extensions are reversed
        if inner_teeth:
            # ra : outer radius (top of teeth)
            self.ra = self.rp + self.m * (h_f + profile_shift)
            # rf: inner radius (bottom of teeth)
            self.rf = self.rp - self.m * (h_a - profile_shift)
        else:
            self.ra = self.rp + self.m * (h_a + profile_shift)
            self.rf = self.rp - self.m * (h_f - profile_shift)
        self.inner_teeth = inner_teeth

        # angle_ofs: to be used with the construction of involutes
        self.angle_ofs = 0
        # angular period of teeth
        self.pitch_angle = self.pitch / self.rp
        # number of points per involute curve and per arc
        self.nppc = nppc

        # note: points are created by the 'generate_points' function, which is called by some of the supers upon init
        super().__init__(**kwargs)

        # this submobject is used for tracking the center and reference angle of the gear
        self.submobjects.append(
            Line(start=ORIGIN, end=RIGHT, stroke_opacity=0, fill_opacity=0)
        )

    def get_center(self):
        """Return the geometric center of the gear."""
        return self.submobjects[0].points[0, :].copy()

    def get_angle_vector(self):
        """Return the internal reference vector used to track rotation."""
        return self.submobjects[0].points[1, :] - self.submobjects[0].points[0, :]

    def get_angle(self):
        """Return the current rotation angle of the gear in radians."""
        v = self.get_angle_vector()
        return np.arctan2(v[1], v[0])

    def set_stroke(self, color=None, **kwargs):
        """Override set_stroke to avoid revealing the line which is used for tracking center and angle.
            If family is specified, it will still do it.

        Parameters
        ----------
        color
        The color to apply.
        kwargs
        Kwargs processed by this operation.
        """
        if "family" in kwargs:
            super().set_stroke(color, **kwargs)
        else:
            kwargs.pop("family")
            super().set_stroke(color, family=False, **kwargs)

    def generate_points(self):
        """Build the gear outline from involute curves, fillets, and arcs."""

        # involute starts at 0 angle at rb, but it should be at 0 on rp, so need an offset angle
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                angle_base = fsolve(
                    lambda u: involute_height_func(u, self.rb) - (self.rp - self.rb),
                    self.alpha * DEGREES,
                    xtol=1e-10,
                )
        except Exception:
            angle_base = np.array([self.alpha * DEGREES])
        self.angle_ofs = angle_base[0] - self.alpha * DEGREES

        # from tec-science article
        # https://www.tec-science.com/mechanical-power-transmission/involute-gear/profile-shift/
        # thicknes of the tooth on the pitch circle
        s0 = self.pitch / 2 + 2 * self.X * np.tan(self.alpha * DEGREES)
        # increment due to profile shift
        ds = s0 - self.pitch / 2
        # angle change from profile shift
        da = ds / 2 / self.rp

        self.angle_ofs = angle_base[0] - self.alpha * DEGREES + da

        # find t-range for the involute that lies inside the rf-ra range
        def invo_cross_diff(t):
            """Compute the y-coordinate where two involute flanks intersect.

            Used to find the maximum involute height before the tooth tip.

            Parameters
            ----------
            t : float
                The involute parameter angle.

            Returns
            -------
            float
                The y-coordinate of the rotated involute point.
            """
            p1 = rotate_vector(
                involute_func(t[0], self.rb), self.pitch_angle / 4 + self.angle_ofs
            )
            # when y coordinate is 0, the 2 involutes of the tooth would intersect because of the symmetry
            return p1[1]

        # find max height
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                t_hmax = fsolve(invo_cross_diff, angle_base[0] * 2)
        except Exception:
            t_hmax = np.array([angle_base[0] * 2])
        hmax = involute_height_func(t_hmax[0], self.rb)

        undercut = False
        if self.ra > self.rb + hmax:
            self.ra = self.rb + hmax
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                res = fsolve(
                    lambda u: involute_height_func(u, self.rb) - (self.ra - self.rb),
                    self.alpha * DEGREES,
                    xtol=1e-9,
                )
        except Exception:
            res = np.array([self.alpha * DEGREES])
        tmax = res[0]
        if self.rf > self.rb:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    res = fsolve(
                        lambda u: involute_height_func(u, self.rb)
                        - (self.rf - self.rb),
                        self.alpha * DEGREES,
                        xtol=1e-9,
                    )
            except Exception:
                res = np.array([self.alpha * DEGREES])
            tmin = res[0]
        else:
            tmin = 0

        ucut_amount = self.rf / np.cos(self.alpha * DEGREES) - self.rb
        v_loc = (self.rb + ucut_amount) * RIGHT
        v_loc_2 = rotate_vector(v_loc, -self.alpha * DEGREES)
        ofs_vector = -self.rp * RIGHT + v_loc_2
        rad_ucut = ofs_vector[0]
        tan_ucut = ofs_vector[1]

        def undercut_func(t):
            """Compute a point on the undercut (radial) curve at parameter ``t``.

            Parameters
            ----------
            t : float
                The involute parameter angle.

            Returns
            -------
            numpy.ndarray
                A point on the undercut curve.
            """
            return involute_func(t, self.rp, rad_offs=rad_ucut, tan_offs=tan_ucut)

        # undercut happening according to standard criteria OR
        # if the root circle is smaller than the base, I'm using the undercut curve to smooth out the transition between
        # base and root, simply because it provides a nice tangent curve.
        if self.z < 2 / (np.sin(self.alpha * DEGREES) ** 2) or self.rf < self.rb:
            undercut = True

            def diff_val_func(t):
                """Compute the 2-D distance between undercut and involute curves.

                Parameters
                ----------
                t : list of float
                    ``[t_undercut, t_involute]`` parameter values.

                Returns
                -------
                numpy.ndarray
                    The ``(x, y)`` difference vector.
                """
                invo_val = rotate_vector(
                    involute_func(-np.abs(t[1]), self.rb), -self.alpha * DEGREES
                )
                ucut_val = undercut_func(t[0])
                diff = ucut_val - invo_val
                return diff[0:2]

            def _solve_undercut_intersection():
                """Find the intersection of undercut and involute curves robustly."""
                candidates = [
                    np.array([0.01, 0.05]),
                    np.array([0.005, 0.025]),
                    np.array([0.02, 0.1]),
                    np.array([0.001, 0.01]),
                ]
                best_result = None
                best_cost = np.inf
                for x0 in candidates:
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            sol, info, ier, msg = fsolve(
                                diff_val_func, x0, full_output=True, maxfev=1000
                            )
                        residual = np.linalg.norm(diff_val_func(sol))
                        if ier == 1 and residual < best_cost:
                            best_cost = residual
                            best_result = sol
                        elif residual < best_cost:
                            best_cost = residual
                            best_result = sol
                    except Exception:
                        continue
                if best_result is not None:
                    return best_result
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        res = least_squares(
                            lambda t: diff_val_func([t[0], t[1]]),
                            x0=np.array([0.01, 0.05]),
                            bounds=([-np.pi, -np.pi], [np.pi, np.pi]),
                        )
                    return res.x
                except Exception:
                    return np.array([0.01, 0.05])

            tres_ucut = _solve_undercut_intersection()
            tmin = tres_ucut[1]
            if tmin < 0:
                tmin = -tmin
            tmax_ucut = tres_ucut[0]

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    sol_ucut, info_ucut, ier_ucut, _ = fsolve(
                        lambda t: np.linalg.norm(undercut_func(t)) - self.rf,
                        0.0,
                        full_output=True,
                        xtol=1e-12,
                    )
                tmin_ucut = sol_ucut[0]
            except Exception:
                tmin_ucut = 0.0
            t_range_ucut = np.linspace(tmin_ucut, tmax_ucut, self.nppc)
            undercut_curve = VMobject()
            undercut_curve.points = involute_point_gen(
                t_range_ucut, self.rp, rad_offs=rad_ucut, tan_offs=tan_ucut
            )

        trange_invo = np.linspace(-tmax, -tmin, self.nppc)
        involute_curve = VMobject()
        involute_curve.points = involute_point_gen(trange_invo, self.rb)
        involute_curve.rotate_about_origin(-self.alpha * DEGREES)

        if undercut:
            undercut_curve.reverse_direction()
            mid_point = (undercut_curve.points[1, :] + involute_curve.points[-2, :]) / 2
            undercut_curve.points[0, :] = mid_point
            involute_curve.points[-1, :] = mid_point
            involute_curve.append_points(undercut_curve.points)

        # rotate to construction position
        involute_curve.rotate(
            angle=self.pitch_angle / 4 + self.angle_ofs + self.alpha * DEGREES,
            about_point=ORIGIN,
        )

        involute_curve2 = involute_curve.copy().flip(axis=RIGHT, about_point=ORIGIN)

        angle_bot_point = involute_curve.points[-1]
        angle_bot = np.arctan2(angle_bot_point[1], angle_bot_point[0])
        arc_bot_1 = Arc(
            radius=self.rf,
            start_angle=angle_bot,
            angle=self.pitch_angle / 2 - angle_bot,
            num_components=self.nppc // 2 + 1,
        )
        arc_bot_2 = arc_bot_1.copy().flip(axis=RIGHT, about_point=ORIGIN)
        arc_bot_1.reverse_points()
        arc_top = ArcBetweenPoints(
            radius=self.rf,
            start=involute_curve2.points[0],
            end=involute_curve.points[0],
            num_components=self.nppc,
        )
        arc_top.reverse_points()

        involute_curve.reverse_direction()

        def smooth_curve_joint(curve1: VMobject, curve2: VMobject):
            """Smoothly join two curves by inserting a midpoint between their ends.

            Parameters
            ----------
            curve1 : VMobject
                The first curve (modified in place).
            curve2 : VMobject
                The second curve (modified in place).
            """
            mid_point = (curve2.points[1, :] + curve1.points[-2, :]) / 2
            curve2.points[0, :] = mid_point
            curve1.points[-1, :] = mid_point

        smooth_curve_joint(arc_bot_1, involute_curve)
        smooth_curve_joint(involute_curve, arc_top)
        smooth_curve_joint(arc_top, involute_curve2)
        smooth_curve_joint(involute_curve2, arc_bot_2)

        tooth_curve_points = np.concatenate(
            (
                arc_bot_1.points,
                involute_curve.points,
                arc_top.points,
                involute_curve2.points,
                arc_bot_2.points,
            )
        )

        self.points = np.empty((0, 3))
        for k in range(self.z - self.z_cut):
            self.points = np.concatenate((self.points, tooth_curve_points), 0)
            self.rotate(self.pitch / self.rp, about_point=ORIGIN)

        if self.z_cut != 0:
            self.rotate(
                -self.pitch_angle * (self.z - self.z_cut + 1) / 2, about_point=ORIGIN
            )
            arc_patch = Arc(
                start_angle=np.arctan2(self.points[-1, 1], self.points[-1, 0]),
                angle=-self.z_cut * self.pitch_angle,
                radius=self.rf,
                arc_center=ORIGIN,
            )

            self.append_points(arc_patch.points)

        if self.inner_teeth:
            Outer_ring = Circle(radius=self.ra * 1.1)
            self.append_points(Outer_ring.points)

    def mesh_to(self, gear2: "Gear", offset: float = 0, bias=1):
        """This will position and rotate the gear (self) next to the input gear2 so that they mesh properly.

        Parameters
        ----------
        gear2: the other gear this gear (self) will mesh to. gear2 will not move due to meshing, only the 'self'.
        offset: axial distance offset coefficient. The gears will be offset*module further apart than default.
        positive_bias: When offset is used, there will play between gears. If positive_bias= True,
            this function meshes 'self' gear to gear2 as if there was a positive rotation torque on 'self'.
        """

        # -- Rack branch -----------------------------------------------------------
        if isinstance(gear2, Rack):
            rack_center = gear2.get_center()
            rack_angle = gear2.get_angle()

            # Rack pitch line direction (along the rack's length) and its normal
            pitch_dir = np.array([np.cos(rack_angle), np.sin(rack_angle), 0])
            pitch_normal = np.array([-np.sin(rack_angle), np.cos(rack_angle), 0])

            diff_vect = self.get_center() - rack_center
            distance = np.linalg.norm(diff_vect)
            if distance != 0:
                diff_vect = diff_vect / distance
            else:
                diff_vect = pitch_normal

            # Pitch distance for external gear-rack meshing
            pitch_dist = self.rp + offset * self.m + self.X

            self.shift(diff_vect * (-distance + pitch_dist))

            # Rotate gear so its teeth mesh with the rack's teeth.
            # For a rack the tooth phase is linear; the gear must rotate so that
            # a gear tooth aligns with a rack tooth gap at the pitch point.
            diff_angle = np.arctan2(diff_vect[1], diff_vect[0])
            mod1 = (
                (self.get_angle() - diff_angle - PI)
                % self.pitch_angle
                / self.pitch_angle
            )
            self.rotate((-mod1 + 0.5) * self.pitch_angle)
            return

        # get the basic distance vector
        # remember: diff vect points towards self
        diff_vect = self.get_center() - gear2.get_center()
        distance = np.linalg.norm(diff_vect)
        if distance != 0:
            # making it unit vector
            diff_vect = diff_vect / distance
        else:
            diff_vect = RIGHT

        # calculate necessary axial distance. Inside-gears complicate things, as usual.
        # The pitch point is not in the middle between pitch circles. The calculation is based on triangle relations.
        if gear2.inner_teeth:
            pitch_dist = gear2.rp - self.rp - offset * self.m - self.X + gear2.X
            rp1 = self.rb * pitch_dist / (-self.rb + gear2.rb)
            rp2 = gear2.rb * pitch_dist / (-self.rb + gear2.rb)
        elif self.inner_teeth:
            pitch_dist = -gear2.rp + self.rp - offset * self.m + self.X - gear2.X
            rp1 = self.rb * pitch_dist / (self.rb - gear2.rb)
            rp2 = gear2.rb * pitch_dist / (self.rb - gear2.rb)
        else:
            pitch_dist = self.rp + gear2.rp + offset * self.m + self.X + gear2.X
            rp1 = self.rb * pitch_dist / (self.rb + gear2.rb)
            rp2 = gear2.rb * pitch_dist / (self.rb + gear2.rb)

        self.shift(diff_vect * (-distance + pitch_dist))

        if offset != 0 or gear2.X != 0 or self.X != 0:
            # find the invo roll-angle where the curve goes as high (out) as the pitch point
            if self.inner_teeth:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        invo_offset_1 = fsolve(
                            lambda t: involute_height_func(t, self.rb)
                            - (rp1 - self.rb),
                            self.angle_ofs + self.alpha * DEGREES,
                        )
                except Exception:
                    invo_offset_1 = np.array([self.angle_ofs + self.alpha * DEGREES])
            else:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        invo_offset_1 = fsolve(
                            lambda t: involute_height_func(t, self.rb)
                            - (rp1 - self.rb),
                            self.angle_ofs + self.alpha * DEGREES,
                        )
                except Exception:
                    invo_offset_1 = np.array([self.angle_ofs + self.alpha * DEGREES])
            if gear2.inner_teeth:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        invo_offset_2 = fsolve(
                            lambda t: involute_height_func(t, gear2.rb)
                            - (rp2 - gear2.rb),
                            gear2.angle_ofs + gear2.alpha * DEGREES,
                        )
                except Exception:
                    invo_offset_2 = np.array([gear2.angle_ofs + gear2.alpha * DEGREES])
            else:
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        invo_offset_2 = fsolve(
                            lambda t: involute_height_func(t, gear2.rb)
                            - (rp2 - gear2.rb),
                            gear2.angle_ofs + gear2.alpha * DEGREES,
                        )
                except Exception:
                    invo_offset_2 = np.array([gear2.angle_ofs + gear2.alpha * DEGREES])
            invo_point_1 = involute_func(invo_offset_1[0], self.rb)
            invo_point_2 = involute_func(invo_offset_2[0], gear2.rb)
            angle_offset_1 = bias * (
                np.arctan2(invo_point_1[1], invo_point_1[0]) - self.angle_ofs
            )
            angle_offset_2 = bias * (
                np.arctan2(invo_point_2[1], invo_point_2[0]) - gear2.angle_ofs
            )

        else:
            angle_offset_1 = 0
            angle_offset_2 = 0

        # angle of the diff vector
        diff_angle = np.arctan2(diff_vect[1], diff_vect[0])

        # get the 'tooth-phases'
        # these mods represent how much a gear has turned within the repeating pattern of the teeth
        # diff_angle needs to be considered for turning due to movement. Think planetary gear movement.
        # In some places -PI is involved due to diff vector pointing towards or away from the pitch point
        # (and sometimes added PI due to experimentation)
        if self.inner_teeth:
            mod1 = (
                (self.get_angle() - diff_angle - PI - angle_offset_1)
                % self.pitch_angle
                / self.pitch_angle
            )
            mod2 = (
                (gear2.get_angle() - diff_angle - PI - angle_offset_2)
                % gear2.pitch_angle
                / gear2.pitch_angle
            )
        elif gear2.inner_teeth:
            mod1 = (
                (self.get_angle() - diff_angle - angle_offset_1)
                % self.pitch_angle
                / self.pitch_angle
            )
            mod2 = (
                (gear2.get_angle() - diff_angle - angle_offset_2)
                % gear2.pitch_angle
                / gear2.pitch_angle
            )
        else:
            mod1 = (
                (self.get_angle() - diff_angle - PI - angle_offset_1)
                % self.pitch_angle
                / self.pitch_angle
            )
            mod2 = (
                (gear2.get_angle() - diff_angle - angle_offset_2)
                % gear2.pitch_angle
                / gear2.pitch_angle
            )

        # with inside gears, the tooth goes into a tooth-hole, they overlap
        if self.inner_teeth or gear2.inner_teeth:
            self.rotate((+mod2 - mod1) * self.pitch_angle)
        # with outside gears, the tooth pattern needs to shift half-cycle, and the rotation is reversed
        else:
            self.rotate((-mod2 - mod1 + 0.5) * self.pitch_angle)

    def rotate(
        self,
        angle: float,
        axis: np.ndarray = OUT,
        about_point: Optional[Sequence[float]] = None,
        **kwargs,
    ):
        """Rotate the gear around its centre by default.

        Parameters
        ----------
        angle : float
            Rotation angle in radians.
        axis : np.ndarray, optional
            Rotation axis (default ``OUT``).
        about_point : sequence of float or None, optional
            Centre point for the rotation.  If ``None`` the gear's own
            centre is used.
        """
        if about_point is None:
            ret = super().rotate(angle, axis, about_point=self.get_center(), **kwargs)
        else:
            ret = super().rotate(angle, axis, about_point=about_point, **kwargs)
        return ret


class Rack(VMobject):
    """A Manim mobject representing a rack for involute gears.

    The rack must use the same module and pressure angle as the mating gear
    for proper meshing.

    .. manim:: RackExample

       from manim import *
       from manim_extensions.gearbox import Gear, Rack

       class RackExample(Scene):
           def construct(self):
               gear = Gear(15, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
               rack = Rack(
                   12, module=gear.m, stroke_opacity=0, fill_color=RED, fill_opacity=1
               )
               gear.mesh_to(rack)

               self.add(gear, rack)
               self.play(Rotate(gear, gear.pitch_angle, rate_func=linear), run_time=2)
               self.wait()
    Parameters
    ----------
    num_of_teeth : int
        Number of teeth on the rack.
    module : float, optional
        Standard size scaling parameter.  Defaults to ``0.2``.
    alpha : float, optional
        Pressure angle in degrees.  Defaults to ``20``.
    h_a : float, optional
        Addendum coefficient (tooth height above the pitch line).
        Defaults to ``1``.
    h_f : float, optional
        Dedendum coefficient (tooth height below the pitch line).
        Defaults to ``1.17``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VMobject`.
    """

    def __init__(self, num_of_teeth, module=0.2, alpha=20, h_a=1, h_f=1.17, **kwargs):
        """Initialize Rack."""
        self.z = num_of_teeth
        self.m = module

        # pressure angle
        self.alpha = alpha
        # tooth height
        self.h = (h_a + h_f) * self.m
        # addendum and dedendum coefficients
        self.h_a = h_a
        self.h_f = h_f
        # arc length of a tooth-period
        self.pitch = self.m * PI

        # note: points are created by the 'generate_points' function, which is called by some of the supers upon init
        super().__init__(**kwargs)

        # these submobjects are a bit of a hack
        # they are used to track the center and angular position of the gear
        self.submobjects.append(
            Line(start=ORIGIN, end=UP, stroke_opacity=0, fill_opacity=0)
        )

    def generate_points(self):
        """Build the rack outline from trapezoidal teeth."""

        h_amax = self.pitch / 4 / np.tan(self.alpha * DEGREES)
        da = self.pitch / 4 * (h_amax - self.h_a * self.m) / h_amax
        h_fmax = h_amax
        df = self.pitch / 4 * (h_fmax - self.h_f * self.m) / h_amax

        tooth_points = [
            UP * (self.pitch / 2) + LEFT * self.h,
            UP * (self.pitch / 2 - df) + LEFT * self.h,
            UP * da,
            ORIGIN,
            DOWN * da,
            DOWN * (self.pitch / 2 - df) + LEFT * self.h,
            DOWN * (self.pitch / 2) + LEFT * self.h,
        ]

        self.set_points_as_corners(tooth_points)
        for k in range(self.z - 1):
            self.shift(UP * self.pitch)
            self.add_points_as_corners(tooth_points)

        self.shift(DOWN * self.pitch * (self.z - 1) / 2 + RIGHT * self.h_a * self.m)
        point2 = LEFT * self.h / 2 + self.points[-1, :]
        self.add_line_to(point2)
        self.add_line_to(self.points[0, :] + LEFT * self.h / 2)
        self.add_line_to(self.points[0, :])

    def get_center(self):
        """Return the geometric center of the rack."""
        return self.submobjects[0].points[0, :].copy()

    def get_angle_vector(self):
        """Return the internal reference vector used to track orientation."""
        return self.submobjects[0].points[1, :] - self.submobjects[0].points[0, :]

    def get_angle(self):
        """Return the current orientation angle of the rack in radians."""
        v = self.get_angle_vector()
        return np.arctan2(v[1], v[0])

    def rotate(
        self,
        angle: float,
        axis: np.ndarray = OUT,
        about_point: Optional[Sequence[float]] = None,
        **kwargs,
    ):
        """Rotate the rack around its centre by default.

        Parameters
        ----------
        angle : float
            Rotation angle in radians.
        axis : np.ndarray, optional
            Rotation axis (default ``OUT``).
        about_point : sequence of float or None, optional
            Centre point for the rotation.  If ``None`` the rack's own
            centre is used.
        """
        if about_point is None:
            ret = super().rotate(angle, axis, about_point=self.get_center(), **kwargs)
        else:
            ret = super().rotate(angle, axis, about_point=about_point, **kwargs)
        return ret