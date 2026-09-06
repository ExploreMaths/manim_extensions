# SPDX-FileCopyrightText: 2023 Ralphie Raccoon
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""TikZ integration for Manim.

This module provides TikZ markup to SVG conversion for Manim animations.

"""

from manim import *
from manim.utils.tex_file_writing import tex_to_svg_file
from .template import TikzTemplate

from typing import List, Optional


class Tikz(SVGMobject):
    r"""Convert TikZ markup into an SVG-based mobject for use in Manim.

    Parameters
    ----------
    code : str
        The TikZ markup to convert into a rendered SVG.
    packages : list[str] | None, optional
        Additional LaTeX packages to include in the preamble, such as
        ``\usepackage{...}`` definitions.
    libraries : list[str] | None, optional
        TikZ libraries to load, such as ``arrows.meta`` or ``calc``.
    tikzset : list[str] | None, optional
        Custom TikZ style definitions to inject through ``\tikzset{...}``.
    preamble : str | None, optional
        Extra LaTeX code appended directly to the document preamble.
    use_pdf : bool, optional
        Whether to render through the PDF pipeline instead of the default DVI
        path when compatibility issues arise.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.svg.svg_mobject.SVGMobject`.

    Examples
    --------
    .. manim:: ManimTikzExample
       :save_last_frame:

       from manim import *
       from manim_extensions.tikz import Tikz

       class ManimTikzExample(Scene):
           def construct(self):
               graph = Tikz(
                   r"\node[draw, circle, fill=blue!20] (a) at (0,0) {A};"
                   r"\node[draw, circle, fill=red!20] (b) at (2.5,0) {B};"
                   r"\draw[conn] (a) -- (b);",
                   libraries=["arrows.meta"],
                   tikzset=["conn/.style={-{Stealth[length=3mm]}, thick, red}"],
                   use_pdf=False,
               )
               self.add(graph)

    .. manim:: TikzDrawExample
       :save_last_frame:

       from manim import *
       from manim_extensions.tikz import Tikz

       class TikzDrawExample(Scene):
           def construct(self):
               square = Tikz(
                   r"\draw[magenta, line width=10mm, fill=blue] (0,0) rectangle(1,1);",
                   use_pdf=False,
               )
               self.add(square)
    """

    def __init__(
        self,
        code: str,
        packages: Optional[List[str]] = None,
        libraries: Optional[List[str]] = None,
        tikzset: Optional[List[str]] = None,
        preamble: Optional[str] = None,
        use_pdf: Optional[bool] = False,
        **kwargs,
    ):
        """Initialize the TikZ instance."""
        file_name = self.convert(code, packages, libraries, tikzset, preamble, use_pdf)
        super().__init__(
            file_name,
            **kwargs,
        )

    def convert(
        self,
        code: str,
        packages: Optional[List[str]] = None,
        libraries: Optional[List[str]] = None,
        tikzset: Optional[List[str]] = None,
        preamble: Optional[str] = None,
        use_pdf: bool = False,
    ) -> str:
        """Convert a TikZ string into an SVG file path.

        Parameters
        ----------
        code : str
            The TikZ markup to be rendered.
        packages : list[str] | None, optional
            Additional LaTeX packages required by the TikZ code.
        libraries : list[str] | None, optional
            TikZ libraries required by the drawing commands.
        tikzset : list[str] | None, optional
            Custom TikZ style definitions to add to the preamble.
        preamble : str | None, optional
            Additional raw LaTeX content added to the document preamble.
        use_pdf : bool, optional
            Whether to use the PDF rendering path for compatibility with some
            TikZ commands.

        Returns
        -------
        str
            The generated SVG file path.
        """
        return tex_to_svg_file(
            code,
            environment="tikzpicture",
            tex_template=TikzTemplate(packages, libraries, tikzset, preamble, use_pdf),
        )