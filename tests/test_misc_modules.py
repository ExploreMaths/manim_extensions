# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the remaining small public modules."""



from manim import *
class TestQrCodes:
    def test_qr_code_builds_vgroup(self):
        from manim_extensions.qr_codes import qr_code

        code = qr_code("https://example.com")
        assert isinstance(code, VGroup)
        assert len(code) > 0

    def test_qr_code_circle_shape(self):
        from manim_extensions.qr_codes import qr_code

        code = qr_code("hello", data_shape="circles")
        assert len(code) > 0


class TestSvgAnimations:
    def test_html_parsed_vmobject(self, tmp_path):
        from manim_extensions.svg_animations import HTMLParsedVMobject

        scene = Scene()
        mob = HTMLParsedVMobject(Square(), scene, width="200px")
        assert mob is not None


class TestArabic:
    def test_template_preamble_uses_fontspec(self):
        from manim_extensions.arabic import create_arabic_template

        template = create_arabic_template("Amiri")
        preamble = template.body
        assert "fontspec" in preamble
        assert "Amiri" in preamble

    def test_default_template(self):
        from manim_extensions.arabic import create_arabic_template

        template = create_arabic_template()
        assert template.body is not None


class TestWeightedLine:
    def test_construct_with_weight(self):
        from manim_extensions.weighted_line import WeightedLine

        line = WeightedLine([-1, 0, 0], [1, 0, 0], weight="3")
        assert line is not None

    def test_construct_numeric_weight(self):
        from manim_extensions.weighted_line import WeightedLine

        line = WeightedLine([-1, 0, 0], [1, 0, 0], weight=2.5, add_bg=False)
        assert line is not None

    def test_construct_with_mobjects(self):
        from manim_extensions.weighted_line import WeightedLine

        a = Circle().shift(LEFT)
        b = Square().shift(RIGHT)
        line = WeightedLine(a, b, weight="w")
        assert line is not None


class TestFontawesome:
    def test_namespaces_exposed(self):
        from manim_extensions.fontawesome import (
            FONT_AWESOME_VERSION,
            brand,
            regular,
            solid,
        )

        assert isinstance(FONT_AWESOME_VERSION, str)
        assert brand is not None
        assert regular is not None
        assert solid is not None

    def test_icon_lookup_returns_svgmobject(self):
        from manim_extensions.fontawesome import solid

        # Icons are exposed as attributes, e.g. ``solid.rocket``.
        icon = solid.rocket
        assert isinstance(icon, SVGMobject)
