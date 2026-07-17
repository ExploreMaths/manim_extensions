Mind maps
=========

.. autoclass:: manim_extensions.mindmap.MindMap
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. manim:: MindMapExample
   :save_last_frame:

   from manim import *
   from manim_extensions.mindmap import MindMap

   class MindMapExample(Scene):
       def construct(self):
           data = {
               'node': MathTex(r"Calculus"),
               'child': [
                   {'node': MathTex(r"Limits")},
                   {'node': MathTex(r"Derivatives")},
                   {'node': MathTex(r"Integrals")},
               ]
           }
           mind_map = MindMap(data)
           mind_map.scale_to_fit_width(12)
           self.add(mind_map)

.. autoclass:: manim_extensions.mindmap.StandardMap
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.CatalogMap
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.mindmap.TimeLine
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
