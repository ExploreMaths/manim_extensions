.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

QR Codes
========

.. module:: manim_extensions.qr_codes

.. vendored-status:: Alexander-Nasuta/manim-qr-codes

**Original author:** `Alexander Nasuta <https://github.com/Alexander-Nasuta>`_

**Source repository:** `GitHub <https://github.com/Alexander-Nasuta/manim-qr-codes>`_

**License:** MIT

``manim-qr-codes`` generates QR codes as Manim :class:`~manim.mobject.types.vectorized_mobject.VGroup` objects using the
`segno <https://pypi.org/project/segno/>`_ library. An optional Nerd Font
icon can be placed in the centre of the code.

The code is bundled inside ``manim_extensions`` as the
:mod:`~manim_extensions.qr_codes` subpackage.  Instantiate
:class:`~manim_extensions.qr_codes.qr.QRCode` with the payload and optional
styling arguments.

.. important::

   The optional ``icon`` argument uses the bundled
   :class:`~manim_extensions.nerdfont.icons.NerdFontIcon`, so no separate
   install is required.

Usage
-----

.. manim:: QRCodeWithIcon
   :save_last_frame:
   :ref_classes: QRCode

   from manim import *
   from manim_extensions.qr_codes import QRCode

   class QRCodeWithIcon(Scene):
       def construct(self):
           code_without_icon = QRCode("https://fishshell.com")
           code_with_icon = QRCode(
               payload="https://fishshell.com",
               icon="terminal",
               icon_size=6,
           )
           code_group = VGroup(
               code_without_icon,
               code_with_icon).arrange(RIGHT, buff=0.75)
           label = Text("https://fishshell.com")
           label.to_edge(UP, buff=0.75)
           self.add(code_group, label)

See the `example gallery <https://manim-qr-codes.readthedocs.io/en/latest/example-gallery.html>`_
of the upstream documentation for more animated examples.

Modules
-------

.. autosummary::
   :nosignatures:

   ~logger
   ~qr

.. toctree::
   :hidden:
   :maxdepth: 1

   logger
   qr
