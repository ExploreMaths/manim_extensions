# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the arabic module."""

import shutil
import pytest
from manim import Tex, TexTemplate

from manim_extensions.arabic import ArabicTemplate, ArabicText
from manim_extensions.arabic.text import _resolve_arabic_font, _FONT_CANDIDATES

_HAS_XELATEX = shutil.which("xelatex") is not None


class TestResolveArabicFont:
    def test_explicit_font_passthrough(self):
        """_resolve_arabic_font should return the given font_name verbatim."""
        result = _resolve_arabic_font("CustomFont")
        assert result == "CustomFont"

    def test_none_falls_back_to_candidate(self):
        """_resolve_arabic_font(None) should return a candidate or default."""
        result = _resolve_arabic_font(None)
        assert isinstance(result, str)
        # Should be one of the known candidates
        assert result in _FONT_CANDIDATES


class TestCreateArabicTemplate:
    def test_returns_tex_template(self):
        """create_arabic_template should return a TexTemplate instance."""
        template = ArabicTemplate(font_name="Amiri")
        assert isinstance(template, TexTemplate)

    def test_xelatex_compiler(self):
        """create_arabic_template should configure xelatex as compiler."""
        template = ArabicTemplate(font_name="Amiri")
        assert template.tex_compiler == "xelatex"
        assert template.output_format == ".xdv"

    def test_custom_font_name(self):
        """create_arabic_template should use the provided font name."""
        template = ArabicTemplate(font_name="MyArabicFont")
        assert isinstance(template, TexTemplate)


@pytest.mark.skipif(not _HAS_XELATEX, reason="xelatex not installed")
class TestCreateArabicText:
    def test_basic_construction(self):
        """create_arabic_text should return a Tex object."""
        text = ArabicText("مرحبا", font_name="Amiri")
        assert isinstance(text, Tex)

    def test_custom_color(self):
        """create_arabic_text should accept custom color names."""
        text = ArabicText("سلام", color="arabicgreen", font_name="Amiri")
        assert isinstance(text, Tex)

    def test_custom_font_size(self):
        """create_arabic_text should accept custom font_size."""
        text = ArabicText("مرحبا", font_size=48, font_name="Amiri")
        assert isinstance(text, Tex)
