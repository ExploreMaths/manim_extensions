.. SPDX-FileCopyrightText: 2022 Hammad Nasir
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Data structures
===============

.. vendored-status:: drageelr/manim-data-structures

**Original author:** `Hammad Nasir <https://github.com/drageelr>`_

**Source repository:** `GitHub <https://github.com/drageelr/manim-data-structures>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-data-structures`` is a Manim toolkit for visualising common data
structures such as arrays, variables, and indices in algorithm explanations.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.data_structures`` subpackage.

Features
--------

- :class:`~manim_extensions.data_structures.m_array.MArray` – array-style container for indexed values.
- :class:`~manim_extensions.data_structures.m_variable.MVariable` – variable display for value updates.
- :class:`~manim_extensions.data_structures.m_array.MArrayElement` / :class:`~manim_extensions.data_structures.m_array.MArrayPointer` – element and pointer visual helpers.
- :class:`~manim_extensions.data_structures.m_array.MArraySlidingWindow` – windowed array layout for algorithms.
- directional helpers for array traversal and highlighting.

.. toctree::
   :maxdepth: 1

   classes
   constants
   enums
