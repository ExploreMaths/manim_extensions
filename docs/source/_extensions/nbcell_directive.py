# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Notebook-style code cells for the documentation, without ``.ipynb`` files.

Replicates `nbsphinx <https://nbsphinx.readthedocs.io/>`_ (MIT) code
cells from inline reStructuredText: the directive builds the same
docutils node tree nbsphinx builds (``container(nbinput)`` holding an
``only(html)``-wrapped ``literal_block`` prompt and an ``input_area``
``literal_block``, plus the matching ``nboutput`` structure), so the
rendered HTML -- ``In [n]:`` / ``Out[n]:`` prompts, input and output
areas -- matches nbsphinx's output cell for cell, styled by
``_static/nbcell.css`` (adapted from nbsphinx's
``nbsphinx-code-cells.css``).

An interactive example can therefore live directly in a docstring or
``.rst`` file::

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
* ``:language:`` — lexer for the input cell. Defaults to ``python``.
* ``:output-language:`` — lexer for the output. Defaults to no
  highlighting.
* ``:prompt-in:`` / ``:prompt-out:`` — cell prompts, defaulting to
  ``In [1]:`` and ``Out[1]:`` (nbsphinx's own default is the shorter
  ``[%s]:``; the Jupyter-style prompts are chosen here to match the
  classic notebook look).
"""

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes


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
        prompt_in = self.options.get("prompt-in", "In [1]:")
        prompt_out = self.options.get("prompt-out", "Out[1]:")
        output = self.options.get("output")

        # Input cell: nbinput container + html-only prompt + input_area.
        input_outer = nodes.container(classes=["nbinput"])
        if not output:
            input_outer["classes"].append("nblast")
        prompt_node = nodes.literal_block(
            prompt_in, prompt_in, language="none", classes=["prompt"]
        )
        input_outer += addnodes.only("", prompt_node, expr="html")
        input_outer += nodes.literal_block(
            code, code, language=language, classes=["input_area"]
        )
        result = [input_outer]

        if output:
            out_lang = self.options.get("output-language", "none")
            output_text = output.rstrip("\n")
            output_outer = nodes.container(classes=["nboutput", "nblast"])
            out_prompt = nodes.literal_block(
                prompt_out, prompt_out, language="none", classes=["prompt"]
            )
            output_outer += addnodes.only("", out_prompt, expr="html")
            output_area = nodes.container(classes=["output_area"])
            output_area += nodes.literal_block(
                output_text, output_text, language=out_lang
            )
            output_outer += output_area
            result.append(output_outer)

        return result


def setup(app):
    """Register the nbcell directive and its stylesheet."""
    app.add_directive("nbcell", NBCell)
    app.add_css_file("nbcell.css")
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
