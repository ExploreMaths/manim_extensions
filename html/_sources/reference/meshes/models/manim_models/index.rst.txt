.. SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

manim_models
============

.. automodule:: manim_extensions.meshes.models.manim_models

Usage
-----

Wrap a data mesh in a Manim mobject for drawing.

.. manim:: PyramidMesh
   :save_last_frame:
   :ref_classes: ManimMesh

   from manim import *
   from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh
   from manim_extensions.meshes.templates import create_pyramid

   class PyramidMesh(Scene):
       def construct(self):
           mesh = ManimMesh(create_pyramid(triangles_only=True))
           mesh.scale_to_fit_height(6)
           self.add(mesh)

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
