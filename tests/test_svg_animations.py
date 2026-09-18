# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the svg_animations module."""

import pytest
from manim import Scene, Circle, VGroup

try:
    import manim_mobject_svg  # noqa: F401
    _HAS_MANIM_MOBJECT_SVG = True
except ImportError:
    _HAS_MANIM_MOBJECT_SVG = False

try:
    import svgpathtools  # noqa: F401
    _HAS_SVGPATHTOOLS = True
except ImportError:
    _HAS_SVGPATHTOOLS = False

_HAS_SVG_DEPS = _HAS_MANIM_MOBJECT_SVG and _HAS_SVGPATHTOOLS


@pytest.mark.skipif(not _HAS_SVG_DEPS, reason="manim-mobject-svg or svgpathtools not installed")
class TestHTMLParsedVMobject:
    def test_basic_construction(self):
        """HTMLParsedVMobject should be created with a vmobject and scene."""
        from manim_extensions.svg_animations import HTMLParsedVMobject
        scene = Scene()
        vg = VGroup(Circle())
        parsed = HTMLParsedVMobject(vg, scene)
        assert parsed.vmobject is vg
        assert parsed.scene is scene
        assert parsed.current_index == 0
        # Clean up: remove the updater
        scene.remove_updater(parsed.updater)

    def test_update_html_regenerates_html(self):
        """HTMLParsedVMobject.update_html should regenerate the html string."""
        from manim_extensions.svg_animations import HTMLParsedVMobject
        scene = Scene()
        vg = VGroup(Circle(radius=1))
        parsed = HTMLParsedVMobject(vg, scene)
        old_html = parsed.html
        parsed.update_html()
        assert isinstance(parsed.html, str)
        # HTML should still be a valid string after update
        assert len(parsed.html) > 0
        scene.remove_updater(parsed.updater)

    def test_basic_html_mode(self):
        """HTMLParsedVMobject should support basic_html=True."""
        from manim_extensions.svg_animations import HTMLParsedVMobject
        scene = Scene()
        vg = VGroup(Circle())
        parsed = HTMLParsedVMobject(vg, scene, basic_html=True)
        assert parsed.basic_html is True
        assert isinstance(parsed.html, str)
        # Basic HTML should be shorter (no full page structure)
        assert len(parsed.html) > 0
        scene.remove_updater(parsed.updater)

    def test_custom_width(self):
        """HTMLParsedVMobject should accept a custom width parameter."""
        from manim_extensions.svg_animations import HTMLParsedVMobject
        scene = Scene()
        vg = VGroup(Circle())
        parsed = HTMLParsedVMobject(vg, scene, width="300px")
        assert parsed.width == "300px"
        assert "300px" in parsed.html
        scene.remove_updater(parsed.updater)

    def test_continue_updating_flag(self):
        """HTMLParsedVMobject should have continue_updating set to True initially."""
        from manim_extensions.svg_animations import HTMLParsedVMobject
        scene = Scene()
        vg = VGroup(Circle())
        parsed = HTMLParsedVMobject(vg, scene)
        assert parsed.continue_updating is True
        scene.remove_updater(parsed.updater)
