"""Magnetostatics module"""

from __future__ import annotations
import itertools as it
from typing import Iterable, Tuple

from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
from manim.mobject.types.vectorized_mobject import VMobject
from manim.mobject.vector_field import ArrowVectorField
import numpy as np


__all__ = ["Wire", "MagneticField"]


class Wire(VMobject, metaclass=ConvertToOpenGL):
    """An abstract class denoting a current carrying wire to produce a
    :class:`~manim_extensions.physics.electromagnetism.magnetostatics.MagneticField`.

    Parameters
    ----------
    stroke
        The original wire :class:`~manim.mobject.types.vectorized_mobject.VMobject`. The resulting wire takes its form.
    current
        The magnitude of current flowing in the wire.
    samples
        The number of segments of the wire used to create the
        :class:`~manim_extensions.physics.electromagnetism.magnetostatics.MagneticField`.
    kwargs
        Additional parameters passed to :class:`~manim.mobject.types.vectorized_mobject.VMobject`.


    .. note::

        See :class:`~manim_extensions.physics.electromagnetism.magnetostatics.MagneticField` for examples.

    Examples
    --------
    .. manim:: WireExample
       :save_last_frame:

       from manim import *
       from manim_extensions.physics.electromagnetism.magnetostatics import Wire

       class WireExample(Scene):
           def construct(self):
               wire = Wire(Circle(2).rotate(PI / 2, UP))
               self.add(wire)
"""

    def __init__(
        self,
        stroke: VMobject,
        current: float = 1,
        samples: int = 16,
        **kwargs,
    ):
        """Initialize the Wire instance."""
        self.current = current
        self.samples = samples

        super().__init__(**kwargs)
        self.set_points(stroke.points)


class MagneticField(ArrowVectorField):
    """A magnetic field.

    Parameters
    ----------
    wires
        All wires contributing to the total field.
    kwargs
        Additional parameters to be passed to :class:`~manim.mobject.vector_field.ArrowVectorField`.

    Example
    -------
    .. manim:: MagneticFieldExample
       :save_last_frame:

       from manim_extensions.physics import *

       class MagneticFieldExample(ThreeDScene):
           def construct(self):
               wire = Wire(Circle(2).rotate(PI / 2, UP))
               mag_field = MagneticField(
                   wire,
                   x_range=[-4, 4],
                   y_range=[-4, 4],
               )
               self.set_camera_orientation(PI / 3, PI / 4)
               self.add(wire, mag_field)

    """

    def __init__(self, *wires: Wire, **kwargs):
        """Initialize the MagneticField instance."""
        dls = []
        currents = []
        for wire in wires:
            points = [
                wire.point_from_proportion(i)
                for i in np.linspace(0, 1, wire.samples + 1)
            ]
            dls.append(list(zip(points, points[1:])))
            currents.append(wire.current)
        super().__init__(
            lambda p: MagneticField._field_func(p, dls, currents), **kwargs
        )

    @staticmethod
    def _field_func(
        p: np.ndarray,
        dls: Iterable[Tuple[np.ndarray, np.ndarray]],
        currents: Iterable[float],
    ):
        """Compute the magnetic field vector at a point using the Biot-Savart law.

        Parameters
        ----------
        p : numpy.ndarray
            Field point at which the magnetic field is evaluated.
        dls : iterable of tuple
            Line segments (pairs of points) representing current-carrying
            wire segments.
        currents : iterable of float
            Current magnitudes (in Amperes) flowing through each wire.

        Returns
        -------
        numpy.ndarray
            The magnetic field vector at point *p*.
        """
        B_field = np.zeros(3)
        for dl in dls:
            for (r0, r1), I in it.product(dl, currents):
                dr = r1 - r0
                r = p - r0
                dist = np.linalg.norm(r)
                if dist < 0.1:
                    return np.zeros(3)
                B_field += np.cross(dr, r) * I / dist**4
        return B_field