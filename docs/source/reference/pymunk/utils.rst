.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Utilities
=========

Geometry helpers used to convert Manim mobjects into Pymunk shapes, and a
singleton logger shared by the physics classes.

Helpers
-------

.. autofunction:: manim_extensions.pymunk.utils.img_tools.get_normalized_convex_polygons

.. autofunction:: manim_extensions.pymunk.utils.img_tools.map_polygons_to_manim

.. autofunction:: manim_extensions.pymunk.utils.tools_func.get_moment_for_box

.. autofunction:: manim_extensions.pymunk.utils.tools_func.get_moment_for_circle

.. autofunction:: manim_extensions.pymunk.utils.tools_func.get_moment_for_line

.. autofunction:: manim_extensions.pymunk.utils.tools_func.get_moment_for_poly

Logger
------

.. autodata:: manim_extensions.pymunk.utils.logger_tool.manim_pymunk_logger
   :annotation:

.. autoclass:: manim_extensions.pymunk.utils.logger_tool.SingletonLogger
   :show-inheritance:
