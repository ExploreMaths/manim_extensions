.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

space
=====

.. automodule:: manim_extensions.pymunk.space

Usage
-----

Create a physics space and run it inside a scene.

.. manim:: SpaceSceneUsage
   :ref_classes: SpaceScene VSpace

   from manim import *
   from manim_extensions.pymunk import *

   class SpaceSceneUsage(SpaceScene):
       def construct(self):
           floor = Line(LEFT * 6, RIGHT * 6, stroke_width=8, color=GREY)
           floor.to_edge(DOWN, buff=0.5)
           wall1 = Line([-6, -3.5, 0], [-6, 3.5, 0], stroke_width=8, color=GREY)
           wall2 = Line([6, -3.5, 0], [6, 3.5, 0], stroke_width=8, color=GREY)
           ceiling = Line([-6, 3.5, 0], [6, 3.5, 0], stroke_width=8, color=GREY)
           walls = VGroup(floor, wall1, wall2, ceiling)
           balls = VGroup(*[
               Circle(radius=0.3, color=BLUE, fill_opacity=0.8).move_to(
                   UP * 3 + (i - 1) * RIGHT
               )
               for i in range(3)
           ])
           self.play(FadeIn(walls), FadeIn(balls))
           self.add_static_body(floor, wall1, wall2, ceiling)
           self.add_dynamic_body(*balls)
           self.add_shapes_filter(*balls, group=1)
           self.apply_impulse_at_world_point(
               balls[0], impulse=(4, 2, 0), point=tuple(balls[0].get_center())
           )
           self.wait(3)

Modules
-------

.. autosummary::
   :nosignatures:

   ~SpaceScene
   ~VSpace

.. toctree::
   :hidden:
   :maxdepth: 1

   SpaceScene
   VSpace
