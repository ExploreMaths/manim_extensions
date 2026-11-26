# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for module-docstring and automodule page rules."""

import sys
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

pytest.importorskip("docutils")

import validate_docstrings as docstrings  # noqa: E402
import validate_rst as rst  # noqa: E402


def test_module_docstring_rejects_code(tmp_path: Path) -> None:
    """A module docstring containing an example snippet is rejected."""
    path = tmp_path / "module.py"
    path.write_text(
        '"""Description.\n\nExample::\n\n    from manim import *\n"""\n',
        encoding="utf-8",
    )
    hits = docstrings.check_module_examples(path)
    assert hits and hits[0][1] == "code example"


def test_module_docstring_allows_prose(tmp_path: Path) -> None:
    """A description without a code block is accepted."""
    path = tmp_path / "module.py"
    path.write_text('"""Description only."""\n', encoding="utf-8")
    assert docstrings.check_module_examples(path) == []


def test_automodule_without_members_passes() -> None:
    """A module page that only renders the docstring is accepted."""
    lines = [".. automodule:: manim_extensions.radar"]
    assert rst.check_automodule_options(lines) == []


def test_automodule_with_members_fails() -> None:
    """A module page that requests members is reported."""
    lines = [
        ".. automodule:: manim_extensions.radar",
        "   :members:",
    ]
    issues = rst.check_automodule_options(lines)
    assert issues and issues[0][0] == 2


def test_recursive_type_alias_block_fails() -> None:
    """A package-level recursive alias block repeats submodule aliases."""
    lines = [
        ".. autoall:: manim_extensions.radar",
        "   :recursive:",
        "   :types: typealias",
    ]
    issues = rst.check_reference_page_layout(lines)
    assert issues and issues[0][0] == 1


def test_module_type_alias_block_passes() -> None:
    """A non-recursive alias block stays on its defining module page."""
    lines = [
        ".. autoall:: manim_extensions.radar.chart",
        "   :types: typealias",
    ]
    assert rst.check_reference_page_layout(lines) == []


def test_inline_autoclass_next_to_autosummary_fails() -> None:
    """A class may not be rendered both in a table and inline."""
    lines = [
        ".. autosummary::",
        "   ~RadarChart",
        "   ~Series",
        "",
        ".. autoclass:: manim_extensions.radar.chart.Series",
    ]
    issues = rst.check_reference_page_layout(lines)
    assert issues and issues[0][0] == 5
