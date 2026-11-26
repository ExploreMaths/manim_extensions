.. SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

data_models
===========

.. automodule:: manim_extensions.meshes.models.data_models

Usage
-----

Create a mesh from vertices and face index lists, then query its edges and parts.

.. code-block:: python

   from manim_extensions.meshes.models.data_models.mesh import Mesh

   vertices = [[0, 0, 0], [2, 0, 0], [1, 1.5, 0]]
   faces = [[0, 1, 2]]
   mesh = Mesh(vertices, faces)

Modules
-------

.. autosummary::
   :nosignatures:

   ~mesh

.. toctree::
   :hidden:
   :maxdepth: 1

   mesh
