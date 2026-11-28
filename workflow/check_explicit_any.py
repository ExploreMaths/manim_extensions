# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Enforce the explicit-``Any`` baseline with ``mypy --disallow-any-explicit``.

``mypy`` already type-checks the package; this wrapper adds the stricter
``--disallow-any-explicit`` pass and compares its findings with a checked-in
baseline.  Existing technical debt is recorded, but any new explicit ``Any``
fails the check.  When entries are fixed, refresh the baseline with::

    python workflow/check_explicit_any.py --update

Keys use the file path plus the stripped source line rather than the line
number, so unrelated edits that move code do not invalidate the baseline.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "workflow" / "explicit_any_baseline.txt"
ERROR_RE = re.compile(
    r'^(?P<path>.+?):(?P<line>\d+): error: Explicit "Any" is not allowed'
)


def _key(root: Path, path: str, line: int) -> tuple[str, str]:
    """Return a line-number-independent key for one mypy finding."""
    source_path = Path(path)
    if not source_path.is_absolute():
        source_path = root / source_path
    relative = source_path.resolve().relative_to(root.resolve()).as_posix()
    source = source_path.read_text(encoding="utf-8").splitlines()[line - 1].strip()
    return relative, source


def parse_output(root: Path, output: str) -> Counter[tuple[str, str]]:
    """Count explicit-``Any`` findings in raw mypy output."""
    findings: Counter[tuple[str, str]] = Counter()
    for line in output.splitlines():
        match = ERROR_RE.match(line)
        if match is not None:
            findings[_key(root, match.group("path"), int(match.group("line")))] += 1
    return findings


def load_baseline(path: Path) -> Counter[tuple[str, str]]:
    """Read the checked-in baseline as a multiset of file/source keys."""
    findings: Counter[tuple[str, str]] = Counter()
    if not path.exists():
        return findings
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        count, file_name, source = line.split("\t", 2)
        findings[(file_name, source)] += int(count)
    return findings


def write_baseline(path: Path, findings: Counter[tuple[str, str]]) -> None:
    """Write a stable TSV baseline sorted by path and source line."""
    lines = [
        "# " + "SPDX-FileCopyrightText: 2026 ExploreMaths",
        "# " + "SPDX-License-Identifier: MIT",
        "# count\tpath\tsource",
    ]
    for (file_name, source), count in sorted(findings.items()):
        lines.append(f"{count}\t{file_name}\t{source}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_mypy(root: Path, package: Path) -> tuple[int, str]:
    """Run the strict explicit-``Any`` pass from the project root."""
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--disallow-any-explicit",
            str(package),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout + completed.stderr


def main(argv: list[str] | None = None) -> int:
    """Compare current findings with the baseline and report regressions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--package", type=Path)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    package = args.package or root / "manim_extensions"
    exit_code, output = run_mypy(root, package)
    current = parse_output(root, output)
    if exit_code not in (0, 1):
        print(output, end="")
        return exit_code

    if args.update:
        write_baseline(args.baseline, current)
        print(f"Updated {args.baseline} with {sum(current.values())} findings")
        return 0

    baseline = load_baseline(args.baseline)
    new = current - baseline
    fixed = baseline - current
    if new:
        print("New explicit Any annotations are not allowed:\n")
        for (file_name, source), count in sorted(new.items()):
            print(f"{file_name}: {source} ({count}x)")
        print(
            f"\n{sum(new.values())} new finding(s); "
            f"{sum(baseline.values())} existing finding(s) remain in the baseline."
        )
        return 1

    print(
        f"PASS explicit Any baseline: {sum(current.values())} existing findings, "
        f"{sum(fixed.values())} fixed."
    )
    if fixed:
        print(
            "Run `python workflow/check_explicit_any.py --update` to shrink the baseline."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
