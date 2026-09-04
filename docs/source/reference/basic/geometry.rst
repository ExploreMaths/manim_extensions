.. SPDX-FileCopyrightText: 2020 manim-kindergarten
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Geometry
========

.. module:: manim_extensions.geometry

This module contains geometric calculation functions that operate directly on
Manim mobjects without creating any on-screen mobjects themselves.
:func:`~manim_extensions.geometry.VMobjectInt` works with *any* two
:class:`~manim.mobject.types.vectorized_mobject.VMobject` instances — circles,
lines, arcs, polygons, parametric curves, text, groups, and so on — by
intersecting their cubic Bézier outlines, so it needs no special cases for
particular mobject types.  They are useful for analytic geometry tasks inside
a :class:`~manim.scene.scene.Scene`.

VMobjectInt
-----------

.. autofunction:: manim_extensions.geometry.VMobjectInt

TangentPoint
------------

.. autofunction:: manim_extensions.geometry.TangentPoint
