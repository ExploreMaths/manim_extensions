Classes
=======

.. autoclass:: manim_extensions.gearbox.Gear
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. manim:: GearExample
   :save_last_frame:

   from manim import *
   from manim_extensions.gearbox import Gear

   class GearExample(Scene):
       def construct(self):
           gear1 = Gear(15, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
           gear2 = Gear(25, stroke_opacity=0, fill_color=RED, fill_opacity=1)
           gear1.shift(-gear1.rp * 1.5 * RIGHT)
           gear2.mesh_to(gear1)

           self.add(gear1, gear2)

.. autoclass:: manim_extensions.gearbox.Rack
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

.. manim:: RackExample
   :save_last_frame:

   from manim import *
   from manim_extensions.gearbox import Gear, Rack

   class RackExample(Scene):
       def construct(self):
           gear = Gear(15, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
           rack = Rack(12, module=gear.m, stroke_opacity=0, fill_color=RED, fill_opacity=1)
           gear.shift(RIGHT * gear.rp)
           rack.shift(UP * rack.pitch * 0.5)

           self.add(gear, rack)
