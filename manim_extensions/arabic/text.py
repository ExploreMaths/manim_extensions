# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

# patched: default font resolution — the upstream default "Al Bayan" only
#          exists on macOS, so ArabicTemplate()/ArabicText() failed on every
#          other platform. When no font is given explicitly, the first
#          installed font from _FONT_CANDIDATES (queried via fontconfig's
#          fc-list) is used; an explicitly passed font_name is
#          used verbatim.
"""Utilities for rendering Arabic text in Manim using XeLaTeX."""

import subprocess
from typing import Optional

from manim import Tex, TexTemplate


_FONT_CANDIDATES = (
    "Al Bayan",  # macOS
    "Geeza Pro",  # macOS
    "Amiri",  # Linux/Windows, fonts-amiri
    "Scheherazade",  # Linux/Windows, fonts-sil-scheherazade
    "Noto Naskh Arabic",  # Linux, fonts-noto-core
    "Arial Unicode MS",  # cross-platform if installed
)


def _resolve_arabic_font(font_name: Optional[str]) -> str:
    """Pick an installed Arabic font.

    Parameters
    ----------
    font_name
        Font name to use, or ``None`` to resolve the first installed font
        from :data:`_FONT_CANDIDATES` via fontconfig.

    Returns
    -------
        The chosen font name.
    """
    if font_name is not None:
        return font_name
    try:
        available = subprocess.check_output(
            ["fc-list", ":", "family"], text=True, stderr=subprocess.DEVNULL
        )
    except Exception:
        available = ""
    for candidate in _FONT_CANDIDATES:
        if candidate in available:
            return candidate
    return _FONT_CANDIDATES[0]


class ArabicTemplate(TexTemplate):
    """A :class:`~manim.TexTemplate` configured for Arabic text rendering using XeLaTeX.

    Parameters
    ----------
    font_name
        Name of the Arabic-supporting font to use. ``None`` picks the first
        installed font from a built-in candidate list ("Al Bayan", "Geeza Pro",
        "Amiri", "Scheherazade", "Noto Naskh Arabic", "Arial Unicode MS") via
        fontconfig; pass a name explicitly to override.

    Examples
    --------
    .. manim:: ArabicTemplateDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.arabic import ArabicTemplate

       class ArabicTemplateDocExample(Scene):
           def construct(self):
               template = ArabicTemplate()
               label = Tex("مرحبا", tex_template=template, font_size=48)
               label.scale(3)
               self.add(label)
    """

    def __init__(self, font_name: Optional[str] = None):
        """Initialize the template for Arabic typesetting."""
        super().__init__()
        font_name = _resolve_arabic_font(font_name)
        self.tex_compiler = "xelatex"
        self.output_format = ".xdv"

        # Use fontspec to set an Arabic-supporting font
        # XeLaTeX will automatically render Arabic Unicode characters
        self.add_to_preamble(r"\usepackage{fontspec}")
        self.add_to_preamble(rf"\setmainfont{{{font_name}}}")

        # Define colors in LaTeX
        self.add_to_preamble(r"\usepackage{xcolor}")
        self.add_to_preamble(r"\definecolor{arabicblue}{RGB}{68,114,196}")
        self.add_to_preamble(r"\definecolor{arabicgreen}{RGB}{112,173,71}")
        self.add_to_preamble(r"\definecolor{arabicred}{RGB}{192,0,0}")


class ArabicText(Tex):
    """A :class:`~manim.Tex` object rendered with Arabic text.

    Parameters
    ----------
    text
        Arabic text to render.
    color
        LaTeX color name (arabicblue, arabicgreen, arabicred, or any xcolor).
    font_size
        Font size in points.
    font_name
        Arabic font name. ``None`` picks the first installed font from a
        built-in candidate list; see
        :class:`~manim_extensions.arabic.text.ArabicTemplate`.

    Examples
    --------
    .. manim:: ArabicTextDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.arabic import ArabicText

       class ArabicTextDocExample(Scene):
           def construct(self):
               label = ArabicText("مرحبا", color="arabicblue", font_size=48)
               label.scale(3)
               self.add(label)
    """

    def __init__(
        self,
        text: str,
        color: str = "arabicblue",
        font_size: int = 34,
        font_name: Optional[str] = None,
    ):
        """Initialize the Arabic text object."""
        template = ArabicTemplate(font_name=font_name)
        super().__init__(
            rf"\textcolor{{{color}}}{{{text}}}",
            tex_template=template,
            font_size=font_size,
        )
