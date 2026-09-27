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
* ``:prompt-in:`` / ``:prompt-out:`` — cell prompts. When omitted, the
  prompts are ``In [n]:`` / ``Out[n]:`` with ``n`` increasing across the
  cells of each document, like a notebook's execution counters.
"""

COUNTER_KEY = "nbcell_counter"

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes

try:
    from nbcell_hash import normalize_code
except ImportError:  # pragma: no cover - direct file execution
    from .nbcell_hash import normalize_code



_cache = None


def load_execution_cache():
    """Return {hash: stdout} from the CI-executed cache, or {} if absent.

    The Docs cache workflow runs every nbcell block and stores the real
    stdout on the rtd-cache branch; Read the Docs copies it next to this
    file before building. Cells without a cache entry keep their
    hand-written ``:output:``.
    """
    global _cache
    if _cache is not None:
        return _cache
    _cache = {}
    import json
    from pathlib import Path

    path = Path(__file__).with_name("nbcell_cache.json")
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            _cache = {k: v["stdout"] for k, v in data.get("cells", {}).items()
                      if v.get("ok")}
        except Exception:
            _cache = {}
    return _cache


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
        output = self.options.get("output")
        cached = load_execution_cache().get(normalize_code(code))
        if cached is not None:
            output = cached

        # Auto-number like notebook execution counters, per document.
        document = self.state.document
        count = document.attributes.get(COUNTER_KEY, 0)
        if "prompt-in" in self.options:
            prompt_in = self.options["prompt-in"]
        else:
            count += 1
            document.attributes[COUNTER_KEY] = count
            prompt_in = f"In [{count}]:"
        if "prompt-out" in self.options:
            prompt_out = self.options["prompt-out"]
        elif "[" in prompt_in:
            prompt_out = "Out[%s]:" % prompt_in.split("[")[1].split("]")[0]
        else:
            prompt_out = ""  # custom prompt-in without brackets: no Out prompt

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
            if prompt_out:
                out_prompt = nodes.literal_block(
                    prompt_out, prompt_out, language="none", classes=["prompt"]
                )
            else:
                out_prompt = nodes.container(classes=["prompt", "empty"])
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
