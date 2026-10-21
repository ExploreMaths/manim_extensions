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

.. toctree::
   :maxdepth: 1

   classes
   functions

See the `original README <https://github.com/GarryBGoode/manim-GearBox>`_
for animated examples and further details.
