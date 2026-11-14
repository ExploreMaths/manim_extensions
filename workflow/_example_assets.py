# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Standalone sample-file helpers for the validation scripts.

``docs/source/_extensions/manim_files.py`` is the Sphinx-side implementation.
A repository that only vendors ``workflow/`` and ``scripts/`` may not have
that extension, so this module provides the small subset the checkers need
without pulling in the documentation build.
"""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

ASSET_DIR = "examples"
MISSING_DIGEST = "missing"


@dataclass(frozen=True)
class ExampleAsset:
    """A sample file referenced by a ``.. manim::`` example."""

    name: str
    path: Path
    rel_path: str
    size: int
    digest: str


def parse_file_list(option_input: str) -> list[str]:
    """Split a ``:files:`` option value into plain file names."""
    return [token for token in option_input.replace(",", " ").split() if token]


def resolve_asset(
    name: str, root: Path, asset_root: Path | None = None
) -> ExampleAsset | None:
    """Find a sample file by bare name inside the configured examples tree."""
    search_root = asset_root if asset_root is not None else root / ASSET_DIR
    if not search_root.is_dir():
        return None
    for path in sorted(search_root.rglob(name)):
        if path.is_file():
            try:
                rel_path = path.relative_to(root).as_posix()
            except ValueError:
                rel_path = path.name
            return ExampleAsset(
                name=name,
                path=path,
                rel_path=rel_path,
                size=path.stat().st_size,
                digest=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
    return None


def resolve_assets(
    names: list[str], root: Path, asset_root: Path | None = None
) -> list[ExampleAsset | None]:
    """Resolve every requested file name, keeping unresolved ones as ``None``."""
    return [resolve_asset(name, root, asset_root) for name in names]


def copy_assets(assets: list[ExampleAsset | None], workdir: Path) -> None:
    """Copy resolved assets into the scratch directory the example runs in."""
    for asset in assets:
        if asset is None:
            continue
        shutil.copyfile(asset.path, workdir / asset.name)


def example_digest(
    class_name: str, code_lines: list[str], assets: list[ExampleAsset | None]
) -> str:
    """Deterministic short hash of the example source and its sample files."""
    payload = "\n".join(code_lines)
    for asset in assets:
        digest = MISSING_DIGEST if asset is None else asset.digest
        name = "" if asset is None else asset.name
        payload += f"\n{name}:{digest}"
    digest = hashlib.md5(payload.encode()).hexdigest()[:8]
    return f"{class_name}-{digest}"
