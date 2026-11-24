.. SPDX-FileCopyrightText: 2024 sinianluoye
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

utils
=====

.. module:: manim_extensions.algorithm.utils

Usage
-----

Vector helpers and paragraph-index helpers used by the algorithm mobjects.

.. manim:: ParagraphIndexLabels
   :save_last_frame:
   :ref_classes: NumpyHelper index_paragraph_labels

   import numpy as np
   from manim import *
   from manim_extensions.algorithm.utils import NumpyHelper, index_paragraph_labels

   class ParagraphIndexLabels(Scene):
       def construct(self):
           paragraph = Paragraph("first line", "second line")
           labels = index_paragraph_labels(paragraph)
           unit = NumpyHelper.normalize_vector(np.array([3.0, 4.0]))
           arrow = Arrow(ORIGIN, RIGHT * 3 * unit[0] + UP * 3 * unit[1], buff=0)
           arrow.next_to(paragraph, LEFT, buff=0.8)
           self.add(VGroup(paragraph, labels, arrow).scale(0.8).move_to(ORIGIN))

Modules
-------

.. autosummary::
   :nosignatures:

   ~debug
   ~numpy_helper

.. toctree::
   :hidden:
   :maxdepth: 1

   debug
   numpy_helper
