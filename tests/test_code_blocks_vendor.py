# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Smoke tests for the vendored ``manim-code-blocks-redux`` package."""

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from manim_extensions.code_blocks import OneDark, ProgrammingLanguage, Python

ROOT = Path(__file__).resolve().parent.parent


def test_python_language_metadata():
    assert Python.name == "Python"
    assert Python.color == "#3572A5"
    assert isinstance(Python, ProgrammingLanguage)


def test_theme_colour_lookup():
    token = SimpleNamespace(type="keyword")
    assert OneDark.color_for(token) == "#C678DD"


def test_import_does_not_open_a_network_connection():
    script = """
import urllib.request

def fail(*args, **kwargs):
    raise AssertionError("network access during import")

urllib.request.urlopen = fail
import manim_extensions.code_blocks
print("IMPORT OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, result.stderr
    assert "IMPORT OK" in result.stdout
