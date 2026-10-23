.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

SVG Animations
==============

.. vendored-status:: MathItYT/manim-svg-animations

**Original author:** `MathLike <https://github.com/MathItYT>`_

**Source repository:** `GitHub <https://github.com/MathItYT/manim-svg-animations>`_

**License:** MIT

``manim-svg-animations`` exports Manim scenes as interactive HTML + SVG +
JavaScript animations. It converts each frame's mobjects to SVG paths and
generates an HTML file with JavaScript that replays the animation in a
browser. It is a plugin for Manim Community Edition that renders SVG
animations directly from Python.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.svg_animations`` subpackage.

.. note::

   This module requires the ``manim-mobject-svg`` plugin (it provides
   :attr:`~manim.mobject.types.vectorized_mobject.VMobject.to_svg()`). On Python 3.13+ install it with
   ``pip install --ignore-requires-python manim-mobject-svg``.

Features
--------

- :class:`~manim_extensions.svg_animations.html_parsed_vmobject.HTMLParsedVMobject`
  – converts a :class:`~manim.mobject.types.vectorized_mobject.VMobject` into an SVG-based HTML animation. Attaches to a
  scene as an updater, writes per-frame SVG paths, and produces a finished
  ``.html`` + ``.js`` pair on ``finish()``.
- Streams every frame's mobjects to SVG paths while the scene plays, so the
  animation replays in a browser with no video codec.
- New mobjects introduced later in the scene can be added to the tracked
  group at any time and are picked up automatically.
- Experimental interactive mode that precomputes states for a set of
  :class:`~manim.mobject.value_tracker.ValueTracker` parameters, letting a
  browser script drive the animation.

Usage
-----

Import Manim and the exporter. Build the scene as usual — set
``self.camera.background_color = WHITE`` for a white background. Collect
every :class:`~manim.mobject.types.vectorized_mobject.VMobject` of the first
animation into a :class:`~manim.mobject.types.vectorized_mobject.VGroup`
(here ``vg``), and create the
:class:`~manim_extensions.svg_animations.html_parsed_vmobject.HTMLParsedVMobject`
with ``HTMLParsedVMobject(vg, self)`` *before* playing the first animation.
When later animations introduce more mobjects, just add them to ``vg``. Call
:meth:`~manim_extensions.svg_animations.html_parsed_vmobject.HTMLParsedVMobject.finish`
once the animations are done.

.. code-block:: python

   from manim import *
   from manim_extensions.svg_animations import HTMLParsedVMobject


   VMobject.set_default(color=BLACK)


   class SceneExample(Scene):
       def construct(self):
           self.camera.background_color = WHITE
           ax = Axes().add_coordinates()
           labels = ax.get_axis_labels("x", "y")
           vg = VGroup(ax, labels)
           parsed = HTMLParsedVMobject(vg, self)
           self.play(Write(VGroup(ax, labels)))
           graph = ax.plot(
               np.log,
               x_range=[np.exp(-4), 7],
               color=RED
           )
           vg.add(graph)
           self.play(Create(graph))
           riemann = ax.get_riemann_rectangles(
               graph,
               x_range=[1, 6],
               dx=1
           )
           vg.add(riemann)
           self.play(Write(riemann))
           dx = ValueTracker(1)
           riemann.add_updater(
               lambda m: m.become(ax.get_riemann_rectangles(
                   graph,
                   x_range=[1, 6],
                   dx=dx.get_value()
               ))
           )
           self.play(dx.animate.set_value(0.1))
           self.wait()
           riemann.clear_updaters()
           self.play(FadeOut(vg))
           banner = ManimBanner(dark_theme=False)
           vg.remove(*vg)
           vg.add(banner)
           self.play(banner.create())
           self.play(banner.expand())
           parsed.finish()

Render the scene with the ``manim`` command, adding the
``--disable_caching`` flag — this is important. Besides the MP4 in the
media folder, an ``.html`` and a ``.js`` file are written next to the scene
file. Open the HTML file in a browser, open the developer tools console and
call ``renderSceneExample()`` (replace ``SceneExample`` with your scene's
name) to play the SVG animation.

Interactive animation
^^^^^^^^^^^^^^^^^^^^^

Interactive SVG animations are an experimental feature and may be slow; use
at your own risk. Call
:meth:`~manim_extensions.svg_animations.html_parsed_vmobject.HTMLParsedVMobject.start_interactive`
on the exporter. Its first argument is a list of
:class:`~manim.mobject.value_tracker.ValueTracker` objects whose values you
want to manipulate, and its second is a list of NumPy ``linspace`` arrays,
one per tracker, giving the values that tracker can take. Add updaters to
the mobjects that should change when each parameter moves.

.. code-block:: python

   from manim import *
   from manim_extensions.svg_animations import HTMLParsedVMobject


   VMobject.set_default(color=BLACK)


   class SceneExample(Scene):
       def construct(self):
           self.camera.background_color = WHITE
           b = ManimBanner(dark_theme=False)
           vg = VGroup(b)
           parsed = HTMLParsedVMobject(vg, self)
           self.play(b.create())
           self.play(b.expand())
           self.play(FadeOut(b))
           vg.remove(b)
           ax = Axes().add_coordinates()
           labels = ax.get_axis_labels("x", "y")
           vg.add(ax, labels)
           self.play(Write(VGroup(ax, labels)))
           graph = ax.plot(np.log, x_range=[np.exp(-4), 7], color=RED)
           vg.add(graph)
           self.play(Create(graph))
           riemann = ax.get_riemann_rectangles(graph, x_range=[1, 6], dx=1)
           vg.add(riemann)
           self.play(Write(riemann))
           dx = ValueTracker(1)
           riemann.add_updater(
               lambda m: m.become(ax.get_riemann_rectangles(
                   graph, x_range=[1, 6], dx=dx.get_value()))
           )
           parsed.start_interactive([dx], [np.flip(np.linspace(0.1, 1, 100))])
           parsed.finish()

After the animation has played, call ``update(0, 0.5)`` in the console to
set the first parameter to ``0.5``, ``update(1, 1.2)`` for the second
parameter, and so on. No range slider is produced automatically, so add
one to the HTML yourself. The slider only takes effect after
``renderSceneExample()`` has been run at least once:

.. code-block:: html

   <input type="range" min="0.1" max="1.0" step="0.01" value="0.1"
          class="slider" oninput="update(0, this.value)">

Notes
^^^^^

This plugin is not meant to build a full website — it only produces the SVG
animations as HTML. To embed the animations in a website, include the
generated HTML and JS files in your own pages. If the size of the animation
does not look right, fix it with CSS.

.. toctree::
   :maxdepth: 1

   classes
   constants
