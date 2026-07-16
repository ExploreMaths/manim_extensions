manim-GearBox
=============

**Original author:** `GarryBGoode <https://github.com/GarryBGoode>`_

**Source repository:** https://github.com/GarryBGoode/manim-GearBox

**License:** MIT (see the upstream repository for the full license text)

``manim-GearBox`` is a Manim plugin for drawing realistic involute gears and
mechanisms. The geometry is based on the `tec-science involute gear article
<https://www.tec-science.com/mechanical-power-transmission/involute-gear/geometry-of-involute-gears/>`_.

The code is included in this repository as a Git submodule under
``third_party/manim-GearBox``. The submodule points to an ExploreMaths fork that
adds extra docstrings to the original code while keeping all logic unchanged.

Features
--------

- Basic spur gears (:class:`Gear`)
- Inside ring-gears (``inner_teeth=True``)
- Basic rack (:class:`Rack`)
- Undercutting for gears with fewer than 17 teeth
- Profile-shifted gears
- Meshing calculation with distance variation via :meth:`Gear.mesh_to`

Installation
------------

Install from PyPI:

.. code-block:: bash

   pip install manim-gearbox

Or use the local submodule:

.. code-block:: bash

   git submodule update --init third_party/manim-GearBox
   pip install -e third_party/manim-GearBox

Both methods require Manim and SciPy.

Quick start
-----------

Import Manim and the plugin at the top of your scene:

.. code-block:: python

   from manim import *
   from manim_gearbox import *

A common rendering style is ``stroke_opacity=0`` and ``fill_opacity=1``,
because the stroke slightly enlarges the gear and can look like interference.

Two meshing gears
^^^^^^^^^^^^^^^^^

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

Inner ring gear
^^^^^^^^^^^^^^^

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

API reference
-------------

.. automodule:: manim_gearbox
   :members:
   :undoc-members:
   :show-inheritance:

See the `original README <https://github.com/GarryBGoode/manim-GearBox/blob/main/README.md>`_
for animated examples and further details.
