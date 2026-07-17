Mobjects
========

.. autoclass:: manim_extensions.compass.Compass
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. manim:: CompassExample
   :save_last_frame:

   from manim import *
   from manim_extensions.compass import Compass

   class CompassExample(Scene):
       def construct(self):
           compass = Compass().to_edge(LEFT)
           self.add(compass)

.. autoclass:: manim_extensions.compass.Pencil
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. autoclass:: manim_extensions.compass.Ruler
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. manim:: RulerExample
   :save_last_frame:

   from manim import *
   from manim_extensions.compass import Ruler

   class RulerExample(Scene):
       def construct(self):
           ruler = Ruler()
           self.add(ruler)
