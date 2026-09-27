# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
"""Utility functions for computing moments of inertia.

This module provides convenience functions for computing moments of inertia
of various shapes, used to configure the physical properties of Pymunk
rigid bodies.
"""

from ...utils.deps import require


def get_moment_for_box(mass: float, width: float, height: float) -> float:
    """Compute the moment of inertia of a rectangular shape.

    Calculates the moment of inertia about the center of a rectangle given
    its mass, width, and height.

    Parameters
    ----------
    mass : float
        Mass of the rectangle.
    width : float
        Width of the rectangle.
    height : float
        Height of the rectangle.

    Returns
    -------
    float
        Moment of inertia.
    """
    moment_for_box = require("physics", "pymunk").moment_for_box
    return moment_for_box(mass=mass, size=(width, height))


def get_moment_for_circle(
    mass: float,
    inner_radius: float,
    outer_radius: float,
    x_offset: float = 0,
    y_offset: float = 0,
) -> float:
    """Compute the moment of inertia of a ring or solid circle.

    Calculates the moment of inertia of a ring given its mass, inner and
    outer radii, and offset. When ``inner_radius`` is 0, computes the moment
    of inertia of a solid circle.

    Parameters
    ----------
    mass : float
        Mass of the ring.
    inner_radius : float
        Inner radius.
    outer_radius : float
        Outer radius.
    x_offset : float, optional
        Center X offset, defaults to 0.
    y_offset : float, optional
        Center Y offset, defaults to 0.

    Returns
    -------
    float
        Moment of inertia.
    """
    moment_for_circle = require("physics", "pymunk").moment_for_circle
    return moment_for_circle(
        mass=mass,
        inner_radius=inner_radius,
        outer_radius=outer_radius,
        offset=(x_offset, y_offset),
    )


def get_moment_for_poly(
    mass: float,
    vertices: list[tuple[float, float]],
    x_offset: float = 0,
    y_offset: float = 0,
    stroke_width: float = 0,
) -> float:
    """Compute the moment of inertia of a polygon.

    Calculates the moment of inertia given the polygon's mass, vertex
    coordinates, and offset.

    Parameters
    ----------
    mass : float
        Mass of the polygon.
    vertices : list[tuple[float, float]]
        List of polygon vertices, each represented as :math:`(x, y)`.
    x_offset : float, optional
        Center X offset, defaults to 0.
    y_offset : float, optional
        Center Y offset, defaults to 0.
    stroke_width : float, optional
        Shape radius (used as line width), defaults to 0.

    Returns
    -------
    float
        Moment of inertia.
    """
    moment_for_poly = require("physics", "pymunk").moment_for_poly
    return moment_for_poly(
        mass=mass, vertices=vertices, offset=(x_offset, y_offset), radius=stroke_width
    )


def get_moment_for_line(
    mass: float,
    start: tuple[float, float],
    end: tuple[float, float],
    stroke_width: float,
) -> float:
    """Compute the moment of inertia of a line segment.

    Calculates the moment of inertia given the segment's mass, endpoints,
    and width.

    Parameters
    ----------
    mass : float
        Mass of the line segment.
    start : tuple[float, float]
        Start point of the segment: :math:`(x, y)`.
    end : tuple[float, float]
        End point of the segment: :math:`(x, y)`.
    stroke_width : float
        Width (radius) of the segment.

    Returns
    -------
    float
        Moment of inertia.
    """
    moment_for_segment = require("physics", "pymunk").moment_for_segment
    return moment_for_segment(mass=mass, a=start, b=end, radius=stroke_width)
