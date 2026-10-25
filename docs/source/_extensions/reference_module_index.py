# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Reference Manual module index with out-of-sync warning icons.

The ``.. module-index::`` directive renders the Module Index of the
Reference Manual as a one-line-per-module list. For every vendored
module whose vendored copy is behind upstream (per the committed
``_vendored_status_cache.json``), a warning icon is appended after the
module's entry, so readers can see at a glance which vendored packages
are out of date.

Usage in ``reference/index.rst``::

    .. module-index::

       basic
       algorithm
       arabic
       ...

Each line is a module page name; the icon uses the same upstream-data
machinery (and version-frozen cache selection) as ``vendored-status``.
"""

from __future__ import annotations

import json
from pathlib import Path

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

from vendored_status import _load_registry


class ModuleIndexDirective(SphinxDirective):
    """Render a per-module list with a warning icon for out-of-sync packages."""

    has_content = True

    def run(self) -> list[nodes.Node]:
        app = self.state.document.settings.env.app
        confdir = Path(app.confdir)

        registry_path = (confdir / app.config.vendored_registry_path).resolve()
        registry = _load_registry(registry_path)

        # Same version-frozen cache selection as vendored-status: a release
        # build uses its frozen snapshot when one exists, otherwise the
        # latest cache.
        cache_file = (confdir / app.config.vendored_status_cache).resolve()
        release = getattr(app.config, "release", None)
        if release:
            frozen = cache_file.with_name(f"_vendored_status_cache.{release}.json")
            if frozen.exists():
                cache_file = frozen

        # Collect module short-names whose vendored copy is behind upstream.
        lagging: set[str] = set()
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                data = {}
            repos = data.get("repos", {})
            for slug, info in repos.items():
                if not isinstance(info, dict):
                    continue
                compare = info.get("compare") or {}
                status = compare.get("status")
                ahead = compare.get("ahead_by", 0) or 0
                if status in ("ahead", "diverged") and ahead > 0:
                    entry = registry.get(slug)
                    if entry:
                        lagging.add(entry["module"].split("/")[-1])

        bullet_list = nodes.bullet_list()
        bullet_list["classes"].append("module-index")
        for raw_line in self.content:
            line = raw_line.strip()
            if not line:
                continue
            if "=" in line:
                title, page = [x.strip() for x in line.split("=", 1)]
            else:
                title = page = line
            item = nodes.list_item()
            para = nodes.paragraph()
            ref = nodes.reference(
                rawsource=title, text=title, refuri=f"{page}/index.html"
            )
            if page in lagging:
                badge = nodes.inline()
                badge["classes"].append("lagging-badge")
                badge += ref
                icon = nodes.raw(
                    "",
                    '<span class="lagging-icon" '
                    'title="This vendored package is behind upstream" '
                    'aria-label="out of sync"></span>',
                    format="html",
                )
                badge += icon
                para += badge
            else:
                para += ref
            item += para
            bullet_list += item

        self.state.document.settings.env.note_dependency(str(registry_path))
        if cache_file.exists():
            self.state.document.settings.env.note_dependency(str(cache_file))
        return [bullet_list]


def setup(app) -> dict:
    app.add_directive("module-index", ModuleIndexDirective)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
