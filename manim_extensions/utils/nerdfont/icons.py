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
# patched: install the font into the fontconfig user font directory on
#          Linux. On modern Linux stacks (pango >= 1.52 / fontconfig
#          >= 2.15, e.g. ubuntu-24.04) Pango resolves families through a
#          per-process fontmap snapshot taken at initialization: fonts
#          registered afterwards — both manimpango's register_font
#          (FcConfigAppFontAddFile) and fonts copied into fontconfig
#          directories with a post-hoc fc-cache — are invisible to it.
#          The icon Text then falls back per character, and with a CJK
#          font installed (RTD/CI apt packages) the Private Use Area
#          codepoints render as CJK glyphs. The font must be in place
#          BEFORE Pango initializes, so the installation happens at
#          module import time (importing manim does not initialize Pango)
#          and the docs build/CI pre-install it before rendering.
"""Create Nerd Font icon mobjects (vendored from manim-nerdfont-icons)."""

from manim import Text
import manim as m

import importlib.resources as pkg_resources
import os
import platform
import shutil
import subprocess
from typing import Any

from .icons_dict import SYMBOLS_UNICODE

_FONT_FILENAME = "SymbolsNerdFontMono-Regular.ttf"
_font_installed = False


def _font_path() -> str:
    return str(pkg_resources.files("manim_extensions.utils.nerdfont") / _FONT_FILENAME)


def _install_font_linux() -> None:
    """Install the TTF into the fontconfig user font dir (Linux only).

    Idempotent and best-effort: a missing ``fc-cache`` binary or an
    unwritable home directory is silently ignored (``register_font``
    remains sufficient on Windows/macOS and older pango).
    """
    global _font_installed
    if _font_installed or platform.system() != "Linux":
        return
    _font_installed = True
    try:
        font_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "fonts")
        os.makedirs(font_dir, exist_ok=True)
        dest = os.path.join(font_dir, _FONT_FILENAME)
        if not os.path.exists(dest):
            shutil.copy2(_font_path(), dest)
        # Rebuild the cache even if the file already exists: it may have
        # landed after the cache for that directory was written.
        subprocess.run(["fc-cache", "-f", font_dir], capture_output=True)
    except OSError:
        pass


# Install as early as possible: at import time Pango is usually not
# initialized yet in this process (importing manim does not touch it), so
# fontconfig picks the font up when Pango later builds its fontmap.
_install_font_linux()


def nerdfont_icon(icon: int | str, **kwargs: Any) -> Text:
    """
    Create a Nerd Font icon using the Symbols Nerd Font Mono font.
    Please have a look at the documentation for an exhaustive list of available icons.

    https://manim-nerdfont-icons.readthedocs.io/en/latest/icon-gallery.html

    Parameters
    ----------
    icon : int or str
        The icon to be displayed: an integer Unicode code point, or a
        string giving either an icon name from the Nerd Font icon set
        (resolved via :mod:`~manim_extensions.utils.nerdfont.icons_dict`)
        or literal text to render.
    **kwargs
        Additional keyword arguments to be passed to the
        :class:`~manim.mobject.text.text_mobject.Text` constructor.

    Returns
    -------
    Text
        A Text object representing the specified icon.
    """
    font_path = _font_path()
    _install_font_linux()
    with m.register_font(font_path):
        kwargs["font"] = "Symbols Nerd Font Mono"
        if isinstance(icon, str):
            if icon in SYMBOLS_UNICODE.keys():
                return m.Text(chr(SYMBOLS_UNICODE[icon]), **kwargs)
            else:
                return m.Text(icon, **kwargs)
        elif isinstance(icon, int):
            return m.Text(chr(icon), **kwargs)
