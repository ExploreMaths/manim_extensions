# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Sphinx extension that shows vendoring status for a vendored package.

Usage in the ``index.rst`` of a vendored package::

    .. vendored-status:: bmmtstb/manim-meshes

The directive renders a status block containing:

- the sync point recorded in ``VENDORED.md`` (or a note that it is not
  recorded), plus the date of the last commit that touched the local
  module in this repository,
- the latest upstream release, if any,
- how many commits upstream has made since the sync point, with the
  newest commit hash and date (GitHub-style "N commits behind"), and
- a warning when the vendored copy is behind upstream.

All upstream data comes from the committed cache
``_vendored_status_cache.json`` next to ``conf.py``. The canonical copy
lives on the repository's ``rtd-media`` branch and is copied into place
by the ReadTheDocs ``pre_build`` step; the "Vendored status cache"
GitHub Actions workflow refreshes it daily via
``workflow/update_vendored_status.py`` (using the automatic
``GITHUB_TOKEN``), and the Docs media workflow refreshes it on every
push before triggering the ReadTheDocs build. For a local docs build,
run that script once to create the cache file.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

# ---------------------------------------------------------------------------
# Registry (VENDORED.md) parsing
# ---------------------------------------------------------------------------

_registry_cache: dict[str, dict | None] | None = None


def _load_registry(registry_path: Path) -> dict[str, dict]:
    """Parse the VENDORED.md table into {repo_slug: row} mapping."""
    global _registry_cache
    key = str(registry_path.resolve())
    if _registry_cache is not None and key in _registry_cache:
        return _registry_cache[key]

    rows: dict[str, dict] = {}
    if registry_path.exists():
        for line in registry_path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|") or "---" in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or cells[0].startswith("Local module"):
                continue
            module, upstream, synced = cells[0], cells[1], cells[2]
            match = re.search(r"github\.com/([\w.-]+/[\w.-]+)", upstream)
            if not match:
                continue
            slug = match.group(1)
            rows[slug] = {
                "module": module.strip("`").replace("`", ""),
                "synced": synced.strip("`").replace("`", ""),
            }
            quoted = re.search(r"`([^`]+)`", synced)
            if quoted:
                rows[slug]["synced"] = quoted.group(1)
    result = rows
    _registry_cache = {key: result}
    return result


def _short(sha: str | None) -> str:
    return sha[:7] if sha else "?"


# ---------------------------------------------------------------------------
# Upstream data (committed cache, refreshed by the Vendored status cache
# GitHub Actions workflow via workflow/update_vendored_status.py)
# ---------------------------------------------------------------------------


def _upstream_info(slug: str, cached: dict | None) -> dict:
    """Return the cache entry for a repository (empty when unknown)."""
    if cached is not None:
        return cached
    return {"release": None, "compare": None, "latest_commit": None}


# ---------------------------------------------------------------------------
# Directive
# ---------------------------------------------------------------------------


class VendoredStatusDirective(SphinxDirective):
    """Render live vendoring status for one upstream repository."""

    required_arguments = 1
    optional_arguments = 0
    has_content = False
    option_spec = {
        "name": str,
        "ref": str,
    }

    def run(self) -> list[nodes.Node]:
        app = self.state.document.settings.env.app
        slug = self.arguments[0].strip().rstrip("/")
        slug = re.sub(r"^https?://github\.com/", "", slug)
        name = self.options.get("name", slug.split("/")[-1])

        confdir = Path(app.confdir)
        registry_path = (confdir / app.config.vendored_registry_path).resolve()
        registry = _load_registry(registry_path)
        entry = registry.get(slug, {})
        synced = self.options.get("ref", entry.get("synced", "not recorded"))

        # Item segments: ("t", text) plain, ("c", text) inline code,
        # ("l", text, url) linked inline code.
        def T(text: str) -> tuple:
            return ("t", text)

        def C(text: str) -> tuple:
            return ("c", text)

        def L(text: str, url: str) -> tuple:
            return ("l", text, url)

        def commit_link(repo_slug: str, sha: str) -> str:
            return f"https://github.com/{repo_slug}/commit/{sha}"

        items: list[list[tuple]] = []

        # Upstream side ----------------------------------------------------
        cache_file = (confdir / app.config.vendored_status_cache).resolve()
        cached_entry = None
        cache_date = None
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                cached_entry = data.get("repos", {}).get(slug)
                cache_date = data.get("generated")
                self.state.document.settings.env.note_dependency(str(cache_file))
            except (ValueError, OSError):
                cached_entry = None
        info = _upstream_info(slug, cached_entry)

        # Current vendored state -------------------------------------------
        if synced and synced != "not recorded":
            items.append([T("Vendored copy: synced at "), C(synced), T(".")])
        else:
            items.append([T("Vendored copy: sync point not recorded in VENDORED.md.")])

        synced_commit = info.get("synced_commit")
        if synced_commit:
            items.append([
                T("Currently vendored upstream commit: "),
                L(_short(synced_commit["sha"]),
                  commit_link(slug, synced_commit["sha"])),
                T(f" ({synced_commit['date']})."),
            ])

        if cached_entry is not None and cache_date:
            items.append([T(f"Upstream data cached on {cache_date}.")])

        release = info.get("release")
        if release:
            items.append([
                T("Latest upstream release: "),
                C(release["tag"]),
                T(f" ({release['date']})."),
            ])

        compare = info.get("compare")
        behind = False
        if compare:
            # GitHub compare semantics: ahead_by = commits in HEAD (upstream)
            # not in the base (the recorded sync point); behind_by = commits
            # in the base not reachable from upstream HEAD.
            status = compare["status"]
            if status == "identical":
                items.append([T("The vendored copy is up to date with upstream.")])
            elif status == "ahead":
                if synced != "not recorded":
                    ref_seg = C(synced)
                else:
                    ref_seg = T("the sync point")
                items.append([
                    T(f"{compare['ahead_by']} new upstream commit(s) since "),
                    ref_seg,
                    T(", latest "),
                    L(_short(compare["newest_sha"]),
                      commit_link(slug, compare["newest_sha"])),
                    T(f" ({compare['newest_date']})."),
                ])
                behind = compare["ahead_by"] > 0
            elif status == "behind":
                items.append([
                    T(f"The recorded sync point has {compare['behind_by']} "
                      "commit(s) not reachable from upstream HEAD (upstream "
                      "history may have been rewritten)."),
                ])
            else:  # diverged
                items.append([
                    T(f"Histories diverged: {compare['ahead_by']} upstream / "
                      f"{compare['behind_by']} local-only commit(s); newest "
                      "upstream commit "),
                    L(_short(compare["newest_sha"]),
                      commit_link(slug, compare["newest_sha"])),
                    T(f" ({compare['newest_date']})."),
                ])
                behind = compare["ahead_by"] > 0
        elif info.get("latest_commit"):
            latest = info["latest_commit"]
            if synced and synced != "not recorded":
                items.append([
                    T("Could not compare against "), C(synced),
                    T(" (the ref may not exist upstream)."),
                ])
            items.append([
                T("Latest upstream commit: "),
                L(_short(latest["sha"]), commit_link(slug, latest["sha"])),
                T(f" ({latest['date']}); "
                  "sync point unknown, cannot count new commits."),
            ])
        else:
            items.append([
                T("No upstream data in the cache; run "),
                C("workflow/update_vendored_status.py"),
                T(" to refresh it."),
            ])

        # Render as an admonition: a "note" block normally, escalating to a
        # "warning" block when the vendored copy is behind upstream. The
        # custom classes allow theme-specific styling.
        admonition = nodes.admonition()
        admonition["classes"].append("vendored-status")
        if behind:
            admonition["classes"] += ["warning", "vendored-status-behind"]
        else:
            admonition["classes"].append("note")
        title = nodes.title()
        title += nodes.Text("Vendoring status: ")
        title += nodes.literal(text=name, rawsource=name)
        admonition += title

        bullet_list = nodes.bullet_list()
        for segments in items:
            item = nodes.list_item()
            para = nodes.paragraph()
            for seg in segments:
                if seg[0] == "t":
                    para += nodes.Text(seg[1])
                elif seg[0] == "c":
                    para += nodes.literal(text=seg[1], rawsource=seg[1])
                else:  # "l": linked inline code
                    ref = nodes.reference(rawsource=seg[1], text=seg[1], refuri=seg[2])
                    ref["classes"].append("literal")
                    para += ref
            item += para
            bullet_list += item
        admonition += bullet_list

        if behind:
            warning = nodes.paragraph()
            warning += nodes.strong(
                text="This vendored copy is behind upstream — consider re-vendoring."
            )
            admonition += warning

        self.state.document.settings.env.note_dependency(str(registry_path))
        return [admonition]


def setup(app) -> dict:
    app.add_config_value(
        "vendored_registry_path", "../../VENDORED.md", rebuild="env", types=[str]
    )
    app.add_config_value(
        "vendored_status_cache", "_vendored_status_cache.json",
        rebuild="env", types=[str],
    )
    app.add_directive("vendored-status", VendoredStatusDirective)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
