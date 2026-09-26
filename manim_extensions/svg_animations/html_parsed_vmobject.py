# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazily import the manim-mobject-svg plugin and svgpathtools (svg extra)
"""HTML parsed SVG vmobjects for Manim.

This module provides functionality to parse SVG files and create
animated Manim objects from them.

"""

from manim import (
    DOWN,
    MovingCameraScene,
    RIGHT,
    Scene,
    UL,
    VMobject,
    ValueTracker,
    color_to_int_rgba,
)
from manim.camera.camera import Camera
from manim.camera.moving_camera import MovingCamera
import itertools
import os
from types import ModuleType
from typing import cast

import numpy as np
from numpy.typing import NDArray

from ..utils.deps import require


HTML_STRUCTURE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%s</title>
</head>
<body>
    <svg id="%s" width="%s" viewBox="0 0 %d %d" style="background-color:%s;"></svg>
    %s
    <script src="%s"></script>
</body>
</html>"""


BASIC_HTML_STRUCTURE = """<div>
    <svg id="%s" width="%s" viewBox="0 0 %d %d" style="background-color:%s;"></svg>
</div>"""


JAVASCRIPT_STRUCTURE = """var rendered = false;
var ready = true;
var timeouts = [];
var %s = document.getElementById("%s");
function render%s() {
    if (!ready) {
        for (var i=0; i<timeouts.length; i++) {
            clearTimeout(timeouts[i]);
        }
        while(timeouts.length > 0) {
            timeouts.pop();
        }
    }
    ready = false;
    rendered = false;
%s
    setTimeout(function() {
        ready = true;
        rendered = true;
    }, %f)
}"""


JAVASCRIPT_UPDATE_STRUCTURE = """    timeouts.push(setTimeout(function() {
        %s.replaceChildren();
        %s
    }, %f))"""


JAVASCRIPT_INTERACTIVE_STRUCTURE = r"""var combsDict = {%s};
var comb = [%s];
function update(i, val) {
if (!rendered) {
    return
}
var keys = Object.keys(combsDict);
var ithElements = [];
for (let arr of keys) {
    if (Array.isArray(arr[i])) {   
        ithElements.push(arr[i]);
    }
    else {
        ithElements.push(arr);
    }
}
var x = val;
var closest = ithElements.sort( (a, b) => Math.abs(x - a) - Math.abs(x - b))[0];
comb[i] = closest;
combsDict[comb]();
}
"""


def _ensure_to_svg_plugin() -> None:
    """Import the manim-mobject-svg plugin, which registers VMobject.to_svg().

    The import is done lazily so that :mod:`manim_extensions.svg_animations`
    remains importable without the plugin installed.
    """
    try:
        import manim_mobject_svg  # noqa: F401 (side effect: registers to_svg)
    except ImportError as exc:
        raise ImportError(
            "HTMLParsedVMobject requires the manim-mobject-svg plugin "
            "(it provides VMobject.to_svg()). Install it with "
            "`pip install manim-mobject-svg`; on Python 3.13+ use "
            "`pip install --ignore-requires-python manim-mobject-svg`."
        ) from exc


class HTMLParsedVMobject:
    """Wrap a VMobject and stream its rendered SVG into an HTML page.

    While the scene runs, the vmobject is continuously exported to an SVG
    file and the corresponding JavaScript/SVG updates are injected into a
    generated HTML page, so the object can be viewed and interacted with in
    a web browser.

    Parameters
    ----------
    vmobject : VMobject
        The Manim object to export and animate in the HTML output.
    scene : Scene
        The scene in which ``vmobject`` lives. Its camera state and
        background color are used for the HTML output, and the per-frame
        updater is registered on it.
    width : str, optional
        Width of the embedded SVG element, e.g. ``"500px"``.
        Defaults to ``"500px"``.
    basic_html : bool, optional
        If ``True``, generate a minimal HTML wrapper without the full page
        structure and script tag. Defaults to ``False``.

    Examples
    --------
    Render the scene with the ``--disable_caching`` flag. Besides the MP4,
    an HTML and a JS file are written next to the scene file; open the HTML
    file in a browser and call ``renderHTMLParsedVMobjectDocExample()`` from
    the developer console to see the SVG animation.

    .. manim:: HTMLParsedVMobjectDocExample

       from manim import *
       from manim_extensions.svg_animations import HTMLParsedVMobject

       VMobject.set_default(color=BLACK)

       class HTMLParsedVMobjectDocExample(Scene):
           def construct(self):
               self.camera.background_color = WHITE
               ax = Axes().add_coordinates()
               labels = ax.get_axis_labels("x", "y")
               vg = VGroup(ax, labels)
               parsed = HTMLParsedVMobject(vg, self)
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
               self.play(dx.animate.set_value(0.1))
               self.wait()
               riemann.clear_updaters()
               self.play(FadeOut(vg))
               parsed.finish()
    """

    def __init__(self, vmobject: VMobject, scene: Scene, width: str = "500px", basic_html: bool = False) -> None:
        """Initialize the exporter and write the initial HTML page."""
        self.vmobject = vmobject
        self.scene = scene
        self.filename_base = scene.__class__.__name__
        self.html_filename = self.filename_base + ".html"
        self.js_filename = self.filename_base + ".js"
        self.current_index = 0
        self.final_html_body = ""
        self.width = width
        self.basic_html = basic_html
        self.update_html()
        self.js_updates = ""
        self.continue_updating = True
        camera = cast(Camera, self.scene.camera)
        self.original_frame_width = camera.frame_width
        self.original_frame_height = camera.frame_height
        _ensure_to_svg_plugin()
        self.scene.add_updater(self.updater)
    
    def updater(self, dt: float) -> None:
        """Export the vmobject to an SVG frame and append the JS update.

        Called once per rendered frame through the scene updater registered
        in ``__init__``: serializes ``self.vmobject`` via ``to_svg()``,
        converts the resulting path attributes into JavaScript DOM update
        statements and appends them to ``self.js_updates``.

        Parameters
        ----------
        dt : float
            Elapsed time since the previous frame, in seconds.
        """
        if self.continue_updating is False:
            return
        svg2paths = cast(ModuleType, require("svg", "svgpathtools")).svg2paths
        svg_filename = self.filename_base + str(self.current_index) + ".svg"
        self.vmobject.to_svg(svg_filename)
        html_el_creations = ""
        _, attributes = svg2paths(svg_filename)
        i = 0
        for attr in attributes:
            html_el_creation = f"        var el{i} = document.createElementNS('http://www.w3.org/2000/svg', 'path');\n"            
            for k, v in attr.items():
                html_el_creation += f"       el{i}.setAttribute('{k}', '{v}');\n"
            html_el_creation += f"       {self.filename_base.lower()}.appendChild(el{i});\n"
            html_el_creations += html_el_creation
            i += 1
        camera = cast(Camera, self.scene.camera)
        background_color = color_to_int_rgba(camera.background_color, camera.background_opacity)
        background_color[-1] = background_color[-1] / 255
        background_color_str = [str(par) for par in background_color]
        html_el_creations += f"     {self.filename_base.lower()}.style.backgroundColor = 'rgb({', '.join(background_color_str)})';\n"
        if isinstance(self.scene, MovingCameraScene):
            moving_camera = cast(MovingCamera, self.scene.camera)
            frame = moving_camera.frame
            pixel_width = moving_camera.pixel_width * moving_camera.frame_width / self.original_frame_width
            pixel_height = moving_camera.pixel_height * moving_camera.frame_height / self.original_frame_height
            frame_center = frame.get_corner(UL)
            pixel_center = frame_center * moving_camera.pixel_width / self.original_frame_width
            pixel_center += moving_camera.pixel_width / 2 * RIGHT + moving_camera.pixel_height / 2 * DOWN
            pixel_center[1] = -pixel_center[1]
            pixel_center = pixel_center[:2]
            arr = [*pixel_center, pixel_width, pixel_height]
            arr = [str(p) for p in arr]
            html_el_creations += f"     {self.filename_base.lower()}.setAttribute('viewBox', '{' '.join(arr)}');\n"
        self.js_updates += JAVASCRIPT_UPDATE_STRUCTURE % (
            self.filename_base.lower(),
            html_el_creations,
            1000 * self.scene.renderer.time
        )
        self.js_updates += "\n"
        self.current_index += 1
        os.remove(svg_filename)
    
    def update_html(self) -> None:
        """Rewrite the HTML page with the current frame and time.

        Called on every scene update; embeds the current SVG frame and
        renderer time into the HTML/JS output.
        """
        camera = cast(Camera, self.scene.camera)
        bg_color = color_to_int_rgba(
            camera.background_color,
            camera.background_opacity
        )
        bg_color[-1] = bg_color[-1] / 255
        bg_color_str = [str(c) for c in bg_color]
        bg_color_css = f"rgb({', '.join(bg_color_str)})"
        if self.basic_html is False:
            self.html = HTML_STRUCTURE % (
                self.filename_base,
                self.filename_base,
                self.width,
                camera.pixel_width,
                camera.pixel_height,
                bg_color_css,
                self.final_html_body,
                self.js_filename
            )
        else:
            self.html = BASIC_HTML_STRUCTURE % (
                self.filename_base,
                self.width,
                camera.pixel_width,
                camera.pixel_height,
                bg_color_css
            )
    
    def finish(self) -> None:
        """Stop the updater and write the final HTML and JS files.

        Removes the scene updater and flushes the accumulated
        JavaScript updates to ``<scene_name>.js`` and the final page to
        ``<scene_name>.html``.
        """
        self.scene.remove_updater(self.updater)
        self.js_updates.removesuffix("\n")
        if not hasattr(self, "last_t"):
            self.last_t = self.scene.renderer.time
        js_content = JAVASCRIPT_STRUCTURE % (
            self.filename_base.lower(),
            self.filename_base,
            self.filename_base,
            self.js_updates,
            1000 * self.last_t
        )
        if hasattr(self, "interactive_js"):
            js_content += f"\n{self.interactive_js}"
        with open(self.js_filename, "w") as f:
            f.write(js_content)
        with open(self.html_filename, "w") as f:
            f.write(self.html)
    
    def start_interactive(
        self,
        value_trackers: list[ValueTracker],
        linspaces: list[NDArray[np.float64]],
        animate_this: bool = True
    ) -> None:
        """Precompute the interactive JavaScript state for value combinations.

        Iterates over the cartesian product of ``linspaces``, sets each
        combination on ``value_trackers``, exports the vmobject once per
        combination and records the resulting JavaScript DOM updates, so
        the generated HTML page can switch between the states interactively.

        Parameters
        ----------
        value_trackers : list of ValueTracker
            Value trackers, swept through every combination of
            ``linspaces``.
        linspaces : list of numpy.ndarray
            Arrays of values to sweep, one per entry of ``value_trackers``.
            Their cartesian product is enumerated.
        animate_this : bool, optional
            If ``False``, stop the per-frame updater before sweeping and
            record the current scene time as ``self.last_t``.
            Defaults to ``True``.
        """
        svg2paths = cast(ModuleType, require("svg", "svgpathtools")).svg2paths
        if animate_this is False:
            self.continue_updating = False
            self.last_t = self.scene.renderer.time
        print("This process can be slow, please wait!")
        self.interactive_js = ""
        filename = "update.svg"
        combs = itertools.product(*linspaces)
        combs_dict = ""
        comb_now = ", ".join([str(v.get_value()) for v in value_trackers])
        camera = cast(Camera, self.scene.camera)
        for comb in combs:
            for vt, val in zip(value_trackers, comb):
                self.scene.wait(1/camera.frame_rate)
                vt.set_value(val)
            self.vmobject.to_svg(filename)
            html_el_creations = f"{self.filename_base.lower()}.replaceChildren();\n"
            _, attributes = svg2paths(filename)
            i = 0
            for attr in attributes:
                html_el_creation = f"        var el{i} = document.createElementNS('http://www.w3.org/2000/svg', 'path');\n"            
                for k, v in attr.items():
                    html_el_creation += f"       el{i}.setAttribute('{k}', '{v}');\n"
                html_el_creation += f"       {self.filename_base.lower()}.appendChild(el{i});\n"
                html_el_creations += html_el_creation
                i += 1
            
            combs_dict += "[" + ", ".join([str(v) for v in comb]) + """]: () => {
                %s
            },
            """ % html_el_creations
        self.interactive_js += JAVASCRIPT_INTERACTIVE_STRUCTURE % (combs_dict, comb_now)
        os.remove(filename)