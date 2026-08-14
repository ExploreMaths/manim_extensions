API reference
=============

Data model
----------

.. autoclass:: manim_extensions.meshes.models.data_models.mesh.Mesh
   :members:
   :undoc-members:
   :show-inheritance:

.. note::

   The manim-side renderers (``ManimMesh``, ``Manim2DMesh``, ``TriangleManim2DMesh``
   and the OpenGL ``FastManimMesh``) as well as the Delaunay helpers depend on the
   optional ``colour`` / ``moderngl`` packages and are therefore not importable in
   this environment.

Helpers
-------

.. autofunction:: manim_extensions.meshes.decorators.dangling_vert_decorator
.. autofunction:: manim_extensions.meshes.decorators.dangling_face_decorator

.. autofunction:: manim_extensions.meshes.helpers.is_in_vararray
.. autofunction:: manim_extensions.meshes.helpers.find_in_vararray
.. autofunction:: manim_extensions.meshes.helpers.is_vararray_equal
.. autofunction:: manim_extensions.meshes.helpers.is_twice_nested_iterable
.. autofunction:: manim_extensions.meshes.helpers.are_edges_equal
.. autofunction:: manim_extensions.meshes.helpers.fix_references
.. autofunction:: manim_extensions.meshes.helpers.remove_keys_from_dict

Exceptions
----------

.. autoclass:: manim_extensions.meshes.exceptions.InvalidMeshException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: manim_extensions.meshes.exceptions.InvalidRequestException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: manim_extensions.meshes.exceptions.MeshIndexException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: manim_extensions.meshes.exceptions.InvalidTypeException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: manim_extensions.meshes.exceptions.InvalidMeshDimensionsException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: manim_extensions.meshes.exceptions.InvalidShapeException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: manim_extensions.meshes.exceptions.BadParameterException
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: manim_extensions.meshes.exceptions.FaultyVarArrayException
   :members:
   :undoc-members:
   :show-inheritance:
