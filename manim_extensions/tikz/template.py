from manim.utils.tex import TexTemplate
from typing import List


class TikzTemplate(TexTemplate):
    r"""A custom :class:`~manim.utils.tex.TexTemplate` for rendering TikZ diagrams.

    This template configures a standalone LaTeX document with the ``tikz``
    package loaded and provides hooks for injecting additional packages,
    libraries, style definitions, and raw preamble code.

    Parameters
    ----------
    packages : list[str], optional
        Additional LaTeX packages to include (e.g. ``["pgfplots"]``).
    libraries : list[str], optional
        TikZ libraries to load (e.g. ``["arrows.meta", "calc"]``).
    tikzset : list[str], optional
        Custom TikZ style definitions passed through ``\tikzset{...}``.
    preamble : str, optional
        Extra raw LaTeX code appended to the preamble.
    use_pdf : bool, optional
        If ``True``, use the PDF pipeline instead of the default DVI path.
    **kwargs
        Forwarded to :class:`~manim.utils.tex.TexTemplate`.

    Examples
    --------
    .. manim:: TikzTemplateExample
       :save_last_frame:

       from manim import *
       from manim_extensions.tikz import Tikz

       class TikzTemplateExample(Scene):
           def construct(self):
               tikz = Tikz(
                   r"\draw[fill=yellow, draw=red, thick] (0,0) circle (1);",
                   use_pdf=False,
               )
               self.add(tikz)
"""

    _DEFAULT_PREAMBLE = (
        r"\usepackage[english]{babel}" "\n"
        r"\usepackage{amsmath}" "\n"
        r"\usepackage{amssymb}" "\n"
        r"\usepackage{tikz}" "\n"
    )

    def __init__(
        self,
        packages: List[str] = [],
        libraries: List[str] = [],
        tikzset: List[str] = [],
        preamble: str = None,
        use_pdf=False,
        **kwargs
    ):
        """Initialize the TikzTemplate instance."""
        default_preamble = self._DEFAULT_PREAMBLE
        merged_preamble = (
            default_preamble
            + ("\n" + r"\usepackage{" + ", ".join(packages) + "}\n" if packages else "")
            + (
                "\n" + r"\usetikzlibrary{" + ", ".join(libraries) + "}\n"
                if libraries
                else ""
            )
            + ("\n" + r"\tikzset{" + ",\n".join(tikzset) + "}\n" if tikzset else "")
            + ("\n" + preamble if preamble else "")
        )
        super().__init__(
            tex_compiler="latex",
            documentclass=r"\documentclass[preview, tikz]{standalone}",
            output_format=".pdf" if use_pdf else ".dvi",
            preamble=merged_preamble,
            **kwargs,
        )