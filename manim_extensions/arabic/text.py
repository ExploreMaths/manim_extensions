# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

# patched: default font resolution — the upstream default "Al Bayan" only
#          exists on macOS, so create_arabic_template()/create_arabic_text()
#          failed on every other platform. When no font is given explicitly,
#          the first installed font from _FONT_CANDIDATES (queried via
#          fontconfig's fc-list) is used; an explicitly passed font_name is
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

    Returns *font_name* verbatim when given; otherwise the first candidate
    from :data:`_FONT_CANDIDATES` that fontconfig reports as installed,
    falling back to the historical default ("Al Bayan").
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


def create_arabic_template(font_name: Optional[str] = None) -> TexTemplate:
    """
    Create a TexTemplate configured for Arabic text rendering using XeLaTeX.

    Parameters
    ----------
    font_name
        Name of the Arabic-supporting font to use. ``None`` (the default)
        picks the first installed font from a built-in candidate list
        ("Al Bayan", "Geeza Pro", "Amiri", "Scheherazade",
        "Noto Naskh Arabic", "Arial Unicode MS") via fontconfig; pass a name
        explicitly to override.

    Returns
    -------
    TexTemplate
        Configured TexTemplate for Arabic text rendering.

    Examples
    --------
    .. manim:: CreateArabicTemplateDocExample

       from manim import *
       from manim_extensions.arabic import create_arabic_template

       class CreateArabicTemplateDocExample(Scene):
           def construct(self):
               template = create_arabic_template()
               label = Tex("مرحبا", tex_template=template, font_size=48)
               self.play(Write(label))
               self.wait()
    """
    font_name = _resolve_arabic_font(font_name)
    template = TexTemplate()
    template.tex_compiler = "xelatex"
    template.output_format = ".xdv"

    # Use fontspec to set an Arabic-supporting font
    # XeLaTeX will automatically render Arabic Unicode characters
    template.add_to_preamble(r"\usepackage{fontspec}")
    template.add_to_preamble(rf"\setmainfont{{{font_name}}}")

    # Define colors in LaTeX
    template.add_to_preamble(r"\usepackage{xcolor}")
    template.add_to_preamble(r"\definecolor{arabicblue}{RGB}{68,114,196}")
    template.add_to_preamble(r"\definecolor{arabicgreen}{RGB}{112,173,71}")
    template.add_to_preamble(r"\definecolor{arabicred}{RGB}{192,0,0}")

    return template


def create_arabic_text(
    text: str,
    color: str = "arabicblue",
    font_size: int = 34,
    font_name: Optional[str] = None,
) -> Tex:
    """
    Create a Tex object with Arabic text.

    Parameters
    ----------
    text
        Arabic text to render.
    color
        LaTeX color name (arabicblue, arabicgreen, arabicred, or any xcolor)
    font_size
        Font size in points.
    font_name
        Arabic font name. ``None`` (the default) picks the first installed
        font from a built-in candidate list; see
        :func:`~manim_extensions.arabic.text.create_arabic_template`.

    Returns
    -------
    Tex
        Tex object with Arabic text.

    Examples
    --------
    .. manim:: CreateArabicTextDocExample

       from manim import *
       from manim_extensions.arabic import create_arabic_text

       class CreateArabicTextDocExample(Scene):
           def construct(self):
               label = create_arabic_text("مرحبا", color="arabicblue",
                                          font_size=48)
               self.play(Write(label))
               self.wait()
    """
    template = create_arabic_template(font_name=font_name)
    return Tex(
        rf"\textcolor{{{color}}}{{{text}}}",
        tex_template=template,
        font_size=font_size,
    )
