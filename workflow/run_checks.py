# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Run the repository's validation checks through one entry point.

The checker scripts stay independent; this file only records which group
each one belongs to and runs them with the same working directory.  CI
uses the groups so that one job can install one environment and run every
check that needs it, instead of installing the same environment once per
script.

Usage:
    python workflow/run_checks.py --list
    python workflow/run_checks.py --group static
    python workflow/run_checks.py --check validate-rst validate-refs
    python workflow/run_checks.py --all
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Check:
    """A named command and the CI group that provides its environment."""

    name: str
    group: str
    command: tuple[str, ...]


def py(script: str) -> tuple[str, ...]:
    """Run a repository script with the active interpreter."""
    return (sys.executable, script)


CHECKS: dict[str, Check] = {
    # No third-party packages beyond docutils (installed by the static job).
    "validate-extras": Check(
        "validate-extras", "static", py("workflow/validate_extras.py")
    ),
    "validate-rst": Check("validate-rst", "static", py("workflow/validate_rst.py")),
    "validate-intersphinx": Check(
        "validate-intersphinx", "static", py("workflow/validate_intersphinx.py")
    ),
    "validate-example-files": Check(
        "validate-example-files", "static", py("workflow/validate_example_files.py")
    ),
    "validate-example-spacing": Check(
        "validate-example-spacing", "static", py("workflow/validate_example_spacing.py")
    ),
    "validate-example-names": Check(
        "validate-example-names", "static", py("workflow/validate_example_names.py")
    ),
    "validate-headers": Check(
        "validate-headers", "static", py("workflow/validate_headers.py")
    ),
    "validate-type-annotations": Check(
        "validate-type-annotations", "static", py("scripts/check_type_annotations.py")
    ),
    "validate-return-annotations": Check(
        "validate-return-annotations",
        "static",
        py("scripts/check_return_annotations.py"),
    ),
    # Needs the package installed at ``.[all]``.
    "validate-manim-directives": Check(
        "validate-manim-directives",
        "package",
        py("workflow/validate_manim_directives.py"),
    ),
    "validate-param-docs": Check(
        "validate-param-docs", "package", py("workflow/validate_param_docs.py")
    ),
    "validate-imports": Check(
        "validate-imports", "package", py("workflow/check_redundant_imports.py")
    ),
    "validate-relative-imports": Check(
        "validate-relative-imports", "package", py("workflow/check_relative_imports.py")
    ),
    "validate-docstrings": Check(
        "validate-docstrings", "package", py("workflow/validate_docstrings.py")
    ),
    "validate-doc-sections": Check(
        "validate-doc-sections", "package", py("workflow/validate_doc_sections.py")
    ),
    "validate-api-coverage": Check(
        "validate-api-coverage", "package", py("workflow/validate_api_coverage.py")
    ),
    "validate-refs": Check("validate-refs", "package", py("workflow/validate_refs.py")),
    # Full extras plus dvisvgm; kept separate because it is the slowest job.
    "validate-example-layout": Check(
        "validate-example-layout", "layout", py("workflow/check_example_layout.py")
    ),
    # Formatting and repository policy; no package install.
    "reuse-lint": Check("reuse-lint", "lint", ("reuse", "lint")),
    "black": Check(
        "black",
        "lint",
        (
            sys.executable,
            "-m",
            "black",
            "--check",
            "manim_extensions",
            "tests",
            "scripts",
            "workflow",
            "docs",
        ),
    ),
    "flake8-unused-imports": Check(
        "flake8-unused-imports",
        "lint",
        (
            sys.executable,
            "-m",
            "flake8",
            "manim_extensions",
            "--select",
            "F401",
            "--exclude",
            "*__init__.py*,test,examples",
        ),
    ),
    "flake8-syntax": Check(
        "flake8-syntax",
        "lint",
        (
            sys.executable,
            "-m",
            "flake8",
            "manim_extensions",
            "--select",
            "E9,F63,F7,F82",
            "--max-line-length=127",
        ),
    ),
    # Needs the package installed at ``.[all]`` plus pip-audit.
    "pip-audit": Check("pip-audit", "audit", ("pip-audit", "--desc", "on")),
}

GROUPS: dict[str, tuple[str, ...]] = {
    "static": (
        "validate-extras",
        "validate-rst",
        "validate-intersphinx",
        "validate-example-files",
        "validate-example-spacing",
        "validate-example-names",
        "validate-headers",
        "validate-type-annotations",
        "validate-return-annotations",
    ),
    "package": (
        "validate-manim-directives",
        "validate-param-docs",
        "validate-imports",
        "validate-relative-imports",
        "validate-docstrings",
        "validate-doc-sections",
        "validate-api-coverage",
        "validate-refs",
    ),
    "layout": ("validate-example-layout",),
    "lint": ("reuse-lint", "black", "flake8-unused-imports", "flake8-syntax"),
    "audit": ("pip-audit",),
}


def selected_names(groups: list[str], checks: list[str], use_all: bool) -> list[str]:
    """Resolve CLI arguments into a deduplicated check order."""
    if use_all:
        return [name for group in GROUPS.values() for name in group]
    names: list[str] = []
    for group in groups:
        names.extend(GROUPS[group])
    names.extend(checks)
    return list(dict.fromkeys(names))


def run_check(check: Check) -> bool:
    """Run one check from the repository root and report its result."""
    print(f"\n=== {check.name}", flush=True)
    try:
        completed = subprocess.run(check.command, cwd=ROOT, check=False)
    except FileNotFoundError:
        print(f"FAIL {check.name}: command not found: {check.command[0]}", flush=True)
        return False
    if completed.returncode != 0:
        print(f"FAIL {check.name} (exit {completed.returncode})", flush=True)
        return False
    print(f"PASS {check.name}", flush=True)
    return True


def main() -> int:
    """Parse arguments, run the selected checks, and report a summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list groups and checks")
    parser.add_argument("--group", action="append", choices=sorted(GROUPS), default=[])
    parser.add_argument("--check", nargs="+", choices=sorted(CHECKS), default=[])
    parser.add_argument("--all", action="store_true", help="run every group")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    if args.list:
        for group, names in GROUPS.items():
            print(f"{group}:")
            for name in names:
                print(f"  {name}")
        return 0

    names = selected_names(args.group, args.check, args.all)
    if not names:
        parser.error("select at least one --group, --check, or --all")

    failures: list[str] = []
    for name in names:
        if not run_check(CHECKS[name]):
            failures.append(name)
            if args.fail_fast:
                break

    if failures:
        print(f"\nFAIL {len(failures)} check(s): {', '.join(failures)}")
        return 1
    print(f"\nPASS {len(names)} check(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
