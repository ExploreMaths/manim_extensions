# SPDX-FileCopyrightText: 2024 Matheart
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Rays of light. Refracted by Lenses."""

from __future__ import annotations

from manim import *
from typing import Iterable
import numpy as np

from .lenses import Lens, antisnell, intersection, snell

__all__ = [
    "Ray",
]


class Ray(Line):
    """A light ray that can be refracted through lenses.

    A :class:`~manim_extensions.physics.optics.rays.Ray` extends :class:`~manim.mobject.geometry.line.Line` with
    refraction logic based on Snell's law.  When a list of :class:`~manim_extensions.physics.optics.lenses.Lens`
    objects is passed to the constructor or :meth:`~manim_extensions.physics.optics.rays.Ray.propagate`, the ray
    automatically bends as it passes through each lens surface.

    Parameters
    ----------
    start : array-like
        Starting point of the ray.
    direction : array-like
        Direction vector of the ray.
    init_length : float, optional
        Initial length of the ray.  Defaults to ``5``.
    propagate : iterable of Lens, optional
        Lenses to propagate the ray through immediately upon construction.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.geometry.line.Line`.

    Examples
    --------
    .. manim:: RayExample
       :save_last_frame:

       from manim import *
       from manim_extensions.physics.optics.lenses import Lens
       from manim_extensions.physics.optics.rays import Ray

       class RayExample(Scene):
           def construct(self):
               lens_style = {"fill_opacity": 0.5, "color": BLUE}
               a = Lens(-5, 1, **lens_style).shift(LEFT)
               a2 = Lens(5, 1, **lens_style).shift(RIGHT)
               rays = [
                   Ray(LEFT * 5 + UP * i, RIGHT, 8, [a, a2], color=RED)
                   for i in np.linspace(-2, 2, 10)
               ]
               self.add(a, a2, *rays)
    """

    def __init__(
        self,
        start: Iterable[float],
        direction: Iterable[float],
        init_length: float = 5,
        propagate: Iterable[Lens] | None = None,
        **kwargs,
    ) -> None:
        """Initialize Ray."""
        self.init_length = init_length
        self.propagated = False
        super().__init__(start, start + direction * init_length, **kwargs)
        if propagate:
            self.propagate(*propagate)

    def propagate(self, *lenses: Lens) -> None:
        """Let the ray propagate through the list
        of lenses passed.

        Parameters
        ----------
        lenses
            All the lenses for the ray to propagate through
        """
        sorted_lens = self._sort_lens(lenses)
        for lens in sorted_lens:
            intersects = intersection(lens, self)
            if len(intersects) == 0:
                continue
            intersects = self._sort_intersections(intersects)
            if not self.propagated:
                self.put_start_and_end_on(
                    self.start,
                    intersects[1],
                )
            else:
                nppcc = (
                    self.n_points_per_cubic_curve
                    if config.renderer != "opengl"
                    else self.n_points_per_curve
                )
                self.points = self.points[:-nppcc]
                self.add_line_to(intersects[1])
            self.end = intersects[1]
            i_ang = angle_of_vector(self.end - lens.C[0])
            i_ang -= angle_of_vector(self.start - self.end)
            r_ang = snell(i_ang, lens.n)
            r_ang *= -1 if lens.f > 0 else 1
            ref_ray = rotate_vector(lens.C[0] - self.end, r_ang)
            intersects = intersection(
                lens,
                Line(
                    self.end - ref_ray * self.init_length,
                    self.end + ref_ray * self.init_length,
                ),
            )
            intersects = self._sort_intersections(intersects)
            self.add_line_to(intersects[1])
            self.start = self.end
            self.end = intersects[1]
            i_ang = angle_of_vector(self.end - lens.C[1])
            i_ang -= angle_of_vector(self.start - self.end)
            if np.abs(np.sin(i_ang)) < 1 / lens.n:
                r_ang = antisnell(i_ang, lens.n)
                r_ang *= -1 if lens.f < 0 else 1
                ref_ray = rotate_vector(lens.C[1] - self.end, r_ang)
                ref_ray *= -1 if lens.f > 0 else 1
                self.add_line_to(self.end + ref_ray * self.init_length)
                self.start = self.end
                self.end = self.get_end()
            self.propagated = True

    def _sort_lens(self, lenses: Iterable[Lens]) -> Iterable[Lens]:
        """Sort lenses by distance from the ray's start to the intersection point.

        Parameters
        ----------
        lenses : iterable of Lens
            Lenses to sort.

        Returns
        -------
        iterable of Lens
            Lenses ordered by increasing distance from the ray start.
        """
        dists = []
        for lens in lenses:
            try:
                dists += [
                    [np.linalg.norm(intersection(self, lens)[0] - self.start), lens]
                ]
            except:
                dists += [[np.inf, lens]]
        dists.sort(key=lambda x: x[0])
        return np.array(dists, dtype=object)[:, 1]

    def _sort_intersections(
        self, intersections: Iterable[Iterable[float]]
    ) -> Iterable[Iterable[float]]:
        """Sort intersection points by distance from the ray's current end point.

        Parameters
        ----------
        intersections : iterable of iterable of float
            Intersection coordinates to sort.

        Returns
        -------
        iterable of iterable of float
            Intersections ordered by increasing distance from the ray end.
        """
        result = []
        for inters in intersections:
            result.append([np.linalg.norm(inters - self.end), inters])
        result.sort(key=lambda x: x[0])
        return np.array(result, dtype=object)[:, 1]
