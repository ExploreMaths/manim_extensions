# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Run the repository's validation checks through one entry point.

The checker scripts stay independent; this file records which group each
one belongs to and runs them with one project context.  CI uses the groups
so that one job can install one environment and run every check that needs
it, instead of installing the same environment once per script.

The context defaults to this repository, but a vendored copy can point at
another project:

    python workflow/run_checks.py \
        --root ../my-project \
        --package my_pkg \
        --docs docs/source \
        --examples examples \
        --group static

``--root`` also reads ``[tool.manim-doc-checks]`` from the target
``pyproject.toml``:

    [tool.manim-doc-checks]
    package = "my_pkg"
    distribution = "my-pkg"
    package-dir = "src/my_pkg"
    docs = "docs/source"
    examples = "examples"

Usage:
    python workflow/run_checks.py --list
    python workflow/run_checks.py --group static
    python workflow/run_checks.py --check validate-rst validate-refs
    python workflow/run_checks.py --all
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

SCRIPT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PACKAGE = "manim_extensions"


@dataclass(frozen=True)
class Context:
    """Project paths shared by every checker."""

    root: Path
    package: str
    distribution: str
    package_dir: Path
    docs: Path
    examples: Path

    def env(self) -> dict[str, str]:
        """Environment variables consumed by ``workflow/_context.py``."""
        values = os.environ.copy()
        values.update(
            {
                "MANIM_DOC_CHECKS_ROOT": str(self.root),
                "MANIM_DOC_CHECKS_PACKAGE": self.package,
                "MANIM_DOC_CHECKS_DISTRIBUTION": self.distribution,
                "MANIM_DOC_CHECKS_PACKAGE_DIR": str(self.package_dir),
                "MANIM_DOC_CHECKS_DOCS": str(self.docs),
                "MANIM_DOC_CHECKS_EXAMPLES": str(self.examples),
            }
        )
        return values


Command = tuple[str, ...] | Callable[[Context], tuple[str, ...]]


@dataclass(frozen=True)
class Check:
    """A named command and the CI group that provides its environment."""

    name: str
    group: str
    command: Command


def py(script: str) -> tuple[str, ...]:
    """Run a repository script with the active interpreter."""
    return (sys.executable, str(SCRIPT_DIR / script))


def black_command(ctx: Context) -> tuple[str, ...]:
    """Black-check the target package and any conventional source trees."""
    paths = [str(ctx.package_dir)]
    for name in ("tests", "scripts", "workflow", "docs"):
        path = ctx.root / name
        if path.exists():
            paths.append(str(path))
    return (sys.executable, "-m", "black", "--check", *paths)


def flake8_command(ctx: Context, selection: str) -> tuple[str, ...]:
    """Flake8-check the target package."""
    return (
        sys.executable,
        "-m",
        "flake8",
        str(ctx.package_dir),
        "--select",
        selection,
        "--max-line-length=127",
    )


def flake8_unused_command(ctx: Context) -> tuple[str, ...]:
    """Flake8-check unused imports, excluding package initialisers."""
    return (
        sys.executable,
        "-m",
        "flake8",
        str(ctx.package_dir),
        "--select",
        "F401",
        "--exclude",
        "*__init__.py*,test,examples",
    )


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
    "black": Check("black", "lint", black_command),
    "flake8-unused-imports": Check(
        "flake8-unused-imports", "lint", flake8_unused_command
    ),
    "flake8-syntax": Check(
        "flake8-syntax", "lint", lambda ctx: flake8_command(ctx, "E9,F63,F7,F82")
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


def load_context(args: argparse.Namespace) -> Context:
    """Resolve CLI flags, target ``pyproject.toml``, and defaults."""
    root = (args.root or SCRIPT_DIR).resolve()
    config: dict[str, str] = {}
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        config = data.get("tool", {}).get("manim-doc-checks", {})

    package = args.package or config.get("package") or DEFAULT_PACKAGE
    distribution = args.distribution or config.get("distribution") or package
    package_dir = args.package_dir or config.get("package-dir") or package
    docs = args.docs or config.get("docs") or "docs/source"
    examples = args.examples or config.get("examples") or "examples"
    return Context(
        root=root,
        package=package,
        distribution=distribution,
        package_dir=(root / package_dir).resolve(),
        docs=(root / docs).resolve(),
        examples=(root / examples).resolve(),
    )


def selected_names(groups: list[str], checks: list[str], use_all: bool) -> list[str]:
    """Resolve CLI arguments into a deduplicated check order."""
    if use_all:
        return [name for group in GROUPS.values() for name in group]
    names: list[str] = []
    for group in groups:
        names.extend(GROUPS[group])
    names.extend(checks)
    return list(dict.fromkeys(names))


def run_check(check: Check, ctx: Context) -> bool:
    """Run one check from the target root and report its result."""
    print(f"\n=== {check.name}", flush=True)
    command = check.command(ctx) if callable(check.command) else check.command
    try:
        completed = subprocess.run(command, cwd=ctx.root, env=ctx.env(), check=False)
    except FileNotFoundError:
        print(f"FAIL {check.name}: command not found: {command[0]}", flush=True)
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
    parser.add_argument("--root", type=Path, help="target repository root")
    parser.add_argument("--package", help="target package import name")
    parser.add_argument("--distribution", help="target distribution name for extras")
    parser.add_argument(
        "--package-dir", help="target package directory, relative to root"
    )
    parser.add_argument("--docs", help="target Sphinx source directory")
    parser.add_argument("--examples", help="target examples directory")
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

    ctx = load_context(args)
    failures: list[str] = []
    for name in names:
        if not run_check(CHECKS[name], ctx):
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
