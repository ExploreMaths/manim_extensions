import os
from pathlib import Path

import pytest

from manim_extensions.tikz.tikz import Tikz
from manim_extensions.tikz.template import TikzTemplate


@pytest.fixture
def tikz_code():
    return "\\begin{tikzpicture} \\draw (0,0) -- (1,1); \\end{tikzpicture}"


class TestTikzTemplate:
    def test_init_defaults(self):
        template = TikzTemplate()
        assert template is not None
        assert template.tex_compiler == "latex"
        assert template.documentclass == "\\documentclass[preview, tikz]{standalone}"

    def test_init_with_packages(self):
        template = TikzTemplate(packages=["amsmath", "amssymb"])
        preamble = template.preamble
        assert "\\usepackage{amsmath, amssymb}" in preamble

    def test_init_with_libraries(self):
        template = TikzTemplate(libraries=["arrows.meta", "positioning"])
        preamble = template.preamble
        assert "\\usetikzlibrary{arrows.meta, positioning}" in preamble

    def test_init_with_tikzset(self):
        template = TikzTemplate(tikzset=["mystyle/.style={draw=red}"])
        preamble = template.preamble
        assert "\\tikzset{" in preamble

    def test_init_with_preamble(self):
        template = TikzTemplate(preamble="\\usepackage{tikz-cd}")
        preamble = template.preamble
        assert "\\usepackage{tikz-cd}" in preamble

    def test_init_use_pdf(self):
        template = TikzTemplate(use_pdf=True)
        assert template.output_format == ".pdf"

    def test_init_use_dvi(self):
        template = TikzTemplate(use_pdf=False)
        assert template.output_format == ".dvi"

    def test_default_preamble_contains_tikz(self):
        template = TikzTemplate()
        assert "tikz" in template.preamble.lower()

    def test_combined_preamble(self):
        template = TikzTemplate(
            packages=["amsmath"],
            libraries=["arrows"],
            tikzset=["style1/.style={red}"],
            preamble="\\customcommand",
        )
        preamble = template.preamble
        assert "\\usepackage{amsmath}" in preamble
        assert "\\usetikzlibrary{arrows}" in preamble
        assert "\\tikzset{" in preamble
        assert "\\customcommand" in preamble


class TestTikz:
    def test_init(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        assert tikz is not None
        assert hasattr(tikz, "convert")

    def test_convert_returns_path(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(tikz_code)
        assert isinstance(result, (str, Path))
        assert len(str(result)) > 0

    def test_convert_with_packages(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(tikz_code, packages=["amsmath"])
        assert isinstance(result, (str, Path))

    def test_convert_with_libraries(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(tikz_code, libraries=["arrows.meta"])
        assert isinstance(result, (str, Path))

    def test_convert_with_tikzset(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(
            tikz_code, tikzset=["mystyle/.style={draw=red}"]
        )
        assert isinstance(result, (str, Path))

    def test_convert_with_preamble(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(
            tikz_code, preamble="\\usepackage{tikz-cd}"
        )
        assert isinstance(result, (str, Path))

    def test_convert_with_use_pdf(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(tikz_code, use_pdf=True)
        assert isinstance(result, (str, Path))

    def test_convert_simple_circle(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(
            "\\begin{tikzpicture} \\draw (0,0) circle (1); \\end{tikzpicture}"
        )
        assert isinstance(result, (str, Path))

    def test_svg_file_generated(self, tikz_code):
        tikz = Tikz(code=tikz_code)
        result = tikz.convert(tikz_code)
        assert os.path.exists(str(result))
        assert str(result).endswith(".svg")