.. SPDX-FileCopyrightText: 2026 manim-straightedge-compass contributors
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Straightedge and Compass
========================

.. module:: manim_extensions.straightedge_compass

.. vendored-status:: manim-straightedge-compass/pypi
   :name: manim-straightedge-compass
   :ref: 0.1.1

**Original author:** `manim-straightedge-compass contributors <https://pypi.org/project/manim-straightedge-compass/>`_

**Source repository:** `PyPI <https://pypi.org/project/manim-straightedge-compass/>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-straightedge-compass`` provides Euclid-style straightedge-and-compass
construction mobjects and pure geometry helpers for Manim scenes.

The code is bundled inside ``manim_extensions`` as the
:mod:`~manim_extensions.straightedge_compass` subpackage.

Features
--------

- :class:`~manim_extensions.straightedge_compass.compass.Compass` and
  :class:`~manim_extensions.straightedge_compass.compass.CompassDrawArc` drawing mobjects.
- :class:`~manim_extensions.straightedge_compass.straightedge.Straightedge` and
  :class:`~manim_extensions.straightedge_compass.straightedge.RulerDraw` tools.
- :class:`~manim_extensions.straightedge_compass.marks.MarkedPoint` construction labels.
- pure helpers for distances, midpoints, intersections, and point selection.
- :class:`~manim_extensions.straightedge_compass.scene.EuclidScene` for construction scenes.

Usage
-----

Draw a segment and circle through two marked points:

.. manim:: StraightedgeCompassDemo
   :ref_classes: EuclidScene MarkedPoint

   from manim_extensions.straightedge_compass import EuclidScene, P

   class StraightedgeCompassDemo(EuclidScene):
       def construct(self):
           a = P(-1.5, 0)
           b = P(1.5, 0)
           self.mark_point(a, "A")
           self.mark_point(b, "B")
           self.draw_segment(a, b, keep_ruler=True)
           self.draw_arc(a, 3, keep_compass=True)
           self.flash_points(a, b)

Modules
-------

.. autosummary::
   :nosignatures:

   ~compass
   ~geometry
   ~marks
   ~scene
   ~straightedge

Constants
---------

.. autoall:: manim_extensions.straightedge_compass
   :types: data

.. toctree::
   :hidden:
   :maxdepth: 1

   compass
   geometry
   marks
   scene
   straightedge
