.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Utilities
=========

.. module:: manim_extensions.utils

Helper subpackages: :mod:`~manim_extensions.utils.deps` (lazy optional
dependency loading) and :mod:`~manim_extensions.utils.deprecation` (RST-aware
:func:`~manim_extensions.utils.deprecation.deprecated` decorator).

Usage
-----

Decorators and optional-dependency helpers used across the package.

.. code-block:: python

   from manim_extensions.utils.deprecation import deprecated
   from manim_extensions.utils.deps import require

   @deprecated("Use new_api instead.")
   def old_api():
       return "legacy"

Modules
-------

.. autosummary::
   :nosignatures:

   ~deprecation
   ~deps

.. toctree::
   :hidden:
   :maxdepth: 1

   deprecation
   deps
