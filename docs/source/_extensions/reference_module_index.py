# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Vendoring-aware links to the Reference Manual package pages.

The ``:vendorstatus:`package``` role renders a link to a package page
under ``reference/``. The link text is the package page's own H1 title,
and a vendored package whose copy is behind upstream (per the committed
``_vendored_status_cache.json``) is shown with a warning badge, so
readers can see at a glance which vendored packages are out of date.

Usage::

    * :vendorstatus:`algorithm` – algorithm visualization toolkit.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from docutils import nodes
from sphinx.util.docutils import SphinxRole
from sphinx.util.nodes import make_refnode

_SLUG_RE = re.compile(r"^\s*\.\.\s+vendored-status::\s*(\S+)")


def _read_package(index_rst: Path) -> tuple[str, str | None]:
    """Return the page title and vendored-status slug of a package index."""
    lines = index_rst.read_text(encoding="utf-8").splitlines()
    title = index_rst.parent.name
    title_found = False
    slug = None
    for index, line in enumerate(lines):
        if slug is None:
            match = _SLUG_RE.match(line)
            if match:
                slug = match.group(1)
        if title_found or index + 1 >= len(lines):
            continue
        stripped = line.strip()
        underline = lines[index + 1].strip()
        if (
            stripped
            and not stripped.startswith("..")
            and len(underline) >= 3
            and set(underline) == {"="}
        ):
            title = stripped
            title_found = True
    return title, slug


def _cache_file(app) -> Path:
    """Return the vendored-status cache used by this build."""
    # Same version-frozen selection as vendored-status: a release build uses
    # its frozen snapshot when one exists, otherwise the latest cache.
    confdir = Path(app.confdir)
    cache_file = (confdir / app.config.vendored_status_cache).resolve()
    release = getattr(app.config, "release", None)
    if release:
        frozen = cache_file.with_name(f"_vendored_status_cache.{release}.json")
        if frozen.exists():
            return frozen
    return cache_file


def _lagging_slugs(app) -> set[str]:
    """Return the upstream repositories whose vendored copy is behind."""
    cache_file = _cache_file(app)
    lagging: set[str] = set()
    if not cache_file.exists():
        return lagging
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return lagging
    for slug, info in data.get("repos", {}).items():
        if not isinstance(info, dict):
            continue
        compare = info.get("compare") or {}
        status = compare.get("status")
        ahead = compare.get("ahead_by", 0) or 0
        if status in ("ahead", "diverged") and ahead > 0:
            lagging.add(slug)
    return lagging


def _package_entry(app, docname: str, package: str) -> nodes.Node | None:
    """Return the linked entry for ``package``, badged when it is behind."""
    index_rst = Path(app.confdir) / "reference" / package / "index.rst"
    if not index_rst.is_file():
        return None
    title, slug = _read_package(index_rst)
    ref = make_refnode(
        app.builder,
        docname,
        f"reference/{package}/index",
        None,
        nodes.Text(title),
        title,
    )
    app.env.note_dependency(str(index_rst))
    if slug not in _lagging_slugs(app):
        return ref
    badge = nodes.inline()
    badge["classes"].append("lagging-badge")
    badge += ref
    badge += nodes.raw(
        "",
        '<span class="lagging-icon" '
        'title="This vendored package is behind upstream" '
        'aria-label="out of sync"></span>',
        format="html",
    )
    return badge


class VendorStatusRole(SphinxRole):
    """Render one package link, badged when its vendored copy is behind."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        package = self.text.strip().strip("/")
        if package.startswith("reference/"):
            package = package[len("reference/"):]
        if package.endswith("/index"):
            package = package[: -len("/index")]

        entry = _package_entry(self.env.app, self.env.docname, package)
        if entry is None:
            message = self.inliner.reporter.warning(
                f"vendorstatus: no package page for {package!r}",
                line=self.lineno,
            )
            return [nodes.Text(package)], [message]
        return [entry], []


def setup(app) -> dict:
    app.add_role("vendorstatus", VendorStatusRole())
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
