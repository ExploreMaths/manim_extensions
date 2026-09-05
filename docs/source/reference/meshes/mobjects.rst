.. SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Manim mobjects
==============

This page documents the Manim-side mesh renderers that turn a
:class:`~manim_extensions.meshes.models.data_models.mesh.Mesh` data model into
on-screen Manim mobjects.

.. note::

   The manim-side renderers depend on the optional ``colour`` / ``moderngl``
   packages and are therefore not importable in every environment.

ManimMesh
---------

.. autoclass:: manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh
Manim2DMesh
-----------

.. autoclass:: manim_extensions.meshes.models.manim_models.basic_mesh.Manim2DMesh
TriangleManim2DMesh
-------------------

.. autoclass:: manim_extensions.meshes.models.manim_models.triangle_mesh.TriangleManim2DMesh
FastManimMesh
-------------

.. autoclass:: manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh
