"""Mesh-related visualisation utilities.

This package contains mesh generation and related helper structures used in
visual educational scenes.

    Examples
    --------

.. manim:: MeshPackageDocExample
      :save_last_frame:

   from manim import *
   from manim_extensions.meshes.models.data_models.mesh import Mesh
   from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

   class MeshPackageDocExample(Scene):
       def construct(self):
           vertices = [[0, 0, 0], [1, 0, 0], [0.5, 1, 0]]
           faces = [[0, 1, 2]]
           mesh_data = Mesh(vertices, faces)
           manim_mesh = ManimMesh(mesh_data)
           self.add(manim_mesh)
"""

__authors__ = "Martin Steinborn, Vicky Hagemeister"
__license__ = "MIT"
__status__ = "Prototype"