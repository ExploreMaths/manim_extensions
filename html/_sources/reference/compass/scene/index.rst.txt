.. SPDX-FileCopyrightText: 2026 jj-math
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

scene
=====

.. automodule:: manim_extensions.compass.scene

Usage
-----

These scene classes provide the moving-camera rig used by the straightedge-and-compass examples.

.. manim:: CompassSceneUsage

   from manim import *
   from manim_extensions.compass import CompassScene

   class CompassSceneUsage(CompassScene):
       def construct(self):
           self.play(FadeIn(self.compass, self.ruler, self.pencil))

           A, B = ORIGIN, 2 * RIGHT
           self.set_ruler(start=A, end=B)
           self.draw_line(start=A, end=B)
           self.put_pencil_away(3 * UR)
           self.put_ruler_aside(3 * DOWN)
           self.draw_arc(niddle_point=A, pen_point=B, angle=PI / 2)
           self.put_compass_aside(4 * LEFT)
           self.wait()
