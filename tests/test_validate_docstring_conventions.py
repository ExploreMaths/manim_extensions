# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the strict docstring spacing and return-annotation rules."""

import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(WORKFLOW))
sys.path.insert(0, str(SCRIPTS))

import check_return_annotations as returns  # noqa: E402
import validate_doc_sections as sections  # noqa: E402


def test_section_requires_exactly_one_blank_line() -> None:
    """Two blank lines before a section header are rejected."""
    doc = "Summary.\n\n\nParameters\n----------\nvalue\n    The value.\n"
    violations: list = []
    sections.check_section_spacing(doc, "demo", 1, violations)
    assert [v["type"] for v in violations] == ["SECTION_EXTRA_BLANK_BEFORE"]


def test_section_with_one_blank_line_passes() -> None:
    """A single blank line before a section header is accepted."""
    doc = "Summary.\n\nParameters\n----------\nvalue\n    The value.\n"
    violations: list = []
    sections.check_section_spacing(doc, "demo", 1, violations)
    assert violations == []


def test_section_header_must_align_with_summary() -> None:
    """An over-indented section header is rejected."""
    doc = (
        "Summary.\n\n"
        "        Parameters\n"
        "        ----------\n"
        "        value\n"
        "            The value.\n"
    )
    violations: list = []
    sections.check_section_spacing(doc, "demo", 1, violations)
    assert [v["type"] for v in violations] == ["SECTION_INDENTED"]


def test_returns_body_indented_eight_spaces_is_rejected() -> None:
    """An over-indented Returns description is reported."""
    doc = "Summary.\n\nReturns\n-------\n        The result.\n"
    violations: list = []
    sections.check_return_body_indent(doc, "demo", 1, violations)
    assert [v["type"] for v in violations] == ["RETURNS_BODY_OVER_INDENTED"]


def test_returns_body_indented_four_spaces_passes() -> None:
    """A Returns description four spaces below the header is accepted."""
    doc = "Summary.\n\nReturns\n-------\n    The result.\n"
    violations: list = []
    sections.check_return_body_indent(doc, "demo", 1, violations)
    assert violations == []


def test_bare_any_return_with_value_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """A value-returning function may not use a bare Any return type."""
    (tmp_path / "demo.py").write_text(
        "def value() -> Any:\n    return 1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(returns, "PACKAGE", tmp_path)
    assert returns.main() == 1


def test_bare_any_without_value_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """A side-effect function may not use Any instead of None."""
    (tmp_path / "demo.py").write_text(
        "def side_effect() -> Any:\n    print('x')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(returns, "PACKAGE", tmp_path)
    assert returns.main() == 1


def test_precise_return_annotations_pass(tmp_path: Path, monkeypatch) -> None:
    """Concrete return types and None are accepted."""
    (tmp_path / "demo.py").write_text(
        "def value() -> int:\n    return 1\n\n"
        "def side_effect() -> None:\n    print('x')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(returns, "PACKAGE", tmp_path)
    assert returns.main() == 0
