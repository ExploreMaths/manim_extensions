# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

# mypy: disable-error-code="misc,no-untyped-def,var-annotated,assignment,arg-type"

"""Utilities for the doc_directive module."""

from __future__ import annotations
from typing import Any, cast

"""
A directive for including Manim videos in a Sphinx document.
"""

# unlinked-class-ok: Space


from manim import QUALITIES, config, tempconfig
from sphinx.application import Sphinx
import csv
import itertools as it
import re
import shutil
import sys
from pathlib import Path
from timeit import timeit

import jinja2
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList

classnamedict = {}


class SkipManimNode(nodes.Admonition, nodes.Element):
    """Auxiliary node class that is used when the ``skip-manim`` tag is present
    or ``.pot`` files are being built.

    Skips rendering the manim directive and outputs a placeholder instead.

    Examples
    --------
    .. manim:: SkipManimNodeOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.utils.testing.doc_directive import SkipManimNode

       SkipManimNodeTarget = SkipManimNode

       class SkipManimNodeOverview(Scene):
           def construct(self):
               public = [n for n in dir(SkipManimNodeTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('SkipManimNode', font_size=36),
                   Text('module: manim_extensions.machine_learning.utils.testing.doc_directive', font_size=18, color=GREY),
                   Text('Auxiliary node class that is used when the skip-manim tag is present or .pot files are being built', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        # Internal docutils node used by the documentation extension.
        node = SkipManimNode()
    """

    pass


def visit(self, node: list[Any], name: str = "") -> Any:
    """Visit a :class:`~manim_extensions.machine_learning.utils.testing.doc_directive.SkipManimNode`, adding a placeholder title if missing, then render as admonition.

    Parameters
    ----------
    node
        The :class:`~manim_extensions.machine_learning.utils.testing.doc_directive.SkipManimNode` to visit.
    name
        Name of the admonition.


    Returns
    -------
            The resulting value.
    """
    self.visit_admonition(node, name)
    if not isinstance(node[0], nodes.title):
        node.insert(0, nodes.title("skip-manim", "Example Placeholder"))


def depart(self, node: SkipManimNode) -> Any:
    """Depart from a :class:`~manim_extensions.machine_learning.utils.testing.doc_directive.SkipManimNode` by closing the admonition rendering.

    Parameters
    ----------
    node
        The :class:`~manim_extensions.machine_learning.utils.testing.doc_directive.SkipManimNode` to depart from.


    Returns
    -------
            The resulting value.
    """
    self.depart_admonition(node)


def process_name_list(option_input: str, reference_type: str) -> list[str]:
    r"""Reformats a string of space separated class names
    as a list of strings containing valid Sphinx references.

    Tests
    -----

    ::
        >>> process_name_list("Tex TexTemplate", "class")
        [':class:`~manim.mobject.text.tex_mobject.Tex`', ':class:`~manim.utils.tex.TexTemplate`']
        >>> process_name_list("Scene.play Mobject.rotate", "func")
        [':func:`~manim.scene.scene.Scene.play`', ':func:`~manim.mobject.mobject.Mobject.rotate`']

    Parameters
    ----------
    option_input
        Space separated class names to reformat.
    reference_type
        Type of Sphinx reference to generate (e.g. "class" or "func").

    Returns
    -------
        List of strings containing valid Sphinx references.
    """
    return [f":{reference_type}:`~.{name}`" for name in option_input.split()]


class ManimDirective(Directive):
    """The manim directive, rendering videos while building
    the documentation.

    See the module docstring for documentation.

    Examples
    --------
    .. manim:: ManimDirectiveOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.utils.testing.doc_directive import ManimDirective

       ManimDirectiveTarget = ManimDirective

       class ManimDirectiveOverview(Scene):
           def construct(self):
               public = [n for n in dir(ManimDirectiveTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('ManimDirective', font_size=36),
                   Text('module: manim_extensions.machine_learning.utils.testing.doc_directive', font_size=18, color=GREY),
                   Text('The manim directive, rendering videos while building the documentation', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)
    .. code-block:: python

        # Internal docutils directive registered as ``.. manim::``.
        directive = ManimDirective()
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "hide_source": bool,
        "no_autoplay": bool,
        "quality": lambda arg: directives.choice(
            arg,
            ("low", "medium", "high", "fourk"),
        ),
        "save_as_gif": bool,
        "save_last_frame": bool,
        "ref_modules": lambda arg: process_name_list(arg, "mod"),
        "ref_classes": lambda arg: process_name_list(arg, "class"),
        "ref_functions": lambda arg: process_name_list(arg, "func"),
        "ref_methods": lambda arg: process_name_list(arg, "meth"),
    }
    final_argument_whitespace = True

    def run(self) -> list[Any]:
        """Execute the directive: either render the manim example or output a placeholder.

        Returns
        -------
            A list of the results.

        Raises
        ------
        ValueError
            Raised when an invalid combination of render flags is given.
        """
        # Rendering is skipped if the tag skip-manim is present,
        # or if we are making the pot-files
        should_skip = (
            "skip-manim" in self.state.document.settings.env.app.builder.tags.tags
            or self.state.document.settings.env.app.builder.name == "gettext"
        )
        if should_skip:
            node = SkipManimNode()
            self.state.nested_parse(
                StringList(
                    [
                        f"Placeholder block for ``{self.arguments[0]}``.",
                        "",
                        ".. code-block:: python",
                        "",
                    ]
                    + ["    " + line for line in self.content]
                ),
                self.content_offset,
                node,
            )
            return [node]

        clsname = self.arguments[0]
        if clsname not in classnamedict:
            classnamedict[clsname] = 1
        else:
            classnamedict[clsname] += 1

        hide_source = "hide_source" in self.options
        no_autoplay = "no_autoplay" in self.options
        save_as_gif = "save_as_gif" in self.options
        save_last_frame = "save_last_frame" in self.options
        assert not (save_as_gif and save_last_frame)

        ref_content = (
            self.options.get("ref_modules", [])
            + self.options.get("ref_classes", [])
            + self.options.get("ref_functions", [])
            + self.options.get("ref_methods", [])
        )
        if ref_content:
            ref_block = "References: " + " ".join(ref_content)

        else:
            ref_block = ""

        if "quality" in self.options:
            quality = f'{self.options["quality"]}_quality'
        else:
            quality = "example_quality"
        frame_rate = QUALITIES[quality]["frame_rate"]
        pixel_height = QUALITIES[quality]["pixel_height"]
        pixel_width = QUALITIES[quality]["pixel_width"]

        state_machine = self.state_machine
        document = state_machine.document

        source_file_name = Path(document.attributes["source"])
        source_rel_name = source_file_name.relative_to(cast(Any, setup).confdir)
        source_rel_dir = source_rel_name.parents[0]
        dest_dir = Path(cast(Any, setup).app.builder.outdir, source_rel_dir).absolute()
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)

        source_block = [
            ".. code-block:: python",
            "",
            "    from manim import *\n",
            *("    " + line for line in self.content),
        ]
        source_block = "\n".join(source_block)

        config.media_dir = (Path(cast(Any, setup).confdir) / "media").absolute()
        config.images_dir = "{media_dir}/images"
        config.video_dir = "{media_dir}/videos/{quality}"
        output_file = f"{clsname}-{classnamedict[clsname]}"
        config.assets_dir = Path("_static")
        config.progress_bar = "none"
        config.verbosity = "WARNING"

        example_config = {
            "frame_rate": frame_rate,
            "no_autoplay": no_autoplay,
            "pixel_height": pixel_height,
            "pixel_width": pixel_width,
            "save_last_frame": save_last_frame,
            "write_to_movie": not save_last_frame,
            "output_file": output_file,
        }
        if save_last_frame:
            example_config["format"] = None
        if save_as_gif:
            example_config["format"] = "gif"

        user_code = self.content
        if user_code[0].startswith(">>> "):  # check whether block comes from doctest
            user_code = [
                line[4:] for line in user_code if line.startswith((">>> ", "... "))
            ]

        code = [
            "from manim import *",
            *user_code,
            f"{clsname}().render()",
        ]

        with tempconfig(example_config):
            run_time = timeit(lambda: exec("\n".join(code), globals()), number=1)
            video_dir = config.get_dir("video_dir")
            images_dir = config.get_dir("images_dir")

        _write_rendering_stats(
            clsname,
            run_time,
            self.state.document.settings.env.docname,
        )

        # copy video file to output directory
        if not (save_as_gif or save_last_frame):
            filename = f"{output_file}.mp4"
            filesrc = video_dir / filename
            destfile = Path(dest_dir, filename)
            shutil.copyfile(filesrc, destfile)
        elif save_as_gif:
            filename = f"{output_file}.gif"
            filesrc = video_dir / filename
        elif save_last_frame:
            filename = f"{output_file}.png"
            filesrc = images_dir / filename
        else:
            raise ValueError("Invalid combination of render flags received.")
        rendered_template = jinja2.Template(TEMPLATE).render(
            clsname=clsname,
            clsname_lowercase=clsname.lower(),
            hide_source=hide_source,
            filesrc_rel=Path(filesrc).relative_to(cast(Any, setup).confdir).as_posix(),
            no_autoplay=no_autoplay,
            output_file=output_file,
            save_last_frame=save_last_frame,
            save_as_gif=save_as_gif,
            source_block=source_block,
            ref_block=ref_block,
        )
        state_machine.insert_input(
            rendered_template.split("\n"),
            source=document.attributes["source"],
        )

        return []


rendering_times_file_path = Path("../rendering_times.csv")


def _write_rendering_stats(scene_name: str, run_time: float, file_name: str) -> Any:
    """Append one rendering-time row to the statistics CSV.

    Parameters
    ----------
    scene_name
        Name of the rendered scene.
    run_time
        Rendering duration in seconds.
    file_name
        The source file that contains the example.


    Returns
    -------
            The resulting value.
    """
    with rendering_times_file_path.open("a") as file:
        csv.writer(file).writerow(
            [
                re.sub(r"^(reference\/)|(manim\.)", "", file_name),
                scene_name,
                "%.3f" % run_time,
            ],
        )


def _log_rendering_times(*args: Any) -> Any:
    """Print a summary of the collected rendering times.

    Parameters
    ----------
    *args
        Ignored Sphinx event arguments.


    Returns
    -------
            The resulting value.
    """
    if rendering_times_file_path.exists():
        with rendering_times_file_path.open() as file:
            data = list(csv.reader(file))
        if len(data) == 0:
            sys.exit()

        print("\nRendering Summary\n-----------------\n")

        max_file_length = max(len(row[0]) for row in data)
        for key, raw_group in it.groupby(data, key=lambda row: row[0]):
            key = key.ljust(max_file_length + 1, ".")
            group = list(raw_group)
            if len(group) == 1:
                row = group[0]
                print(f"{key}{row[2].rjust(7, '.')}s {row[1]}")
                continue
            time_sum = sum(float(row[2]) for row in group)
            print(
                f"{key}{f'{time_sum:.3f}'.rjust(7, '.')}s  => {len(group)} EXAMPLES",
            )
            for row in group:
                print(f"{' '*(max_file_length)} {row[2].rjust(7)}s {row[1]}")
        print("")


def _delete_rendering_times(*args: Any) -> Any:
    """Remove the rendering-time CSV if it exists.

    Parameters
    ----------
    *args
        Ignored Sphinx event arguments.


    Returns
    -------
            The resulting value.
    """
    if rendering_times_file_path.exists():
        rendering_times_file_path.unlink()


def setup(app: Sphinx) -> dict[Any, Any]:
    """Register the manim directive and its nodes with the Sphinx application.

    Parameters
    ----------
    app
        The Sphinx application to register the directive with.

    Returns
    -------
        A dictionary of the results.
    """
    app.add_node(SkipManimNode, html=(visit, depart))

    cast(Any, setup).app = app
    cast(Any, setup).config = cast(Any, app).config
    cast(Any, setup).confdir = cast(Any, app).confdir

    app.add_directive("manim", ManimDirective)

    app.connect("builder-inited", _delete_rendering_times)
    app.connect("build-finished", _log_rendering_times)

    metadata = {"parallel_read_safe": False, "parallel_write_safe": True}
    return metadata


#: Jinja template for rendering a Manim example block.
TEMPLATE = r"""
{% if not hide_source %}
.. raw:: html

    <div id="{{ clsname_lowercase }}" class="admonition admonition-manim-example">
    <p class="admonition-title">Example: {{ clsname }} <a class="headerlink" href="#{{ clsname_lowercase }}">¶</a></p>

{% endif %}

{% if not (save_as_gif or save_last_frame) %}
.. raw:: html

    <video
        class="manim-video"
        controls
        loop
        {{ '' if no_autoplay else 'autoplay' }}
        src="./{{ output_file }}.mp4">
    </video>

{% elif save_as_gif %}
.. image:: /{{ filesrc_rel }}
    :align: center

{% elif save_last_frame %}
.. image:: /{{ filesrc_rel }}
    :align: center

{% endif %}
{% if not hide_source %}
{{ source_block }}

{{ ref_block }}

.. raw:: html

    </div>

{% endif %}
"""
