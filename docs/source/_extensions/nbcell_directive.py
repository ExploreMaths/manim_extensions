# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Notebook-style code cells for the documentation, without ``.ipynb`` files.

Replicates the look of `nbsphinx <https://nbsphinx.readthedocs.io/>`_
code cells (same HTML structure and class names) while accepting inline
reStructuredText content, so an interactive example can live directly in
a docstring or ``.rst`` file::

    .. nbcell::

        from manim_extensions.chemistry import GraphMolecule
        molecule = GraphMolecule.molecule_from_file("acetone_2d.mol")
        molecule.find_atom_position_by_index(1)

    .. nbcell::
        :output: array([ 0.9397, -0.7497,  0.    ])

        from manim_extensions.chemistry import GraphMolecule
        molecule = GraphMolecule.molecule_from_file("acetone_2d.mol")
        molecule.find_atom_position_by_index(1)

Options:

* ``:output:`` — text rendered as the cell's stdout result. May span
  several lines when the continuation lines are indented further than
  the option itself.
* ``:language:`` — Pygments lexer for the input cell. Defaults to
  ``python``.
* ``:output-language:`` — Pygments lexer for the output. Defaults to
  plain ``text``.
* ``:prompt-in:`` / ``:prompt-out:`` — cell prompts, defaulting to
  ``In [1]:`` and ``Out[1]:``.

For non-HTML builders a plain ``literal_block`` fallback (hidden in HTML
by ``nbcell.css``) keeps the code visible in other output formats.
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from xml.sax.saxutils import escape as html_escape


def _highlight(code: str, language: str) -> str:
    """Pygments-highlight ``code``, falling back to plain text."""
    try:
        lexer = get_lexer_by_name(language)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    return highlight(code, lexer, HtmlFormatter()).rstrip("\n")


class NBCell(Directive):
    """Render one notebook-style cell pair (input, optional output)."""

    has_content = True
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "output": directives.unchanged,
        "language": directives.unchanged,
        "output-language": directives.unchanged,
        "prompt-in": directives.unchanged,
        "prompt-out": directives.unchanged,
    }

    def run(self):
        code = "\n".join(self.content)
        language = self.options.get("language", "python")
        prompt_in = self.options.get("prompt-in", "In\u00a0[1]:")
        prompt_out = self.options.get("prompt-out", "Out[1]:")
        output = self.options.get("output")

        parts = [
            '<div class="nbinput docutils container">',
            '<div class="prompt highlight-none notranslate">'
            '<div class="highlight"><pre>'
            f'<span class="gp">{html_escape(prompt_in)}</span>&nbsp;'
            "</pre></div></div>",
            f'<div class="input_area highlight-{html_escape(language)} notranslate">',
            _highlight(code, language),
            "</div></div>",
        ]
        if output:
            out_lang = self.options.get("output-language", "text")
            parts += [
                '<div class="nboutput nblast docutils container">',
                '<div class="prompt highlight-none notranslate">'
                '<div class="highlight"><pre>'
                f'<span class="gp">{html_escape(prompt_out)}</span>&nbsp;'
                "</pre></div></div>",
                '<div class="output_area docutils container">',
                _highlight(output.rstrip("\n"), out_lang),
                "</div></div>",
            ]

        raw = nodes.raw("", "\n".join(parts), format="html")
        # Fallback for non-HTML builders: the raw node is dropped there,
        # so keep the plain code visible in e.g. LaTeX output.
        fallback_src = code if not output else f"{code}\n{output}"
        fallback = nodes.literal_block(fallback_src, fallback_src)
        fallback["classes"].append("nbcell-fallback")
        return [raw, fallback]


def setup(app):
    """Register the nbcell directive and its stylesheet."""
    app.add_directive("nbcell", NBCell)
    app.add_css_file("nbcell.css")
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
