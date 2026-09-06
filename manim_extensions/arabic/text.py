# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Utilities for rendering Arabic text in Manim using XeLaTeX."""



from manim import *
def create_arabic_template(font_name: str = "Al Bayan") -> TexTemplate:
    """
    Create a TexTemplate configured for Arabic text rendering using XeLaTeX.

    Args:
        font_name: Name of the Arabic-supporting font to use.
                  Options: "Al Bayan" (macOS), "Geeza Pro" (macOS),
                          "Arial Unicode MS" (cross-platform)

    Returns:
        Configured TexTemplate for Arabic text rendering

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
    font_name: str = "Al Bayan",
) -> Tex:
    """
    Create a Tex object with Arabic text.

    Args:
        text: Arabic text to render
        color: LaTeX color name (arabicblue, arabicgreen, arabicred, or any xcolor)
        font_size: Font size in points
        font_name: Arabic font name

    Returns:
        Tex object with Arabic text

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
