Example Gallery
===============

The examples below use Manim's ``.. manim::`` directive to render the scene
inline.

.. manim:: LabelDotExample
   :save_last_frame:

   from manim_extensions import LabelDot

   class LabelDotExample(Scene):
       def construct(self):
           dot = LabelDot("A", [0, 0, 0], label_pos=UP, buff=0.2)
           self.add(dot)
