Data model
==========

Mesh
----

.. autoclass:: manim_extensions.meshes.models.data_models.mesh.Mesh
   :members:
   :undoc-members:
   :show-inheritance:

.. note::

   The manim-side renderers (``ManimMesh``, ``Manim2DMesh``, ``TriangleManim2DMesh``
   and the OpenGL ``FastManimMesh``) as well as the Delaunay helpers depend on the
   optional ``colour`` / ``moderngl`` packages and are therefore not importable in
   this environment.