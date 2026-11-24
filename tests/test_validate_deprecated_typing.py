# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for ``workflow/validate_deprecated_typing.py``."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

import validate_deprecated_typing as checker  # noqa: E402


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the checker at a temporary project root."""
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    return tmp_path


def _scan(root: Path, source: str) -> list[str]:
    path = root / "sample.py"
    path.write_text(source, encoding="utf-8")
    return checker.scan(path)


def test_clean_annotations(project_root: Path) -> None:
    assert (
        _scan(project_root, "from collections.abc import Callable\nx: list[int]\n")
        == []
    )


def test_import_from_typing(project_root: Path) -> None:
    violations = _scan(project_root, "from typing import List\n")
    assert len(violations) == 1
    assert "use `list`" in violations[0]


def test_import_alias_attribute(project_root: Path) -> None:
    violations = _scan(project_root, "import typing as t\nx: t.List[int]\n")
    assert len(violations) == 1
    assert "`t.List`" in violations[0]


def test_string_annotation(project_root: Path) -> None:
    violations = _scan(
        project_root,
        "import typing as t\n\ndef f(x: 't.List[int]') -> 'typing.Dict[str, int]':\n    pass\n",
    )
    assert len(violations) == 2
    assert any("`t.List`" in violation for violation in violations)
    assert any("`typing.Dict`" in violation for violation in violations)


def test_star_import_rejected(project_root: Path) -> None:
    violations = _scan(project_root, "from typing import *\n")
    assert len(violations) == 1
    assert "import names explicitly" in violations[0]
