.. SPDX-FileCopyrightText: 2026 FTZ-OPUS
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Three-Dimensional Surface Scenes
================================

.. module:: manim_extensions.three_d

.. vendored-status:: FTZ-OPUS/manim-3d

**Original author:** `FTZ-OPUS <https://github.com/FTZ-OPUS>`_

**Source repository:** `GitHub <https://github.com/FTZ-OPUS/manim-3d>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-3d`` supplies ready-made three-dimensional surface scenes, including
Gaussian, saddle, paraboloid, ellipsoid, torus, and hyperboloid presets.

The code is bundled inside ``manim_extensions`` as the
:mod:`~manim_extensions.three_d` subpackage.

Features
--------

- surface configuration classes such as
  :class:`~manim_extensions.three_d.core.GaussianSurface` and
  :class:`~manim_extensions.three_d.core.SaddleSurface`.
- ready-to-render scene classes for each preset surface.
- :func:`~manim_extensions.three_d.core.plan_timeline` beat planning.
- camera, axes, contour, flip, and annotation choreography.

Usage
-----

Create a complete Gaussian-surface scene with the fast pace:

.. manim:: ThreeDDemo
   :ref_classes: GaussianSurfaceScene
   :save_last_frame:

   from manim import *
   from manim_extensions.three_d import gaussian_surface_scene

   class ThreeDDemo(gaussian_surface_scene(pace="fast")):
       def construct(self):
           super().construct()

Modules
-------

.. autosummary::
   :nosignatures:

   ~core

Type Aliases
------------

.. autoall:: manim_extensions.three_d
   :recursive:
   :types: typealias

Constants
---------

.. autoall:: manim_extensions.three_d
   :types: data

.. toctree::
   :hidden:
   :maxdepth: 1

   core
