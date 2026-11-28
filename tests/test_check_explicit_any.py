# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for ``workflow/check_explicit_any.py``."""

from __future__ import annotations

import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

import check_explicit_any as checker  # noqa: E402


def test_parse_output_separates_documented_findings(tmp_path: Path) -> None:
    """Only annotations carrying a non-empty reason are excused."""
    source = tmp_path / "sample.py"
    source.write_text(
        "from typing import Any\n"
        "value: Any  # explicit-any-ok: external JSON payload\n"
        "other: Any\n",
        encoding="utf-8",
    )
    output = (
        f'{source}:2: error: Explicit "Any" is not allowed  [explicit-any]\n'
        f'{source}:3: error: Explicit "Any" is not allowed  [explicit-any]\n'
        "Found 2 errors in 1 file\n"
    )
    violations, excused = checker.parse_output(tmp_path, output)
    assert violations == [f"{source}:3: other: Any"]
    assert excused == [
        f"{source}:2: value: Any  # explicit-any-ok: external JSON payload"
    ]


def test_parse_output_ignores_unrelated_mypy_errors(tmp_path: Path) -> None:
    """Other mypy diagnostics do not count as explicit-Any findings."""
    source = tmp_path / "sample.py"
    source.write_text("value = 1\n", encoding="utf-8")
    output = f"{source}:1: error: Incompatible types  [assignment]\n"
    violations, excused = checker.parse_output(tmp_path, output)
    assert violations == []
    assert excused == []


def test_excuse_reason_must_not_be_empty(tmp_path: Path) -> None:
    """A bare marker without a reason is still a violation."""
    source = tmp_path / "sample.py"
    source.write_text("value: Any  # explicit-any-ok:\n", encoding="utf-8")
    output = f'{source}:1: error: Explicit "Any" is not allowed  [explicit-any]\n'
    violations, excused = checker.parse_output(tmp_path, output)
    assert violations == [f"{source}:1: value: Any  # explicit-any-ok:"]
    assert excused == []


def test_multiline_signature_reason_may_sit_on_closing_line(tmp_path: Path) -> None:
    """One documented reason excuses a whole multi-line signature."""
    source = tmp_path / "sample.py"
    source.write_text(
        "from typing import Any\n"
        "def f(\n"
        "    value: Any,\n"
        ") -> None:  # explicit-any-ok: heterogeneous runtime value\n"
        "    return None\n",
        encoding="utf-8",
    )
    output = f'{source}:2: error: Explicit "Any" is not allowed  [explicit-any]\n'
    violations, excused = checker.parse_output(tmp_path, output)
    assert violations == []
    assert excused == [f"{source}:2: def f("]
