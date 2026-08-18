# SPDX-FileCopyrightText: 2024 Matheart
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Lenses for refracting Rays.
"""
from __future__ import annotations
from typing import Iterable, Tuple

from manim import *
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
import numpy as np
from shapely import geometry as gm


__all__ = ["Lens"]


def intersection(vmob1: VMobject, vmob2: VMobject) -> Iterable[Iterable[float]]:
    """Compute the intersection points of two VMobject curves.

    Parameters
    ----------
    vmob1 : VMobject
        First curve.
    vmob2 : VMobject
        Second curve.

    Returns
    -------
    Iterable[Iterable[float]]
        Array of 3-D intersection coordinates (possibly empty).
    """
    a = gm.LineString(vmob1.points)
    b = gm.LineString(vmob2.points)
    intersects: gm.GeometryCollection = a.intersection(b)
    try:  # for intersections > 1
        return np.array(
            [[[x, y, z] for x, y, z in m.coords][0] for m in intersects.geoms]
        )
    except:  # else
        return np.array([[x, y, z] for x, y, z in intersects.coords])


def snell(i_ang: float, n: float) -> float:
    """Apply Snell's law: compute the refracted angle from the incident angle.

    Parameters
    ----------
    i_ang : float
        Incident angle in radians.
    n : float
        Refractive index ratio ``n2 / n1``.

    Returns
    -------
    float
        Refracted angle in radians.
    """
    return np.arcsin(np.sin(i_ang) / n)


def antisnell(r_ang: float, n: float) -> float:
    """Inverse Snell's law: compute the incident angle from the refracted angle.

    Parameters
    ----------
    r_ang : float
        Refracted angle in radians.
    n : float
        Refractive index ratio ``n2 / n1``.

    Returns
    -------
    float
        Incident angle in radians.
    """
    return np.arcsin(np.sin(r_ang) * n)


class Lens(VMobject, metaclass=ConvertToOpenGL):
    """Thin lens with spherical surfaces for ray-tracing visualisation.

    The lens shape is constructed from the intersection or difference of two
    circles, depending on whether the focal length is positive (convex) or
    negative (concave).  The refractive index controls the curvature.

    .. warning::

        The current focal-length calculation does not precisely match the
        physical point of focus.  This is a known limitation that may be
        addressed in a future release.

    Parameters
    ----------
    f : float
        Focal length.  Positive values produce a convex lens, negative
        values produce a concave lens.
    d : float
        Lens thickness.
    n : float, optional
        Refractive index of the lens material.  Defaults to ``1.52``
        (glass).
    **kwargs
        Additional parameters forwarded to :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: LensExample
       :save_last_frame:

       from manim import *
       from manim_extensions.physics.optics.lenses import Lens

       class LensExample(Scene):
           def construct(self):
               lens = Lens(f=2, d=0.4, fill_opacity=0.5, color=BLUE)
               self.add(lens)
"""
    def __init__(self, f: float, d: float, n: float = 1.52, **kwargs) -> None:
        """Initialize Lens."""
        super().__init__(**kwargs)
        self.f = f
        f *= 50 / 7 * f if f > 0 else -50 / 7 * f  # this is odd, but it works
        if f > 0:
            r = ((n - 1) ** 2 * f * d / n) ** 0.5
        else:
            r = ((n - 1) ** 2 * -f * d / n) ** 0.5
        self.d = d
        self.n = n
        self.r = r
        if f > 0:
            self.set_points(
                Intersection(
                    a := Circle(r).shift(RIGHT * (r - d / 2)),
                    b := Circle(r).shift(LEFT * (r - d / 2)),
                )
                .insert_n_curves(50)
                .points
            )
        else:
            self.set_points(
                Difference(
                    Difference(
                        Square(2 * 0.7 * r),
                        a := Circle(r).shift(LEFT * (r + d / 2)),
                    ),
                    b := Circle(r).shift(RIGHT * (r + d / 2)),
                )
                .insert_n_curves(50)
                .points
            )
        self.add(VectorizedPoint(a.get_center()), VectorizedPoint(b.get_center()))

    @property
    def C(self) -> Tuple[Iterable[float]]:
        """Returns a tuple of two points corresponding to the centers of curvature."""
        i = 0
        i += 1 if config.renderer != "opengl" else 0
        return self[i].points[0], self[i + 1].points[0]  # why is this confusing