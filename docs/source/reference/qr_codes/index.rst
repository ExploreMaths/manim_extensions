.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

QR Codes
========

**Original author:** `Alexander Nasuta <https://github.com/Alexander-Nasuta>`_

**Source repository:** `GitHub <https://github.com/Alexander-Nasuta/manim-qr-codes>`_

**License:** MIT

``manim-qr-codes`` generates QR codes as Manim ``VGroup`` objects using the
`segno <https://pypi.org/project/segno/>`_ library. An optional Nerd Font
icon can be placed in the centre of the code.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.qr_codes`` subpackage.

.. note::

   The optional ``icon`` argument requires the ``manim-nerdfont-icons``
   package, which is not declared as a dependency (its PyPI metadata pins
   ``manim<0.20``). Install it separately with
   ``pip install --no-deps manim-nerdfont-icons``.

Quick start
-----------

.. manim:: QRCodeExample
   :save_last_frame:

   from manim import *
   from manim_extensions.qr_codes import qr_code

   class QRCodeExample(Scene):
       def construct(self):
           qr = qr_code("https://example.com")
           self.add(qr)

.. toctree::
   :hidden:

   functions
