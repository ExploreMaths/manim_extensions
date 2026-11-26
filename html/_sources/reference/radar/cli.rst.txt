.. SPDX-FileCopyrightText: 2026 FTZ-OPUS
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

cli
===

.. automodule:: manim_extensions.radar.cli

``manim-radar`` is the installed console entry point for the radar
subpackage. It is meant for the small jobs that happen before a scene
exists: inspecting the available themes and styles, writing a starter
scene, and locating or rendering the bundled demo. Once a scene file has
been generated, the normal ``manim`` command takes over.

The command is registered by the package installation, so it is available
from any directory:

.. code-block:: console

   $ pip install manim_extensions
   $ manim-radar --version

Command overview
----------------

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Command
     - What it does
   * - ``manim-radar``
     - Print the short usage summary.
   * - ``manim-radar --version``
     - Print the installed ``manim_extensions`` version.
   * - ``manim-radar themes``
     - List the colour themes understood by :class:`~manim_extensions.radar.chart.RadarChart`.
   * - ``manim-radar styles``
     - List the style presets and their geometry.
   * - ``manim-radar template OUTPUT``
     - Write a complete starter scene to ``OUTPUT``.
   * - ``manim-radar demo``
     - Print the bundled demo scene and the command that renders it.
   * - ``manim-radar demo --render``
     - Render the bundled :class:`~manim_extensions.radar.legacy.RadarV2Scene` with Manim.

Quick start
-----------

Check the installed version, then list the two configuration surfaces:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-radar --version

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-radar themes

The theme list is intentionally short because each entry is a complete
background-and-grid palette:

.. code-block:: text

   midnight  bg=#070B16  grid=#8B9BB8
   aurora    bg=#04121A  grid=#7FB2AE
   ember     bg=#140806  grid=#D8A48F
   violet    bg=#0B0716  grid=#A79BC8
   paper     bg=#F7F5F0  grid=#5B6472

Styles control the geometry rather than the colours. ``manim-radar styles``
prints the radius, the number of levels, and the optional decorations for
each preset:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-radar styles

The three presets are:

.. list-table::
   :header-rows: 1
   :widths: 20 18 18 44

   * - Style
     - Radius
     - Levels
     - Decorations
   * - ``neo``
     - 2.9
     - 5
     - rainbow outline, vertex dots, sweep beam
   * - ``classic``
     - 3.2
     - 5
     - snap-in numbers
   * - ``minimal``
     - 2.5
     - 4
     - vertex dots

Create a starter scene
----------------------

``template`` writes a self-contained scene rather than printing code to
the terminal. Pass the output path first; the default is ``my_radar.py``.
The generated scene uses three snapshots, six axes, and
:class:`~manim_extensions.radar.reel.RadarReel`, so it can be rendered
immediately:

.. code-block:: console

   $ manim-radar template my_chart.py --style classic --theme paper

It prints the file that was written and the exact Manim command to render
it::

    wrote my_chart.py
    render it with:  manim -qh my_chart.py MyRadar

The important part of the generated file looks like this:

.. code-block:: python

   from manim import *
   from manim_extensions.radar import RadarChart, RadarData, RadarReel, set_scene_background

   AXES = ["Speed", "Power", "Range", "Comfort", "Price", "Safety"]
   SNAPSHOTS = [
       RadarData(axes=AXES, values=[8, 6, 7, 9, 5, 8], name="Model A", color="#17B8BA"),
       RadarData(axes=AXES, values=[6, 9, 5, 7, 8, 9], name="Model B", color="#E868C8"),
       RadarData(axes=AXES, values=[9, 9, 8, 9, 9, 9], name="Model C", color="#FFD166"),
   ]

   class MyRadar(Scene):
       def construct(self):
           set_scene_background("paper")
           chart = RadarChart(
               SNAPSHOTS[0],
               style="classic",
               theme="paper",
               title="Six axes",
           )
           RadarReel(chart, SNAPSHOTS, hold=0.6, backdrop=True).play_on(self)

The template accepts these options:

.. list-table::
   :header-rows: 1
   :widths: 24 20 56

   * - Option
     - Default
     - Purpose
   * - ``OUTPUT``
     - ``my_radar.py``
     - File to create. The parent directory must already exist.
   * - ``--style``
     - ``neo``
     - One of ``neo``, ``classic`` or ``minimal``.
   * - ``--theme``
     - ``midnight``
     - One of the themes printed by ``manim-radar themes``.
   * - ``--force``
     - off
     - Overwrite an existing file instead of refusing.

``template`` deliberately refuses to overwrite an existing file. This
protects a scene that has already been edited, and makes the command safe
to run in a directory that already contains ``my_radar.py``. Pass
``--force`` when replacing the file is intended.

Render the generated scene
--------------------------

``template`` does not render anything; it prints the command to use. For
a quick preview:

.. code-block:: console

   $ manim -ql my_chart.py MyRadar

For a final-quality render, raise the quality flag:

.. code-block:: console

   $ manim -qh my_chart.py MyRadar

The class name must match the scene class in the file. ``template`` names
it ``MyRadar``; renaming the class means renaming the argument as well.

Bundled demo
------------

The subpackage ships the older :class:`~manim_extensions.radar.legacy.RadarV2Scene` demo. Without
``--render`` the command only reports where the scene lives and how to
render it:

.. nbcell::
   :language: console
   :prompt-in: "$"

   manim-radar demo

Add ``--render`` to render it immediately. The default is low quality,
which is suitable for checking that the camera and backdrop work:

.. code-block:: console

   $ manim-radar demo --render

``-q`` / ``--quality`` selects the Manim quality preset:

.. list-table::
   :header-rows: 1
   :widths: 24 34 42

   * - Flag
     - Manim quality
     - Use it for
   * - ``-ql``
     - ``low_quality``
     - Fast smoke tests (the default).
   * - ``-qm``
     - ``medium_quality``
     - A quick preview with readable labels.
   * - ``-qh``
     - ``high_quality``
     - A normal presentation render.
   * - ``-qk``
     - ``production_quality``
     - Archive-quality output.
   * - ``-qp``
     - ``fourk_quality``
     - 4K output; the slowest option.

For example:

.. code-block:: console

   $ manim-radar demo --render -qh

The demo command renders through ``tempconfig``, so it does not write a
Manim config file and does not change the quality of later commands.

Error handling
--------------

``manim-radar`` uses explicit exit codes so it can be called from a
script:

.. list-table::
   :header-rows: 1
   :widths: 48 52

   * - Situation
     - Result
   * - ``template`` target exists without ``--force``
     - Prints a refusal to stderr and returns exit status 1.
   * - Unknown ``--quality`` flag
     - Prints the accepted flags to stderr and returns exit status 1.
   * - Unknown subcommand or malformed option
     - argparse prints usage and returns exit code 2.
   * - No subcommand
     - Prints the short usage summary and returns exit code 0.

API reference
-------------

Functions
~~~~~~~~~

.. autoall:: manim_extensions.radar.cli
   :types: function

Constants
~~~~~~~~~

.. autoall:: manim_extensions.radar.cli
   :types: data
