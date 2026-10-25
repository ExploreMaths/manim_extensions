# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Atomic orbital visualization for Manim chemistry.

This module provides classes for rendering atomic orbitals in 3D.

"""

from manim import BLUE, ORIGIN, PI, RED, TAU
from manim.mobject.opengl.opengl_surface import OpenGLSurface
import numpy as np
import scipy.special as spe

from typing import Optional
if hasattr(spe, "sph_harm_y"):
    # scipy >= 1.15: Y_l^m(theta_polar, phi_azimuthal)
    def _sph_harm(m: int, l: int, azimuthal: np.ndarray, polar: np.ndarray):
        return spe.sph_harm_y(l, m, polar, azimuthal)

else:
    # legacy scipy: sph_harm(m, l, theta_azimuthal, phi_polar)
    def _sph_harm(m: int, l: int, azimuthal: np.ndarray, polar: np.ndarray):
        return spe.sph_harm(m, l, azimuthal, polar)




class OrbitalBase(OpenGLSurface):
    """
    Base class for implementing atomic orbitals.
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
        :class:`~manim.mobject.three_d.three_dimensional_space_opengl.OpenGLSurface`.
    """

    def add_background_rectangle_to_family_members_with_points(self):
        """No-op override to prevent background rectangle addition on orbital surfaces."""
        pass

    def __init__(
        self,
        center: np.ndarray = ORIGIN,
        resolution: tuple = (100, 50),
        u_range: tuple = (0, PI),
        v_range: tuple = (0, TAU),
        n_value: int = 1,
        l_value: int = 0,
        m_value: int = 0,
        size: int = 1,
        **kwargs,
    ):
        """Initialize the orbital base with quantum numbers, size and surface resolution."""
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

    def psi_ang(self, phi: np.ndarray, theta: np.ndarray, l: int = 0, m: int = 0) -> np.ndarray:
        """Compute the real part of the spherical harmonic :math:`Y_l^m` at angles :math:`\\phi, \\theta`.

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
        Any
            The computed result.
"""
        sphHarm = _sph_harm(m, l, phi, theta)

        return sphHarm.real

    def calculate_coordinates(self, psi: np.ndarray, u: Optional[np.ndarray], v: np.ndarray) -> np.ndarray:
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
        Any
            The computed result.
"""
        x = np.sin(u) * np.cos(v) * abs(psi)
        y = np.sin(u) * np.sin(v) * abs(psi)
        z = np.cos(u) * abs(psi)

        return self.size * np.array([x, y, z])

    def uv_func(self, u: Optional[np.ndarray], v: np.ndarray) -> np.ndarray:
        """Base uv function: compute orbital surface coordinates from spherical angles u, v.

        Parameters
        ----------
        u
            Polar angle. 
        v
            Azimuthal angle.

        Returns
        -------
        Any
            The computed result.
"""
        psi = self.psi_ang(v, u, l=self.l_value, m=self.m_value)

        return self.calculate_coordinates(psi, u, v)


class OrbitalPositive(OrbitalBase):
    """
    Calculates the positive values of the orbital.
    """

    def uv_func(self, u: Optional[np.ndarray], v: np.ndarray) -> np.ndarray:
        """Compute positive-lobe orbital coordinates, clamping negative psi values to zero.

        Parameters
        ----------
        u
            Polar angle. 
        v
            Azimuthal angle.

        Returns
        -------
        Any
            The computed result.
"""
        psi = self.psi_ang(v, u, l=self.l_value, m=self.m_value)
        if psi < 0:
            psi = 0

        return self.calculate_coordinates(psi, u, v)


class OrbitalNegative(OrbitalBase):
    """
    Calculates the negative values of the orbital.
    """

    def uv_func(self, u: Optional[np.ndarray], v: np.ndarray) -> np.ndarray:
        """Compute negative-lobe orbital coordinates, clamping positive psi values to zero.

        Parameters
        ----------
        u
            Polar angle. 
        v
            Azimuthal angle.

        Returns
        -------
        Any
            The computed result.
"""
        psi = self.psi_ang(v, u, l=self.l_value, m=self.m_value)
        if psi > 0:
            psi = 0

        return self.calculate_coordinates(psi, u, v)


class Orbital(OpenGLSurface):
    """
    Uses positive and negative orbitals to create
    an orbital. n value is still not implemented TODO

    .. important::

       :class:`~manim.mobject.opengl.opengl_surface.OpenGLSurface` requires
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
        Additional keyword arguments passed to :class:`~manim.mobject.opengl.opengl_surface.OpenGLSurface`.
    """

    def __init__(self, n: Optional[int]=None, l: int = 0, m: int = 0, size: int = 3, **kwargs):
        """Initialize a full atomic orbital with red positive and blue negative lobes."""
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

    def uv_func(self, u: Optional[np.ndarray], v: np.ndarray) -> np.ndarray:
        """Placeholder uv function returning origin; actual geometry is in child positive/negative orbitals.

        Parameters
        ----------
        u
            Polar angle. 
        v
            Azimuthal angle.

        Returns
        -------
        np.ndarray
            The computed array.
"""
        return np.array([0, 0, 0])