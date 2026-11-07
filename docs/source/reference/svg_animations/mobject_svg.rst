.. SPDX-FileCopyrightText: 2023 Naveen M K
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

``mobject_svg`` module
======================

.. module:: manim_extensions.mobject_svg

.. vendored-status:: naveen521kk/manim-mobject-svg

Vendored ``manim-mobject-svg`` 0.5.0. It renders a mobject into an SVG file
through a Cairo surface and registers the helpers on manim's classes as
VMobject.to_svg() and VGroup.to_svg().

``pycairo`` is the only external dependency, and manim already requires it,
so the package ships inside ``manim_extensions`` instead of being declared
as a runtime dependency (its 0.5.x metadata declares ``python<3.13``).

.. autoall:: manim_extensions.mobject_svg

.. autoall:: manim_extensions.mobject_svg.svg
   :types: function

.. toctree::
   :hidden:
   :maxdepth: 1
