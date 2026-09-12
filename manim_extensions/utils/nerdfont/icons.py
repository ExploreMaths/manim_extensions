# SPDX-FileCopyrightText: 2025 Alexander Nasuta
#
# SPDX-License-Identifier: MIT

# Vendored from manim-nerdfont-icons 1.0.2.
# Upstream: https://github.com/Alexander-Nasuta/manim-nerdfont-icons
#
# patched: rewritten to load the font from this package instead of
#          manim_nerdfont_icons.resources, and to use
#          importlib.resources.files() (pkg_resources.path() was removed
#          in Python 3.13).
"""Create Nerd Font icon mobjects (vendored from manim-nerdfont-icons)."""

from manim import Text
import manim as m

import importlib.resources as pkg_resources

from .icons_dict import SYMBOLS_UNICODE


def nerdfont_icon(icon: int | str, **kwargs) -> Text:
    """
    Create a Nerd Font icon using the Symbols Nerd Font Mono font.
    Please have a look at the documentation for an exhaustive list of available icons:

    https://manim-nerdfont-icons.readthedocs.io/en/latest/icon-gallery.html

    :param icon: The icon to be displayed. It can be an integer (Unicode code point) or a string (icon name).
    :param kwargs: Additional keyword arguments to be passed to the Text constructor.

    :return: A Text object representing the specified icon.
    """
    font_path = pkg_resources.files("manim_extensions.utils.nerdfont") / "SymbolsNerdFontMono-Regular.ttf"
    with m.register_font(str(font_path)):

        kwargs["font"] = "Symbols Nerd Font Mono"
        if isinstance(icon, str):
            if icon in SYMBOLS_UNICODE.keys():
                return m.Text(chr(SYMBOLS_UNICODE[icon]), **kwargs)
            else:
                return m.Text(icon, **kwargs)
