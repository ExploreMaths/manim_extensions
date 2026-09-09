# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Font Awesome icons for Manim.

This module provides access to Font Awesome icons (brand, regular, and solid styles).
It includes 2000+ SVG icons that can be used in Manim animations.

"""

from .manim_fontawesome import *
from .manim_fontawesome import __all__ as _manim_fontawesome_all

__all__ = list(_manim_fontawesome_all)

del _manim_fontawesome_all