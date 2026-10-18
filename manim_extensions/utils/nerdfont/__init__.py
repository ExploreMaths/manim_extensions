# SPDX-FileCopyrightText: 2026 ExploreMaths
#
# SPDX-License-Identifier: MIT

"""Vendored copy of manim-nerdfont-icons (code and font licensed MIT).

Upstream: https://github.com/Alexander-Nasuta/manim-nerdfont-icons (v1.0.2).
Vendored because the 1.0.x PyPI release pins ``manim>=0.19,<0.20`` even
though the package works with current manim.
"""

from .icons import _install_font_linux, NerdFontIcon
from .icons_dict import SYMBOLS_UNICODE

__all__ = ["NerdFontIcon", "SYMBOLS_UNICODE", "_install_font_linux"]
