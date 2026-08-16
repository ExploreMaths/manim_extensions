.. SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Data model
==========

Mesh
----

.. autoclass:: manim_extensions.meshes.models.data_models.mesh.Mesh
   :members:
   :undoc-members:
   :show-inheritance:

.. note::

   The manim-side renderers (:class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh`, :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.Manim2DMesh`, :class:`~manim_extensions.meshes.models.manim_models.triangle_mesh.TriangleManim2DMesh`
   and the OpenGL :class:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh`) as well as the Delaunay helpers depend on the
   optional ``colour`` / ``moderngl`` packages and are therefore not importable in
   this environment.