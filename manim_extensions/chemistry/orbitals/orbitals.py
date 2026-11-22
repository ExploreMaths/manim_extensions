# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Atomic orbital visualization for Manim chemistry.

This module provides classes for rendering atomic orbitals in 3D.

"""

from typing import Any, cast

from manim import BLUE, ORIGIN, PI, RED, TAU
from manim.mobject.opengl.opengl_surface import OpenGLSurface
import numpy as np
import scipy.special as spe
from manim.typing import Point3D, VectorND, MatrixMN

if hasattr(spe, "sph_harm_y"):
    # scipy >= 1.15: Y_l^m(theta_polar, phi_azimuthal)
    def _sph_harm(m: int, l: int, azimuthal: VectorND, polar: VectorND) -> np.ndarray:
        """Return the spherical harmonic with the new scipy argument order."""
        return cast(np.ndarray, spe.sph_harm_y(l, m, polar, azimuthal))

else:
    # legacy scipy: sph_harm(m, l, theta_azimuthal, phi_polar)
    def _sph_harm(m: int, l: int, azimuthal: VectorND, polar: VectorND) -> np.ndarray:
        """Return the spherical harmonic with the legacy scipy argument order."""
        return cast(np.ndarray, spe.sph_harm(m, l, azimuthal, polar))


class OrbitalBase(OpenGLSurface):
    """Base class for implementing atomic orbitals.
    Not meant to be used directly even when you can.

    Parameters
    ----------
    center
        Position of the orbital center.
    resolution
        Resolution ``(u, v)`` of the surface.
    u_range
        Range of the ``u`` parameter.
    v_range
        Range of the ``v`` parameter.
    n_value
        Principal quantum number.
    l_value
        Azimuthal quantum number.
    m_value
        Magnetic quantum number.
    size
        Scale factor applied to the orbital surface.
    **kwargs
        Additional keyword arguments forwarded to
        OpenGLSurface.

    Examples
    --------
    .. manim:: OrbitalBaseOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.orbitals.orbitals import OrbitalBase

       OrbitalBaseTarget = OrbitalBase

       class OrbitalBaseOverview(Scene):
           def construct(self):
               public = [n for n in dir(OrbitalBaseTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('OrbitalBase', font_size=36),
                   Text('module: manim_extensions.chemistry.orbitals.orbitals', font_size=18, color=GREY),
                   Text('Base class for implementing atomic orbitals. Not meant to be used directly even when you can', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.chemistry.orbitals.orbitals import OrbitalBase

        orbital = OrbitalBase(n_value=2, l_value=1, m_value=0, size=1.5)
    """

    def add_background_rectangle_to_family_members_with_points(
        self, **kwargs: Any
    ) -> "OrbitalBase":
        """No-op override to prevent background rectangle addition on orbital surfaces.

        Parameters
        ----------
        **kwargs
            Accepted for signature compatibility and ignored.

        Returns
        -------
            The resulting value.
        """
        return self

    def __init__(
        self,
        center: Point3D = ORIGIN,
        resolution: tuple[Any, ...] = (100, 50),
        u_range: tuple[Any, ...] = (0, PI),
        v_range: tuple[Any, ...] = (0, TAU),
        n_value: int = 1,
        l_value: int = 0,
        m_value: int = 0,
        size: int = 1,
        **kwargs: Any,
    ) -> None:
        self.n_value = n_value
        self.l_value = l_value
        self.m_value = m_value
        self.size = size

        super().__init__(
            self.uv_func,
            resolution=resolution,
            u_range=u_range,
            v_range=v_range,
            **kwargs,
        )

        self.shift(center)

    def psi_ang(
        self, phi: VectorND, theta: VectorND, l: int = 0, m: int = 0
    ) -> VectorND:
        r"""Compute the real part of the spherical harmonic :math:`Y_l^m` at angles :math:`\phi, \theta`.

        Parameters
        ----------
        phi
            Azimuthal angle.
        theta
            Polar angle.
        l
            Azimuthal (angular momentum) quantum number.
        m
            Magnetic quantum number.

        Returns
        -------
            The real part of the spherical harmonic :math:`Y_l^m` at the given angles.
        """
        sphHarm = _sph_harm(m, l, phi, theta)

        return sphHarm.real

    def calculate_coordinates(
        self, psi: VectorND, u: VectorND | None, v: VectorND
    ) -> MatrixMN:
        """Convert spherical psi value and angles u,v to scaled 3D Cartesian coordinates.

        Parameters
        ----------
        psi
            Value of the wave function at the given angles.
        u
            Polar angle.
        v
            Azimuthal angle.

        Returns
        -------
            The scaled 3D Cartesian coordinates for the given spherical angles.
        """
        u_arr = cast(VectorND, u)
        x = np.sin(u_arr) * np.cos(v) * abs(psi)
        y = np.sin(u_arr) * np.sin(v) * abs(psi)
        z = np.cos(u_arr) * abs(psi)

        return self.size * np.array([x, y, z])

    def uv_func(self, u: VectorND | None, v: VectorND) -> MatrixMN:
        """Base uv function: compute orbital surface coordinates from spherical angles u, v.

        Parameters
        ----------
        u
            Polar angle.
        v
            Azimuthal angle.

        Returns
        -------
            The orbital surface coordinates for the given spherical angles.
        """
        psi = self.psi_ang(v, cast(VectorND, u), l=self.l_value, m=self.m_value)

        return self.calculate_coordinates(psi, u, v)


class OrbitalPositive(OrbitalBase):
    """Calculates the positive values of the orbital.

    Examples
    --------
    .. manim:: OrbitalPositiveOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.orbitals.orbitals import OrbitalPositive

       OrbitalPositiveTarget = OrbitalPositive

       class OrbitalPositiveOverview(Scene):
           def construct(self):
               public = [n for n in dir(OrbitalPositiveTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('OrbitalPositive', font_size=36),
                   Text('module: manim_extensions.chemistry.orbitals.orbitals', font_size=18, color=GREY),
                   Text('Calculates the positive values of the orbital', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.chemistry.orbitals.orbitals import OrbitalPositive

        positive = OrbitalPositive(size=1.5)
    """

    def uv_func(self, u: VectorND | None, v: VectorND) -> MatrixMN:
        """Compute positive-lobe orbital coordinates, clamping negative psi values to zero.

        Parameters
        ----------
        u
            Polar angle.
        v
            Azimuthal angle.

        Returns
        -------
            The orbital surface coordinates for the given spherical angles.
        """
        psi = self.psi_ang(v, cast(VectorND, u), l=self.l_value, m=self.m_value)
        if psi < 0:
            psi = cast(VectorND, 0)

        return self.calculate_coordinates(psi, u, v)


class OrbitalNegative(OrbitalBase):
    """Calculates the negative values of the orbital.

    Examples
    --------
    .. manim:: OrbitalNegativeOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.orbitals.orbitals import OrbitalNegative

       OrbitalNegativeTarget = OrbitalNegative

       class OrbitalNegativeOverview(Scene):
           def construct(self):
               public = [n for n in dir(OrbitalNegativeTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('OrbitalNegative', font_size=36),
                   Text('module: manim_extensions.chemistry.orbitals.orbitals', font_size=18, color=GREY),
                   Text('Calculates the negative values of the orbital', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.chemistry.orbitals.orbitals import OrbitalNegative

        negative = OrbitalNegative(size=1.5)
    """

    def uv_func(self, u: VectorND | None, v: VectorND) -> MatrixMN:
        """Compute negative-lobe orbital coordinates, clamping positive psi values to zero.

        Parameters
        ----------
        u
            Polar angle.
        v
            Azimuthal angle.

        Returns
        -------
            The orbital surface coordinates for the given spherical angles.
        """
        psi = self.psi_ang(v, cast(VectorND, u), l=self.l_value, m=self.m_value)
        if psi > 0:
            psi = cast(VectorND, 0)

        return self.calculate_coordinates(psi, u, v)


class Orbital(OpenGLSurface):
    """Uses positive and negative orbitals to create
    an orbital. n value is still not implemented TODO

    .. important::

       OpenGLSurface requires
       the OpenGL renderer; render scenes containing orbitals with
       ``manim render --renderer=opengl``.

    Parameters
    ----------
    n
        Principal quantum number. If ``None``, it is set to ``l + 1``.

    l
        Azimuthal (angular momentum) quantum number.
    m
        Magnetic quantum number.
    size
        Scale of the orbital surface.
    **kwargs
        Additional keyword arguments passed to OpenGLSurface.

    Examples
    --------
    .. manim:: OrbitalOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.orbitals.orbitals import Orbital

       OrbitalTarget = Orbital

       class OrbitalOverview(Scene):
           def construct(self):
               public = [n for n in dir(OrbitalTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('Orbital', font_size=36),
                   Text('module: manim_extensions.chemistry.orbitals.orbitals', font_size=18, color=GREY),
                   Text('Uses positive and negative orbitals to create an orbital. n value is still not implemented TODO', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.chemistry.orbitals.orbitals import Orbital

        orbital = Orbital(n=2, l=1, m=0, size=2)
    """

    def __init__(
        self, n: int | None = None, l: int = 0, m: int = 0, size: int = 3, **kwargs: Any
    ) -> None:
        super().__init__(self.uv_func, **kwargs)
        if not n:
            self.n = l + 1
        else:
            self.n = n
        self.l = l
        self.m = m
        self.size = size
        pos = OrbitalPositive(
            n_value=self.n, l_value=self.l, m_value=self.m, size=self.size
        ).set_color(RED)
        neg = OrbitalNegative(
            n_value=self.n, l_value=self.l, m_value=self.m, size=self.size
        ).set_color(BLUE)
        self.add(pos, neg)
        self.needs_new_bounding_box = True

    def uv_func(self, u: VectorND | None, v: VectorND) -> MatrixMN:
        """Placeholder uv function returning origin; actual geometry is in child positive/negative orbitals.

        Parameters
        ----------
        u
            Polar angle.
        v
            Azimuthal angle.

        Returns
        -------
            The computed array.
        """
        return np.array([0, 0, 0])
