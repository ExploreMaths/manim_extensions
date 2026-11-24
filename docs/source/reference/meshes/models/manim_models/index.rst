.. SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

manim_models
============

.. module:: manim_extensions.meshes.models.manim_models

Usage
-----

Wrap a data mesh in a Manim mobject for drawing.

.. code-block:: python

   from manim import *
   from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh
   from manim_extensions.meshes.templates import create_pyramid

   mesh = ManimMesh(create_pyramid(triangles_only=True))

Modules
-------

.. autosummary::
   :nosignatures:

   ~basic_mesh
   ~opengl_mesh
   ~triangle_mesh

.. toctree::
   :hidden:
   :maxdepth: 1

   basic_mesh
   opengl_mesh
   triangle_mesh
