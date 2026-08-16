.. SPDX-FileCopyrightText: 2021 KingWampy
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Rubik's Cube
============

**Original author:** `KingWampy <https://github.com/WampyCakes>`_

**Source repository:** `GitHub <https://github.com/WampyCakes/manim-rubikscube>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-rubikscube`` is a Manim implementation of the classic Rubik's Cube.
It is designed for puzzle demonstrations, cube-state tutorials, and move-by-move
explanations inside scene code.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.rubikscube`` subpackage.

Features
--------

- :class:`~manim_extensions.rubikscube.cube.RubiksCube` main cube model.
- cubie-based state and face logic.
- move- and rotation-related animation helpers.
- puzzle-style demos for teaching algorithms and turns.
- easy integration into Manim scenes as a standard mobject.

Creating a RubiksCube
---------------------

After creating the :class:`~manim_extensions.rubikscube.cube.RubiksCube`, it may be necessary to scale it to
comfortably see the cube in the camera's frame.

.. manim:: FadeInExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class FadeInExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube().scale(0.6)
           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(8)

Changing the colors of a RubiksCube
-----------------------------------

The ``colors`` parameter accepts a list of six colours in the order
``[Up, Right, Front, Down, Left, Back]``. The default is
``[WHITE, "#B90000", "#009B48", "#FFD500", "#FF5900", "#0045AD"]``.

.. manim:: ColorExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class ColorExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube(colors=[WHITE, ORANGE, DARK_BLUE, YELLOW, PINK, "#00FF00"]).scale(0.6)
           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(8)

Setting the state of a RubiksCube
---------------------------------

When you have a RubiksCube in real life and want to replicate it in manim,
the :meth:`~manim_extensions.rubikscube.cube.RubiksCube.set_state` method enables this functionality. Or, if you
know the state of any cube without knowing what movements got it to that point,
this method allows you to also replicate that.

The :meth:`~manim_extensions.rubikscube.cube.RubiksCube.set_state` method takes in a string that tells the
:class:`~manim_extensions.rubikscube.cube.RubiksCube` what color each :class:`~manim_extensions.rubikscube.cubie.Cubie` should be. Imagine that you
have a RubiksCube that is flattened to 2D as below:

.. code-block:: text

               |************|
               |*U1**U2**U3*|
               |************|
               |*U4**U5**U6*|
               |************|
               |*U7**U8**U9*|
               |************|
  |************|************|************|************|
  |*L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*|
  |************|************|************|************|
  |*L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*|
  |************|************|************|************|
  |*L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*|
  |************|************|************|************|
               |************|
               |*D1**D2**D3*|
               |************|
               |*D4**D5**D6*|
               |************|
               |*D7**D8**D9*|
               |************|

In order to tell :meth:`~manim_extensions.rubikscube.cube.RubiksCube.set_state` what color the U1 cubie should
be, you tell it which face's color that is.

For example, if the R face of the Cube is pink and U1 is pink, the first
letter in the string is ``R``.

Similarly, because the center of the U face (U5) does not change color,
it will be the letter ``U`` in the state string (for the U face, that would
mean the 5th letter in the string).

Starting at the number 1 cubie and working to the number 9 cubie, the order
of the state string is the U face, then R face, followed by F, D, L, B,
in that order.

So, the first 9 letters in the string below tell the :class:`~manim_extensions.rubikscube.cube.RubiksCube` what
color each :class:`~manim_extensions.rubikscube.cubie.Cubie` in the U face is. So on and so forth for the other
sides.

This method works for a cube of any dimensions, as long as a color is
provided for each :class:`~manim_extensions.rubikscube.cubie.Cubie` face.

.. manim:: StateExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class StateExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube().scale(0.6)
           cube.set_state("BBFBUBUDFDDUURDDURLLLDFRBFRLLFFDLUFBDUBBLFFUDLRRRBLURR")

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(8)

Properties of a RubiksCube
--------------------------

Note: It is not necessary to pass any parameters to the :class:`~manim_extensions.rubikscube.cube.RubiksCube`.
Doing so is entirely for additional functionality and stylistic tweaks.

To this point, we have seen that one property of a :class:`~manim_extensions.rubikscube.cube.RubiksCube` is a
list of colors for the cube faces. There are currently two other parameters
that can be passed.

Dimension
^^^^^^^^^

.. manim:: TwoDimensionalExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class TwoDimensionalExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube(2).scale(0.6)

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(3)

An example of :meth:`~manim_extensions.rubikscube.cube.RubiksCube.set_state` on a non-3-dimensional cube:

.. manim:: TwoDimensionalStateExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class TwoDimensionalStateExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube(2).scale(0.6)
           cube.set_state("RUFBLLBDRDDBRUUDLFFBFRLU")

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(3)

10-Dimensional RubiksCube
""""""""""""""""""""""""""

.. warning::

   While this plugin can create a RubiksCube with large dimensions, it takes
   a long time to render. In the future, OpenGL rendering will vastly improve
   this.

.. manim:: TenDimensionalExample
   :save_last_frame:

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class TenDimensionalExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube(10).scale(0.2)
           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.add(cube)

Offset
^^^^^^

A :class:`~manim_extensions.rubikscube.cube.RubiksCube` has three different offset values. Offsets can be useful
for isolating faces or :class:`~manim_extensions.rubikscube.cubie.Cubie` objects for further explanation or
analysis.

The ``x_offset`` determines how close/far Cubies are from Front to Back

The ``y_offset`` determines how close/far Cubies are from Right to Left

The ``z_offset`` determines how close/far Cubies are from Top to Bottom

The default value for all three offsets is ``2.1``. Adjusting these offsets
changes the "gap" between Cubies.

.. manim:: ThreeOffsetExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class ThreeOffsetExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube(x_offset=3, y_offset=3, z_offset=3).scale(0.5)

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(3)

.. manim:: YOffsetExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class YOffsetExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube(y_offset=4).scale(0.6)

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(3)

Accessing Faces and Cubies
--------------------------

Accessing a Cubie
^^^^^^^^^^^^^^^^^

A :class:`~manim_extensions.rubikscube.cubie.Cubie` is each individual cube in a :class:`~manim_extensions.rubikscube.cube.RubiksCube`. For a
3x3x3 RubiksCube, there are 27 cubies. The cube's cubies are stored in a
numpy array called :attr:`~manim_extensions.rubikscube.cube.RubiksCube.cubies`.

For a 3-dimensional :class:`~manim_extensions.rubikscube.cube.RubiksCube`, the :attr:`~manim_extensions.rubikscube.cube.RubiksCube.cubies` array
is structured as follows:

.. code-block:: python

   Shape: (dim, dim, dim)
   [
       [
           [Cubie, Cubie, Cubie],
           [Cubie, Cubie, Cubie],
           [Cubie, Cubie, Cubie]
       ],
       [
           [Cubie, Cubie, Cubie],
           [Cubie, Cubie, Cubie],
           [Cubie, Cubie, Cubie]
       ],
       [
           [Cubie, Cubie, Cubie],
           [Cubie, Cubie, Cubie],
           [Cubie, Cubie, Cubie]
       ]
   ]

Each "level" in the array represents a coordinate. Each of the first three
arrays represents a different X value (0, 1, or 2). In each of those arrays,
there are three more arrays, each representing a different Y value (0, 1,
or 2). Finally, there are three :class:`~manim_extensions.rubikscube.cubie.Cubie` objects. Each represents a
different Z value. The size of this array directly corresponds to the
dimension of the :class:`~manim_extensions.rubikscube.cube.RubiksCube`. This structure, along with numpy,
allows for easy, convenient, and cheap accessing of cubies and faces.

For Reference: If facing the Rubik's Cube, X goes Front to Back, Y goes
Right to Left, Z goes Down to Up. Each coordinate starts at 0 and goes to
``(Dimension - 1)``.

So, to access the :class:`~manim_extensions.rubikscube.cubie.Cubie` at coordinates X=0, Y=0, Z=0,
``cube.cubies[0, 0, 0]`` will return it. This holds true no matter the
dimension of the :class:`~manim_extensions.rubikscube.cube.RubiksCube`.

.. manim:: IndicateCubieExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class IndicateCubieExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube().scale(0.6)

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )
           self.wait()

           self.play(
               Indicate(cube.cubies[0, 0, 0])
           )

           self.wait()

Accessing a Face
^^^^^^^^^^^^^^^^

The :class:`~manim_extensions.rubikscube.cube.RubiksCube` has a method called :meth:`~manim_extensions.rubikscube.cube.RubiksCube.get_face` that
will return an array of :class:`~manim_extensions.rubikscube.cubie.Cubie` objects. At its core, this just
accesses Cubies like we did above.

Because the front face of the :class:`~manim_extensions.rubikscube.cube.RubiksCube` has an X value of 0
(regardless of the dimension of the cube), returning all Cubies with an X
value of 0 will give you the front face. When
``cube.get_face("F")`` is called, it is effectively returning
``cube.cubies[0, :, :]``. This is possible for all 6 faces of the
:class:`~manim_extensions.rubikscube.cube.RubiksCube`, and it can also be used manually to return more than
just one "slice" of a :class:`~manim_extensions.rubikscube.cube.RubiksCube` at a time. This is achievable
with numpy indexing.

.. manim:: IndicateFaceExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class IndicateFaceExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube().scale(0.6)

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )
           self.wait()

           self.play(
               Indicate(VGroup(*cube.get_face("F")))
           )

           self.wait()

Accessing a Cubie Face
^^^^^^^^^^^^^^^^^^^^^^

Just as the :meth:`~manim_extensions.rubikscube.cube.RubiksCube.get_face` method works, once you have accessed
a :class:`~manim_extensions.rubikscube.cubie.Cubie` object, you can call :meth:`~manim_extensions.rubikscube.cubie.Cubie.get_face`. For example,
calling ``cube.cubies[0, 0, 0].get_face("F")`` will return the front face of
that cubie as a :class:`~manim.mobject.geometry.polygram.Square` mobject. If the :meth:`~manim.mobject.geometry.polygram.Square` method
returns a different square than you expected, it is likely a result of the
:class:`~manim_extensions.rubikscube.cube.RubiksCube`'s or the camera's orientation changing your perspective
of direction in the scene.

Face Rotations
--------------

The recommended way to rotate a face of the :class:`~manim_extensions.rubikscube.cube.RubiksCube` is to use
the :class:`~manim_extensions.rubikscube.cube_animations.CubeMove` animation. I highly discourage trying to rotate the
cube without using this pre-made animation. While possible, it's not worth it.

CubeMove animation
^^^^^^^^^^^^^^^^^^

.. manim:: CubeMoveExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube
   from manim_extensions.rubikscube.cube_animations import CubeMove

   class CubeMoveExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube().scale(0.6)

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           self.play(
               FadeIn(cube)
           )
           self.wait()

           self.play(CubeMove(cube, "F"))
           self.play(CubeMove(cube, "U2"), run_time=2)
           self.play(CubeMove(cube, "R'"))

           self.wait()

Solving the Cube
----------------

This implementation of a :class:`~manim_extensions.rubikscube.cube.RubiksCube` also includes Kociemba's
algorithm, a brilliantly fast solving algorithm made by Herbert Kociemba.
The :class:`~manim_extensions.rubikscube.cube.RubiksCube` object includes the method
:meth:`~manim_extensions.rubikscube.cube.RubiksCube.solve_by_kociemba`. Given a state, it will return a list
of moves to perform. Solving is only possible for 3-dimensional cubes.
Solving any other size :class:`~manim_extensions.rubikscube.cube.RubiksCube` will require hardcoding of the
moves to perform. Currently, :meth:`~manim_extensions.rubikscube.cube.RubiksCube.solve_by_kociemba` requires a
state string to solve (like the one used in :meth:`~manim_extensions.rubikscube.cube.RubiksCube.set_state`).
In the future, this will be replaced with using the state of the cube
without having to manually input the state of the cube.

Given the state of the Cube, it returned the necessary moves to execute to
solve it. All moves returned by the method are able to be read by
:class:`~manim_extensions.rubikscube.cube_animations.CubeMove`.

Putting it All Together
-----------------------

.. manim:: AllTogetherExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube
   from manim_extensions.rubikscube.cube_animations import CubeMove

   class AllTogetherExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube(colors=[WHITE, ORANGE, DARK_BLUE, YELLOW, PINK, "#00FF00"]).scale(0.6)

           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())

           state = "BBFBUBUDFDDUURDDURLLLDFRBFRLLFFDLUFBDUBBLFFUDLRRRBLURR"
           cube.set_state(state)

           self.play(FadeIn(cube))
           self.wait()

           for m in cube.solve_by_kociemba(state):
               self.play(CubeMove(cube, m), run_time=1.5)

           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(3)

This package is especially useful for:

* cubing tutorials,
* algorithm explanations for cube solving,
* puzzle-state visualisations in lecture material.

See the `original project <https://github.com/WampyCakes/manim-rubikscube>`_
for the full spec, examples, and documentation.

.. toctree::
   :hidden:

   classes
   animations
   functions