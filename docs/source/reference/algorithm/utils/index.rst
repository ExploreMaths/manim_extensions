.. SPDX-FileCopyrightText: 2024 sinianluoye
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

utils
=====

.. module:: manim_extensions.algorithm.utils

Usage
-----

Vector helpers and paragraph-index helpers used by the algorithm mobjects.

.. code-block:: python

   import numpy as np
   from manim import Paragraph
   from manim_extensions.algorithm.utils import NumpyHelper, index_paragraph_labels

   unit = NumpyHelper.normalize_vector(np.array([3.0, 4.0]))
   labels = index_paragraph_labels(Paragraph("first line", "second line"))

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
