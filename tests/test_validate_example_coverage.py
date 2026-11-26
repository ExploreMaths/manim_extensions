# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for ``workflow/validate_example_coverage.py``."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

import validate_example_coverage as coverage  # noqa: E402


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the checker at a temporary project root."""
    monkeypatch.setattr(coverage, "ROOT", tmp_path)
    return tmp_path


def _scan(root: Path, source: str) -> list[str]:
    path = root / "sample.py"
    path.write_text(source, encoding="utf-8")
    return coverage.scan(path)


def test_visual_function_with_example(project_root: Path) -> None:
    source = '''
def example() -> "Circle":
    """Return a circle.

    Examples
    --------
    .. manim:: CircleExample
       :save_last_frame:
    """
'''
    assert _scan(project_root, source) == []


def test_visual_function_without_example(project_root: Path) -> None:
    violations = _scan(project_root, 'def example() -> "Circle":\n    pass\n')
    assert len(violations) == 1
    assert "`example`" in violations[0]


def test_class_example_does_not_implicitly_cover_method(
    project_root: Path,
) -> None:
    source = '''
class Widget:
    """A widget.

    Examples
    --------
    .. manim:: WidgetExample
    """

    def build(self) -> "VGroup":
        pass
'''
    violations = _scan(project_root, source)
    assert len(violations) == 1
    assert "`Widget.build`" in violations[0]


def test_method_explicitly_covered_by_class(project_root: Path) -> None:
    source = '''
class Widget:
    """A widget.

    .. doc-example-covers: build

    Examples
    --------
    .. manim:: WidgetExample
    """

    def build(self) -> "VGroup":
        pass
'''
    assert _scan(project_root, source) == []


def test_method_without_any_example(project_root: Path) -> None:
    source = '''
class Widget:
    """A widget."""

    def build(self) -> "VGroup":
        pass
'''
    violations = _scan(project_root, source)
    assert len(violations) == 1
    assert "`Widget.build`" in violations[0]


def test_non_visual_function_is_ignored(project_root: Path) -> None:
    assert _scan(project_root, "def example() -> int:\n    pass\n") == []


def test_suffixed_visual_type_is_detected(project_root: Path) -> None:
    violations = _scan(project_root, 'def example() -> "NodeMobject":\n    pass\n')
    assert len(violations) == 1
