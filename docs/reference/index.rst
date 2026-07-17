Reference Manual
================

The reference manual contains the complete API for ``manim_extensions``.

Basic
-----

These modules form the core of the package and are imported directly from
``manim_extensions``.

* :doc:`../api/mobjects` – annotated mobjects such as ``LabelDot``,
  ``MathTexLine``, ``ExtendedLine``, and ``PerpendicularSign``.
* :doc:`../api/geometry` – analytic-geometry helpers such as ``CircleInt``,
  ``LineInt``, and ``TangentPoint``.
* :doc:`../api/animations` – reusable animations such as ``VisDrawArc`` and
  ``TypeWriter``.

Other Modules
-------------

The following subpackages are popular Manim plugins that are bundled inside
``manim_extensions`` as Git submodules. They can be imported directly from the
``manim_extensions`` namespace.

* :doc:`gearbox/index` – involute gears and gear trains from
  `manim-GearBox <https://github.com/GarryBGoode/manim-GearBox>`_.
* :doc:`mindmap/index` – mind maps, timelines, and catalog trees from
  `manim-mindmap <https://github.com/jj-math/manim-mindmap>`_.
* :doc:`compass/index` – compass-and-straightedge constructions from
  `manim-compass <https://github.com/jj-math/manim-compass>`_.

Each plugin section notes the original author and license.

.. toctree::
   :maxdepth: 2
   :hidden:

   ../api/index
   gearbox/index
   mindmap/index
   compass/index
