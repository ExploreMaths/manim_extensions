.. SPDX-FileCopyrightText: 2020 GarryBGoode
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

GearBox
=======

.. vendored-status:: GarryBGoode/manim-GearBox

**Original author:** `GarryBGoode <https://github.com/GarryBGoode>`_

**Source repository:** `GitHub <https://github.com/GarryBGoode/manim-GearBox>`_

**License:** MIT (see the upstream repository for the full license text)

``GearBox`` is a Manim plugin for drawing realistic involute gears and
mechanisms. The geometry is based on the `tec-science involute gear article
<https://www.tec-science.com/mechanical-power-transmission/involute-gear/geometry-of-involute-gears/>`_.
The involute geometry computations use SciPy.

The code is bundled inside ``manim_extensions`` as the ``manim_extensions.gearbox``
subpackage.

Features
--------

- Basic spur gears (:class:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear`)
- Inside ring-gears (``inner_teeth=True``)
- Basic rack (:class:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Rack`)
- Undercutting for gears with fewer than 17 teeth
- Profile-shifted gears
- Meshing calculation with distance variation via :meth:`~manim_extensions.gearbox.Gear.mesh_to`

Cycloid gears and cycloid racks are planned for future development upstream.

Usage
-----

Add :class:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear`
objects and position them into meshing with
:meth:`~manim_extensions.gearbox.Gear.mesh_to`, which moves and rotates the
caller gear so that it meshes with the argument gear. Use ``fill_opacity=1``
and ``stroke_opacity=0`` when you do not want the stroke, since the stroke
increases the gear size by a couple of pixels and gives the feeling of
interference.

.. manim:: GearMeshExample
   :ref_classes: manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear

   from manim import *
   from manim_extensions.gearbox import Gear

   class GearMeshExample(Scene):
       def construct(self):
           # small gear
           gear1 = Gear(15, stroke_opacity=0, fill_color=WHITE, fill_opacity=1)
           # larger gear
           gear2 = Gear(25, stroke_opacity=0, fill_color=RED, fill_opacity=1)
           # shifting gear1 away from center
           gear1.shift(-gear1.rp * 1.5 * RIGHT)
           # position gear2 next to gear1 so that they mesh together
           gear2.mesh_to(gear1)

           self.add(gear1, gear2)
           self.play(Rotate(gear1, gear1.pitch_angle, rate_func=linear),
                     Rotate(gear2, -gear2.pitch_angle, rate_func=linear),
                     run_time=4)

For ring gears with inner teeth, pass ``inner_teeth=True`` and use the
``offset`` and ``bias`` arguments of :meth:`~manim_extensions.gearbox.Gear.mesh_to`
to control the axial distance and which tooth flank engages:

.. manim:: RingGearMeshExample
   :ref_classes: manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear
   :save_last_frame:

   from manim import *
   from manim_extensions.gearbox import Gear

   class RingGearMeshExample(Scene):
       def construct(self):
           gear1 = Gear(12, module=1, profile_shift=0.3, stroke_opacity=0,
               fill_color=WHITE, fill_opacity=1)
           gear2 = Gear(36, module=1, inner_teeth=True, profile_shift=0.1,
               stroke_opacity=0, fill_color=RED, fill_opacity=1)
           gear1.shift(gear1.rp * UP)
           gear2.shift(gear2.rp * UP)
           # mesh with 0.15*module larger distance than default
           gear2.mesh_to(gear1, offset=0.15, bias=False)
           group = VGroup(gear1, gear2).scale_to_fit_height(8)
           group.move_to(ORIGIN)
           self.add(group)

.. toctree::
   :hidden:
   :maxdepth: 1

   classes
   functions

See the `original README <https://github.com/GarryBGoode/manim-GearBox>`_
for animated examples and further details.
