Meshes
======

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

- ``Mesh`` data model for mesh topology and operations.
- ``ManimMesh`` / ``Manim2DMesh`` for mesh rendering.
- ``TriangleManim2DMesh`` for triangle-based geometric structures.
- ``FastManimMesh`` for faster scene rendering when available.
- Delaunay and Voronoi-related tooling in the bundled mesh utilities.

Quick start
-----------

Import the package directly from the vendored namespace:

.. code-block:: python

   from manim import *
   from manim_extensions.meshes.models.data_models.mesh import Mesh
   from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

   class MeshExample(Scene):
       def construct(self):
           mesh = Mesh(
               vertices=[[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
               faces=[[0, 1, 2], [1, 3, 2]],
           )
           self.add(ManimMesh(mesh))
           self.wait(0.5)

Building a mesh structure
^^^^^^^^^^^^^^^^^^^^^^^^^

The low-level :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh` is a
pure data model: pass an array-like list of *vertices* and a list of *faces*
(referencing vertex indices), and it validates the structure and lets you inspect
or combine meshes before rendering.

.. note::

   The manim-side renderers (``ManimMesh`` and the 2D / triangle / OpenGL
   variants) require the optional ``colour`` and ``moderngl`` dependencies.  When
   those are not installed, the :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh`
   data model is still fully importable and usable for computing mesh structures.

This package is most appropriate for:

* geometry lessons,
* mesh and triangulation demonstrations,
* topology and connected-structure visualisations.

See the `original project page <https://github.com/bmmtstb/manim-meshes>`_
for details on the mesh model and more advanced examples.

.. toctree::
   :hidden:

   api