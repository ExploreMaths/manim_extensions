# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Refresh the vendored-status cache used by the docs build.

Queries the GitHub API for every upstream repository listed in
``VENDORED.md`` and writes ``docs/source/_vendored_status_cache.json``.
The ``vendored_status`` Sphinx extension reads this cache exclusively,
so the docs build performs no network access of its own.

The committed copy of the cache lives on the ``vendored-status-cache``
branch (refreshed daily by the GitHub Actions workflow); pass the
previous revision via ``--old-cache`` so the script can report which
repositories changed. Existing entries are kept when a refresh fails,
so a transient network or API error never loses previously fetched
data.

Usage:
    python workflow/update_vendored_status.py [--old-cache PATH] [--summary PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "VENDORED.md"
CACHE = ROOT / "docs" / "source" / "_vendored_status_cache.json"

GITHUB_API = "https://api.github.com"


def github_get(path: str) -> dict | list | None:
    """GET the GitHub REST API; return decoded JSON or None on failure."""
    token = os.environ.get("GITHUB_TOKEN", "")
    request = urllib.request.Request(
        f"{GITHUB_API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "manim-extensions-vendored-status",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError):
        return None


def iter_registry() -> list[tuple[str, str]]:
    """Return [(repo_slug, synced_ref)] parsed from the VENDORED.md table."""
    entries = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].startswith("Local module"):
            continue
        match = re.search(r"github\.com/([\w.-]+/[\w.-]+)", cells[1])
        if not match:
            continue
        synced = cells[2].strip("`").replace("`", "")
        # The cell may be a markdown link: [`<sha>`](https://...) — the
        # first backtick-quoted token is the ref.
        quoted = re.search(r"`([^`]+)`", cells[2])
        if quoted:
            synced = quoted.group(1)
        entries.append((match.group(1), "" if synced == "not recorded" else synced))
    return entries


def fetch_upstream(slug: str, ref: str) -> dict:
    """Fetch release/compare/latest-commit info for one repository."""
    info: dict = {
        "release": None, "compare": None, "latest_commit": None,
        "synced_commit": None,
    }

    release = github_get(f"/repos/{slug}/releases/latest")
    if isinstance(release, dict):
        info["release"] = {
            "tag": release.get("tag_name", ""),
            "date": (release.get("published_at") or "")[:10],
        }

    if ref:
        # Resolve the recorded sync ref (tag, branch, or sha) to a commit
        # so the docs can show the exact upstream commit being vendored.
        synced = github_get(f"/repos/{slug}/commits/{ref}")
        if isinstance(synced, dict) and synced.get("sha"):
            info["synced_commit"] = {
                "sha": synced["sha"],
                "date": (synced.get("commit", {}).get("committer", {}).get("date", ""))[:10],
            }

        compare = github_get(f"/repos/{slug}/compare/{ref}...HEAD")
        if isinstance(compare, dict) and compare.get("status") in (
            "identical", "ahead", "behind", "diverged",
        ):
            commits = compare.get("commits") or []
            newest = commits[-1] if commits else compare.get("merge_base_commit")
            info["compare"] = {
                "status": compare["status"],
                "behind_by": compare.get("behind_by", 0),
                "ahead_by": compare.get("ahead_by", 0),
                "newest_sha": (newest or {}).get("sha", ""),
                "newest_date": (
                    (newest or {}).get("commit", {}).get("committer", {}).get("date", "")
                )[:10],
            }

    if not info["compare"]:
        latest = github_get(f"/repos/{slug}/commits?per_page=1")
        if isinstance(latest, list) and latest:
            info["latest_commit"] = {
                "sha": latest[0].get("sha", ""),
                "date": (
                    latest[0].get("commit", {}).get("committer", {}).get("date", "")
                )[:10],
            }
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--old-cache", type=Path, default=None,
        help="previous cache JSON used for change detection and merging",
    )
    parser.add_argument(
        "--summary", type=Path, default=None,
        help="write a one-line commit-message summary to this path",
    )
    args = parser.parse_args()

    old_cache_path = args.old_cache or CACHE
    old: dict = {}
    if old_cache_path.exists():
        try:
            old = json.loads(
                old_cache_path.read_text(encoding="utf-8")
            ).get("repos", {})
        except (ValueError, OSError):
            old = {}

    repos = dict(old)
    changed: list[str] = []
    unchanged = 0
    failures: list[str] = []
    for slug, ref in iter_registry():
        info = fetch_upstream(slug, ref)
        if (info["release"] or info["compare"] or info["latest_commit"]
                or info.get("synced_commit")):
            if repos.get(slug) != info:
                changed.append(slug)
            else:
                unchanged += 1
            repos[slug] = info
        else:
            failures.append(slug)
            if slug not in repos:
                repos[slug] = info  # keep an (empty) placeholder

    today = datetime.now(timezone.utc).date().isoformat()
    data = {"generated": today, "repos": repos}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    parts = [f"{len(changed)} changed", f"{unchanged} no change"]
    message = f"Update vendored status cache {today}: " + ", ".join(parts)
    if changed:
        message += " (" + ", ".join(changed) + ")"
    if failures:
        message += "; fetch failed: " + ", ".join(failures)

    print(f"Cache written: {len(repos)} repositories ({CACHE.relative_to(ROOT)})")
    print(message)
    if failures:
        print(
            f"WARNING: refresh failed for: {', '.join(failures)} "
            "(kept previous data where available)",
            file=sys.stderr,
        )
    if args.summary:
        args.summary.write_text(message + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
