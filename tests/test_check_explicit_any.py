# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for ``workflow/check_explicit_any.py``."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

import check_explicit_any as checker  # noqa: E402


def test_parse_output_keys_by_file_and_source(tmp_path: Path) -> None:
    """Findings use the stripped source line, not the line number."""
    source = tmp_path / "sample.py"
    source.write_text(
        "from typing import Any\n" "def f(value: Any) -> None:\n" "    pass\n",
        encoding="utf-8",
    )
    output = (
        f'{source}:2: error: Explicit "Any" is not allowed  [explicit-any]\n'
        f'{source}:2: error: Explicit "Any" is not allowed  [explicit-any]\n'
        "Found 2 errors in 1 file\n"
    )
    findings = checker.parse_output(tmp_path, output)
    assert findings == Counter({("sample.py", "def f(value: Any) -> None:"): 2})


def test_baseline_round_trip(tmp_path: Path) -> None:
    """The TSV baseline preserves duplicate counts and tabs in source lines."""
    baseline = tmp_path / "baseline.txt"
    findings = Counter(
        {
            ("pkg/a.py", "def f(x: Any) -> None:"): 2,
            ("pkg/b.py", "value: dict[str, Any]"): 1,
        }
    )
    checker.write_baseline(baseline, findings)
    assert checker.load_baseline(baseline) == findings
