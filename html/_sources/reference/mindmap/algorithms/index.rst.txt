.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

algorithms
==========

.. module:: manim_extensions.mindmap.algorithms

Usage
-----

The layout algorithms consume mind-map nodes and produce positions; most scenes use :class:`~manim_extensions.mindmap.mindmap.MindMap`, which selects a layout for you.

.. code-block:: python

   from manim_extensions.mindmap.algorithms import LayoutFactory
   from manim_extensions.mindmap.algorithms.layout import Layout

Modules
-------

.. autosummary::
   :nosignatures:

   ~alg_catalog
   ~alg_standard
   ~alg_tidy_tree
   ~alg_time_line
   ~layout
   ~layout_config
   ~layout_factory

.. toctree::
   :hidden:
   :maxdepth: 1

   alg_catalog
   alg_standard
   alg_tidy_tree
   alg_time_line
   layout
   layout_config
   layout_factory
