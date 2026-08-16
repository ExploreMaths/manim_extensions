.. SPDX-FileCopyrightText: 2020 GarryBGoode
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

GearBox
=======

**Original author:** `GarryBGoode <https://github.com/GarryBGoode>`_

**Source repository:** `GitHub <https://github.com/GarryBGoode/manim-GearBox>`_

**License:** MIT (see the upstream repository for the full license text)

``GearBox`` is a Manim plugin for drawing realistic involute gears and
mechanisms. The geometry is based on the `tec-science involute gear article
<https://www.tec-science.com/mechanical-power-transmission/involute-gear/geometry-of-involute-gears/>`_.

The code is bundled inside ``manim_extensions`` as the ``manim_extensions.gearbox``
subpackage.

Features
--------

- Basic spur gears (:class:`~manim_extensions.gearbox.Gear`)
- Inside ring-gears (``inner_teeth=True``)
- Basic rack (:class:`~manim_extensions.gearbox.Rack`)
- Undercutting for gears with fewer than 17 teeth
- Profile-shifted gears
- Meshing calculation with distance variation via :meth:`~manim_extensions.gearbox.Gear.mesh_to`

Quick start
-----------

Because the module is included in ``manim_extensions``, you can import it
directly (``from manim_extensions.gearbox import *``). A common rendering
style is ``stroke_opacity=0`` and ``fill_opacity=1``, because the stroke
slightly enlarges the gear and can look like interference.

.. manim:: GearExample

   from manim import *
   from manim_extensions.gearbox import Gear

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

.. manim:: InnerGearExample

   from manim import *
   from manim_extensions.gearbox import Gear

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
               run_time=4,
           )

.. toctree::
   :hidden:

   classes
   functions

See the `original README <https://github.com/GarryBGoode/manim-GearBox>`_
for animated examples and further details.