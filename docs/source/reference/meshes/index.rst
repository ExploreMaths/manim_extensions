.. SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Meshes
======

.. vendored-status:: bmmtstb/manim-meshes

**Original author:** `Brizar <https://github.com/bmmtstb>`_ and `99Vicky <https://github.com/99Vicky>`_

**Source repository:** `GitHub <https://github.com/bmmtstb/manim-meshes>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-meshes`` is a geometry and mesh toolkit for Manim. It focuses on
rendering polygonal and triangular structures, especially for educational
visualisations of geometry, triangulation, and topology.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.meshes`` subpackage.

Features
--------

- :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh` data model for mesh topology and operations.
- :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh` / :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.Manim2DMesh` for mesh rendering.
- :class:`~manim_extensions.meshes.models.manim_models.triangle_mesh.TriangleManim2DMesh` for triangle-based geometric structures.
- :class:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh` for faster scene rendering when available.
- Delaunay and Voronoi-related tooling in the bundled mesh utilities.

Building a mesh structure
^^^^^^^^^^^^^^^^^^^^^^^^^

The low-level :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh` is a
pure data model: pass an array-like list of *vertices* and a list of *faces*
(referencing vertex indices), and it validates the structure and lets you inspect
or combine meshes before rendering.

.. note::

   The manim-side renderers (:class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh` and the 2D / triangle / OpenGL
   variants) require the optional ``colour`` and ``moderngl`` dependencies.  When
   those are not installed, the :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh`
   data model is still fully importable and usable for computing mesh structures.

Rendering backends
^^^^^^^^^^^^^^^^^^

All renderers wrap a :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh`
node-face data model (meshes can also be imported from the ``trimesh``
library). The Cairo renderer will not work for these scenes — run them with
the OpenGL renderer (``--renderer=opengl``):

.. code-block:: python

   from manim import *

   from manim_extensions.meshes.models.data_models.mesh import Mesh
   from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

   class ConeScene(Scene):
       def construct(self):
           # build the node-face data model, then wrap it in a renderer
           mesh = Mesh(vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0]],
                       faces=[[0, 1, 2]])
           renderable = ManimMesh(mesh)
           self.add(renderable)

You can shift (translate) and scale the whole mesh or single vertices, and
most manim coloring functions are available on individual mesh objects.
Note that ``Rotate`` does not update the wrapped mesh, because it only updates
a copy of the rotation.

Renderer classes:

- :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh` /
  :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.Manim2DMesh` –
  basic renderers for smaller meshes (under roughly 1 000 nodes). They suit 2D
  and small 3D explanatory videos rather than high-resolution rendering;
  shift / rotate / scale are available, but not every ``Mobject`` method is
  re-implemented.
- :class:`~manim_extensions.meshes.models.manim_models.triangle_mesh.TriangleManim2DMesh` –
  2-D triangle meshes, designed for educational use, with Delaunay-oriented
  operations.
- :class:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh` –
  a faster renderer based on a custom shader that can render large meshes;
  at the moment it is rendering-only.

The bundled ``delaunay`` package provides Delaunay-triangulation helpers:
Voronoi diagrams, checking the Delaunay criterion, and a divide-and-conquer
triangulation algorithm.

Default rendering parameters (which parts are displayed, edge / face /
vertex colors and sizes) live in ``params.py``; pass the kwargs you want to
override when constructing a mesh. Upstream example scenes (``ConeScene``,
``PyramidScene``, ``SnapToGridScene``) live in the upstream ``tests/``
directory.

.. note::

   The package is not fully optimized and is intended for smaller meshes;
   the OpenGL renderer integration is still rough.

This package is most appropriate for:

* geometry lessons,
* mesh and triangulation demonstrations,
* topology and connected-structure visualisations.

See the `original project page <https://github.com/bmmtstb/manim-meshes>`_
for details on the mesh model and more advanced examples.

.. toctree::
   :hidden:
   :maxdepth: 1

   data_model
   mobjects
   helpers
   classes
   functions
   constants
   exceptions
