# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""CI checker: every Python file changed by a push or pull request is Black-clean.

The repository is formatter-adopted incrementally, not reformatted in one
sweep: 265 of the 470 modules still differ from Black's output, mostly because
they are vendored from upstream projects whose history we do not want to
rewrite. So this checker only looks at the files a commit actually touches; a
file that was already unformatted fails the moment someone edits it, which
forces new and edited code onto the formatter without a repo-wide diff.

Usage:
    python scripts/check_black_changed.py --base <rev> [--head <rev>]

``--base`` is the commit to diff against (the push's ``before`` SHA or the
pull request's base SHA). ``--head`` defaults to ``HEAD``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def changed_python_files(base: str, head: str) -> list[Path]:
    added_modified_renamed = "--diff-filter=ACMR"
    out = git("diff", "--name-only", added_modified_renamed, base, head, "--", "*.py")
    paths = [ROOT / line for line in out.splitlines() if line.strip()]
    return [path for path in paths if path.is_file()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="revision to diff against")
    parser.add_argument("--head", default="HEAD", help="revision to check")
    args = parser.parse_args()

    files = changed_python_files(args.base, args.head)
    if not files:
        print("PASS  black  no Python files changed")
        return 0

    result = subprocess.run(
        [sys.executable, "-m", "black", "--check", "--diff", *map(str, files)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        print(
            f"FAIL  black  {len(files)} changed file(s) checked; run "
            "`python -m black <those files>` (or enable the pre-commit hook) "
            "and amend the commit.",
            file=sys.stderr,
        )
        return 1

    print(f"PASS  black  {len(files)} changed file(s) are formatted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
