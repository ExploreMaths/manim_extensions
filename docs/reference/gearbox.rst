manim-GearBox
=============

**Original author:** `GarryBGoode <https://github.com/GarryBGoode>`_

**Source repository:** https://github.com/GarryBGoode/manim-GearBox

This plugin adds realistic-looking involute gears and mechanisms to Manim.
It is included in this repository as a Git submodule for reference and easy
access.

Features
--------

- Basic spur gears
- Inside ring-gears
- Basic rack
- Undercutting (gears with fewer than 17 teeth)
- Profile-shifted gears
- Meshing calculation with distance variation

Installation
------------

The package is available on PyPI:

.. code-block:: bash

   pip install manim-gearbox

It depends on Manim and SciPy.

Usage
-----

Import both Manim and the plugin at the top of your scene file:

.. code-block:: python

   from manim import *
   from manim_gearbox import *

Create ``Gear`` objects and use ``mesh_to()`` to position two gears into mesh.
A common rendering style is to set ``stroke_opacity=0`` and ``fill_opacity=1``,
because the stroke slightly enlarges the gear and can look like interference.

Example: two meshing gears
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class GearExample(Scene):
       def construct(self):
           gear1 = Gear(15, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
           gear2 = Gear(25, stroke_opacity=0, fill_color=RED, fill_opacity=1)
           gear1.shift(-gear1.rp * 1.5 * RIGHT)
           gear2.mesh_to(gear1)

           self.add(gear1, gear2)
           self.play(
               Rotate(gear1, gear1.pitch_angle, rate_func=linear),
               Rotate(gear2, -gear2.pitch_angle, rate_func=linear),
               run_time=4,
           )

Example: inner ring gear
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   class InnerGearExample(Scene):
       def construct(self):
           gear1 = Gear(
               12, module=1, profile_shift=0.3,
               stroke_opacity=0, fill_color=WHITE, fill_opacity=1,
           )
           gear2 = Gear(
               36, module=1, inner_teeth=True, profile_shift=0.1,
               stroke_opacity=0, fill_color=RED, fill_opacity=1,
           )
           gear1.shift(gear1.rp * UP)
           gear2.shift(gear2.rp * UP)
           gear2.mesh_to(gear1, offset=0.15, bias=False)

           self.add(gear1, gear2)
           self.play(
               Rotate(gear1, gear1.pitch_angle, rate_func=linear),
               Rotate(gear2, gear2.pitch_angle, rate_func=linear),
               run_time=10,
           )

See the `original README <https://github.com/GarryBGoode/manim-GearBox/blob/main/README.md>`_
for full details and animated examples.
