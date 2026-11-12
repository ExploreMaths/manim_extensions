# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Bundled sample files for ``.. manim::`` examples.

Inside a Manim example block, list the data files the example reads with the
``:files:`` option, for instance ``:files: morphine_2d.mol``; the example then
uses the bare name (``molecule_from_file("morphine_2d.mol")``).

The names are resolved inside the repository's ``examples/`` tree, copied into
the example's scratch working directory, and rendered as a card below the code
block. Both the directive and ``workflow/render_doc_examples.py`` go through
these helpers, so the resolved files and the hashed output name stay in sync.
"""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

SOURCE_REPO_URL = "https://github.com/ExploreMaths/manim_extensions"
SOURCE_BRANCH = "main"
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

    @property
    def raw_url(self) -> str:
        """Direct download link for the file."""
        return f"{SOURCE_REPO_URL}/raw/{SOURCE_BRANCH}/{self.rel_path}"

    @property
    def extension(self) -> str:
        """Lower-case file extension without the dot."""
        return self.path.suffix.lower().lstrip(".") or "file"

    @property
    def human_size(self) -> str:
        """Size rendered the way a person would write it."""
        size = float(self.size)
        for unit in ("B", "KB", "MB"):
            if size < 1024 or unit == "MB":
                if unit == "B":
                    return f"{int(size)} {unit}"
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{self.size} B"  # pragma: no cover - unreachable


def repo_root(confdir: str | Path) -> Path:
    """Repository root that owns the documentation source tree."""
    return Path(confdir).resolve().parents[1]


def parse_file_list(option_input: str) -> list[str]:
    """Split a ``:files:`` option value into plain file names."""
    return [token for token in option_input.replace(",", " ").split() if token]


def resolve_asset(name: str, root: Path) -> ExampleAsset | None:
    """Find a sample file by bare name inside ``<root>/examples``."""
    search_root = root / ASSET_DIR
    if not search_root.is_dir():
        return None
    for path in sorted(search_root.rglob(name)):
        if path.is_file():
            rel_path = path.relative_to(root).as_posix()
            return ExampleAsset(
                name=name,
                path=path,
                rel_path=rel_path,
                size=path.stat().st_size,
                digest=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
    return None


def resolve_assets(names: list[str], root: Path) -> list[ExampleAsset | None]:
    """Resolve every requested file name, keeping unresolved ones as ``None``."""
    return [resolve_asset(name, root) for name in names]


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


EXTENSION_COLORS = {
    "mol": "#2b8a3e",
    "sdf": "#2b8a3e",
    "asnt": "#2b8a3e",
    "json": "#6741d9",
    "xml": "#e8590c",
    "csv": "#0ca678",
    "png": "#c2255c",
    "jpg": "#c2255c",
    "jpeg": "#c2255c",
    "svg": "#c2255c",
    "mp4": "#1c7ed6",
    "gif": "#1c7ed6",
}
DEFAULT_EXTENSION_COLOR = "#495057"

DOWNLOAD_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true"><path d="M12 4v9.2"/><path d="M8.4 10.4 12 14l3.6'
    '-3.6"/><path d="M5.2 16.4v1.8c0 .9.8 1.7 1.7 1.7h10.2c.9 0 1.7-.8 '
    '1.7-1.7v-1.8"/></svg>'
)


def _file_row(asset: ExampleAsset) -> str:
    color = EXTENSION_COLORS.get(asset.extension, DEFAULT_EXTENSION_COLOR)
    badge = asset.extension[:4] or "file"
    return (
        '    <div class="manim-file-row">\n'
        f'      <span class="manim-file-badge" style="background:{color}">'
        f"{badge}</span>\n"
        '      <span class="manim-file-meta">\n'
        f'        <span class="manim-file-name">{asset.name}</span>\n'
        f'        <span class="manim-file-size">{asset.human_size}</span>\n'
        "      </span>\n"
        '      <span class="manim-file-actions">\n'
        f'        <a class="manim-file-action" href="{asset.raw_url}" '
        'title="下载该文件" download>'
        f"{DOWNLOAD_ICON}</a>\n"
        "      </span>\n"
        "    </div>\n"
    )


def files_rst(assets: list[ExampleAsset | None]) -> str:
    """reST block that renders the sample files below the code block.

    Each file becomes one row in the style of a chat file attachment: a coloured
    extension badge, the file name and size, and view/download actions.
    """
    present = [asset for asset in assets if asset is not None]
    if not present:
        return ""
    rows = "".join(_file_row(asset) for asset in present)
    return (
        ".. raw:: html\n\n"
        '    <div class="manim-example-files">\n'
        f"{rows}"
        "    </div>\n"
    )
