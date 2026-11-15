.. SPDX-FileCopyrightText: 2020 GarryBGoode
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

CAD Drawing Utilities
=====================

.. module:: manim_extensions.cad_drawing_utils

.. vendored-status:: GarryBGoode/Manim_CAD_Drawing_utils

**Original author:** `GarryBGoode <https://github.com/GarryBGoode>`_

**Source repository:** `GitHub <https://github.com/GarryBGoode/Manim_CAD_Drawing_utils>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-CAD_Drawing_utils`` adds CAD-style dimension lines, hatching, path
mapping, rounded corners, and Bezier helpers to Manim.

The code is bundled inside ``manim_extensions`` as the
:mod:`~manim_extensions.cad_drawing_utils` subpackage.

Features
--------

- :class:`~manim_extensions.cad_drawing_utils.dimensions.Linear_Dimension` and
  angular dimension mobjects.
- :class:`~manim_extensions.cad_drawing_utils.hatch.Hatch_lines` hatching.
- :class:`~manim_extensions.cad_drawing_utils.path_mapper.Path_mapper` and dashed-path mobjects.
- round and chamfer corner helpers for Bezier paths.
- :class:`~manim_extensions.cad_drawing_utils.utils.Bezier_Handlebars` for editing control points.

Usage
-----

Add a linear dimension to a line:

.. manim:: LinearDimensionDemo
   :ref_classes: Linear_Dimension

   from manim import *
   from manim_extensions.cad_drawing_utils import Linear_Dimension

   class LinearDimensionDemo(Scene):
       def construct(self):
           line = Line(LEFT * 3, RIGHT * 3)
           self.add(line)
           dimension = Linear_Dimension(LEFT * 3, RIGHT * 3, text="6")
           self.play(Create(dimension))

Modules
----------

.. autosummary::
   :nosignatures:

   ~dimensions
   ~hatch
   ~path_mapper
   ~round_corners
   ~utils

.. toctree::
   :hidden:
   :maxdepth: 1

   dimensions
   hatch
   path_mapper
   round_corners
   utils
