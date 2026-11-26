.. SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

delaunay
========

.. automodule:: manim_extensions.meshes.delaunay

Usage
-----

Delaunay and Voronoi tools operate on point sets; the criterion helpers can be used independently of the mesh renderers.

.. code-block:: python

   from manim_extensions.meshes.delaunay.voronoi import VoronoiDelaunay
   from manim_extensions.meshes.delaunay.delaunay_criterion import (
       get_triangle_circum_circle_params,
   )

Modules
-------

.. autosummary::
   :nosignatures:

   ~delaunay_criterion
   ~divide_and_conquer
   ~voronoi

.. toctree::
   :hidden:
   :maxdepth: 1

   delaunay_criterion
   divide_and_conquer
   voronoi
