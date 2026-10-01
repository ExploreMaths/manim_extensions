# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Sync vendored modules from upstream, preserving local patches.

For every module listed in ``VENDORED.md`` this script:

1. Clones the upstream repository and fetches both the *recorded* sync
   commit (the merge base) and the *target* ref supplied via ``--ref``
   (defaults to the recorded commit, i.e. a no-op check).
2. Maps each local ``.py`` file to its upstream counterpart by relative
   path inside the module directory.
3. Runs a **three-way merge** of every matching file:

   - *base* = upstream at the recorded commit
   - *ours* = the current local file (with all local patches: SPDX
     headers, explicit imports, type annotations, numpydoc docstrings,
     bug fixes)
   - *theirs* = upstream at the target ref

   Regions changed by only one side merge cleanly; regions changed by
   both sides are left as conflict markers and reported for manual
   resolution.  No local patch is ever silently overwritten.
4. Reports API surface changes (added / removed functions, methods,
   classes and parameters) by comparing the local AST against upstream.

Files that exist only upstream or only locally are reported but never
created or deleted automatically.

Usage::

    python workflow/sync_vendored.py                        # all modules, recorded refs (check)
    python workflow/sync_vendored.py --module algorithm      # one module only
    python workflow/sync_vendored.py --module algorithm --ref main
    python workflow/sync_vendored.py --dry-run               # report only, no writes
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "VENDORED.md"
REPORT_JSON = ROOT / "workflow" / "_sync_report.json"


# ---------------------------------------------------------------------------
# VENDORED.md parsing
# ---------------------------------------------------------------------------


@dataclass
class VendoredEntry:
    local_module: str  # e.g. "manim_extensions/algorithm"
    repo_slug: str  # e.g. "sinianluoye/manim-algorithm"
    sync_ref: str  # commit sha / tag / branch, or ""


def parse_registry() -> list[VendoredEntry]:
    """Return vendored entries parsed from the VENDORED.md table."""
    entries: list[VendoredEntry] = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].startswith("Local module"):
            continue
        local = cells[0].strip("`").split(",")[0].strip()
        if not local.startswith("manim_extensions/"):
            continue
        match = re.search(r"github\.com/([\w.-]+/[\w.-]+)", cells[1])
        if not match:
            continue
        quoted = re.search(r"`([^`]+)`", cells[2])
        synced = quoted.group(1) if quoted else cells[2].strip("`")
        entries.append(VendoredEntry(local, match.group(1), synced))
    return entries


# ---------------------------------------------------------------------------
# Upstream fetch
# ---------------------------------------------------------------------------


def clone_upstream(slug: str, refs: list[str], dest: Path) -> dict[str, str]:
    """Clone *slug* and fetch every ref in *refs* (shallow).

    Returns ``{ref: resolved_sha}`` so callers can address each fetched
    revision unambiguously (``FETCH_HEAD`` only keeps the last one).
    """
    url = f"https://github.com/{slug}.git"
    if dest.exists():
        import shutil

        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "remote", "add", "origin", url], check=True)
    shas: dict[str, str] = {}
    for ref in refs:
        if not ref:
            continue
        subprocess.run(
            ["git", "-C", str(dest), "fetch", "-q", "--depth", "1", "origin", ref],
            check=True,
        )
        sha = subprocess.run(
            ["git", "-C", str(dest), "rev-parse", "FETCH_HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        shas[ref] = sha
    return shas


def detect_upstream_subdir(upstream_root: Path, sha: str, local_module: Path) -> Path:
    """Find the upstream subdirectory (at *sha*) whose layout best matches local."""
    local_files = {
        p.relative_to(local_module).as_posix()
        for p in local_module.rglob("*.py")
        if "__pycache__" not in str(p)
    }
    if not local_files:
        return upstream_root

    result = subprocess.run(
        ["git", "-C", str(upstream_root), "ls-tree", "-r", "--name-only", sha],
        capture_output=True,
        text=True,
        check=True,
    )
    upstream_files = {
        line for line in result.stdout.splitlines() if line.endswith(".py")
    }

    best: tuple[int, str] = (0, "")
    # Try the repo root first, then every directory prefix that appears.
    candidates = {""}
    for f in upstream_files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            candidates.add("/".join(parts[:i]))
    for candidate in candidates:
        prefix = candidate + "/" if candidate else ""
        overlap = sum(1 for f in local_files if (prefix + f) in upstream_files)
        if overlap > best[0]:
            best = (overlap, candidate)
    return upstream_root / best[1] if best[1] else upstream_root


def git_show(repo: Path, sha: str, path: str) -> str | None:
    """Return the contents of *path* at *sha*, or None if absent."""
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{sha}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout


# ---------------------------------------------------------------------------
# AST helpers (API change detection)
# ---------------------------------------------------------------------------


def _qualified_name(node: ast.AST, prefix: str = "") -> str:
    name = getattr(node, "name", "")
    return f"{prefix}.{name}" if prefix else name


def collect_functions(
    tree: ast.AST,
) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    result: dict[str, object] = {}

    def visit(node: ast.AST, prefix: str = "") -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = _qualified_name(child, prefix)
                result[qn] = child
                visit(child, qn)
            elif isinstance(child, ast.ClassDef):
                visit(child, _qualified_name(child, prefix))
            else:
                visit(child, prefix)

    visit(tree)
    return result


def collect_classes(tree: ast.AST) -> dict[str, ast.ClassDef]:
    result: dict[str, ast.ClassDef] = {}

    def visit(node: ast.AST, prefix: str = "") -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                qn = _qualified_name(child, prefix)
                result[qn] = child
                visit(child, qn)

    visit(tree)
    return result


def param_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    args = node.args
    names: list[str] = []
    names.extend(a.arg for a in args.posonlyargs)
    names.extend(a.arg for a in args.args)
    if args.vararg:
        names.append("*" + args.vararg.arg)
    names.extend(a.arg for a in args.kwonlyargs)
    if args.kwarg:
        names.append("**" + args.kwarg.arg)
    return names


def signature_diff(
    local: ast.FunctionDef | ast.AsyncFunctionDef,
    upstream: ast.FunctionDef | ast.AsyncFunctionDef,
) -> dict[str, list[str]]:
    lp = param_names(local)
    up = param_names(upstream)
    return {
        "added": [p for p in up if p not in lp],
        "removed": [p for p in lp if p not in up],
    }


def detect_api_changes(local_src: str, upstream_src: str, file_rel: str) -> list[dict]:
    """Compare local and upstream ASTs; return API change records."""
    changes: list[dict] = []
    try:
        local_tree = ast.parse(local_src)
        upstream_tree = ast.parse(upstream_src)
    except SyntaxError:
        return [{"type": "parse_error", "file": file_rel}]

    local_funcs = collect_functions(local_tree)
    upstream_funcs = collect_functions(upstream_tree)

    for qn, up_node in upstream_funcs.items():
        if qn not in local_funcs:
            changes.append({"type": "added", "file": file_rel, "name": qn})
            continue
        diff = signature_diff(local_funcs[qn], up_node)
        if diff["added"] or diff["removed"]:
            changes.append(
                {
                    "type": "signature_changed",
                    "file": file_rel,
                    "name": qn,
                    "added_params": diff["added"],
                    "removed_params": diff["removed"],
                }
            )

    for qn in local_funcs:
        if qn not in upstream_funcs:
            changes.append({"type": "removed", "file": file_rel, "name": qn})

    local_classes = collect_classes(local_tree)
    upstream_classes = collect_classes(upstream_tree)
    for qn in upstream_classes:
        if qn not in local_classes:
            changes.append({"type": "class_added", "file": file_rel, "name": qn})
    for qn in local_classes:
        if qn not in upstream_classes:
            changes.append({"type": "class_removed", "file": file_rel, "name": qn})

    return changes


# ---------------------------------------------------------------------------
# Three-way merge
# ---------------------------------------------------------------------------

_CONFLICT_RE = re.compile(r"^(<<<<<<<|=======|>>>>>>>)", re.MULTILINE)


def has_conflicts(text: str) -> bool:
    return bool(_CONFLICT_RE.search(text))


def three_way_merge(local_path: Path, base: str, theirs: str) -> tuple[str, bool]:
    """Merge *theirs* into *local_path* using *base* as the common ancestor.

    Returns ``(merged_text, had_conflicts)``.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base_path = Path(tmp) / "base.py"
        theirs_path = Path(tmp) / "theirs.py"
        merged_path = Path(tmp) / "merged.py"
        base_path.write_text(base, encoding="utf-8")
        theirs_path.write_text(theirs, encoding="utf-8")
        merged_path.write_text(local_path.read_text(encoding="utf-8"))

        subprocess.run(
            [
                "git",
                "merge-file",
                "-L",
                "local",
                "-L",
                "base",
                "-L",
                "upstream",
                str(merged_path),
                str(base_path),
                str(theirs_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        merged = merged_path.read_text(encoding="utf-8")
        return merged, has_conflicts(merged)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class ModuleReport:
    module: str
    repo: str
    base_ref: str
    target_ref: str
    upstream_subdir: str = ""
    files_merged: list[str] = field(default_factory=list)
    files_conflict: list[str] = field(default_factory=list)
    files_missing_upstream: list[str] = field(default_factory=list)
    files_new_upstream: list[str] = field(default_factory=list)
    changes: list[dict] = field(default_factory=list)


def sync_module(
    entry: VendoredEntry, target_ref: str | None, dry_run: bool
) -> ModuleReport:
    repo = entry.repo_slug
    base_ref = entry.sync_ref
    their_ref = target_ref or base_ref or "HEAD"
    report = ModuleReport(entry.local_module, repo, base_ref, their_ref)

    local_module = ROOT / entry.local_module
    if not local_module.exists():
        report.changes.append({"type": "module_missing", "module": entry.local_module})
        return report

    refs_to_fetch = [r for r in dict.fromkeys([base_ref, their_ref]) if r]
    with tempfile.TemporaryDirectory() as tmp:
        upstream_root = Path(tmp) / "upstream"
        try:
            shas = clone_upstream(repo, refs_to_fetch, upstream_root)
        except subprocess.CalledProcessError as exc:
            report.changes.append(
                {
                    "type": "clone_failed",
                    "repo": repo,
                    "ref": their_ref,
                    "error": str(exc),
                }
            )
            return report

        base_sha = shas.get(base_ref, "")
        their_sha = shas.get(their_ref, "")
        if not their_sha:
            report.changes.append(
                {
                    "type": "clone_failed",
                    "repo": repo,
                    "ref": their_ref,
                    "error": "could not resolve target ref",
                }
            )
            return report

        subdir = detect_upstream_subdir(upstream_root, their_sha, local_module)
        subdir_rel = (
            str(subdir.relative_to(upstream_root)) if subdir != upstream_root else ""
        )
        report.upstream_subdir = subdir_rel

        local_files = {
            p.relative_to(local_module).as_posix()
            for p in local_module.rglob("*.py")
            if "__pycache__" not in str(p)
        }

        result = subprocess.run(
            [
                "git",
                "-C",
                str(upstream_root),
                "ls-tree",
                "-r",
                "--name-only",
                their_sha,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        upstream_files = {
            line[len(subdir_rel) + 1 :] if subdir_rel else line
            for line in result.stdout.splitlines()
            if line.endswith(".py")
            and (not subdir_rel or line.startswith(subdir_rel + "/"))
        }

        for rel in sorted(local_files):
            local_path = local_module / rel
            up_path = f"{subdir_rel}/{rel}" if subdir_rel else rel

            base = git_show(upstream_root, base_sha, up_path) if base_sha else None
            theirs = git_show(upstream_root, their_sha, up_path)

            if theirs is None:
                report.files_missing_upstream.append(rel)
                continue

            # API change detection: local vs upstream (theirs).
            report.changes.extend(
                detect_api_changes(local_path.read_text(encoding="utf-8"), theirs, rel)
            )

            if base is None:
                # No recorded base — cannot 3-way merge; report only.
                report.changes.append(
                    {
                        "type": "no_base",
                        "file": rel,
                        "note": "no recorded sync commit; manual diff required",
                    }
                )
                continue

            if base == theirs:
                # Upstream unchanged since recorded commit.
                continue

            merged, conflicted = three_way_merge(local_path, base, theirs)
            if conflicted:
                report.files_conflict.append(rel)
                report.changes.append(
                    {
                        "type": "merge_conflict",
                        "file": rel,
                        "note": "conflict markers present; resolve manually",
                    }
                )
                # Do NOT write a conflicted file — keep local as-is.
                continue

            if not dry_run and merged != local_path.read_text(encoding="utf-8"):
                local_path.write_text(merged, encoding="utf-8")
            report.files_merged.append(rel)

        for rel in sorted(upstream_files - local_files):
            report.files_new_upstream.append(rel)

    return report


def print_summary(reports: list[ModuleReport]) -> None:
    total_changes = sum(len(r.changes) for r in reports)
    print(f"\n{'=' * 70}")
    print(f"SYNC SUMMARY  ({len(reports)} modules, {total_changes} change records)")
    print(f"{'=' * 70}")
    for r in reports:
        if not r.changes and not r.files_new_upstream and not r.files_missing_upstream:
            print(
                f"\n[{r.module}]  {len(r.files_merged)} file(s) merged — no API changes"
            )
            continue
        print(
            f"\n[{r.module}]  {r.repo} @ {r.target_ref} (base {r.base_ref or 'none'})"
        )
        if r.files_merged:
            print(f"  merged {len(r.files_merged)} file(s)")
        for rel in r.files_conflict:
            print(f"  ! CONFLICT:         {rel}")
        for rel in r.files_new_upstream:
            print(f"  NEW FILE (upstream): {rel}")
        for rel in r.files_missing_upstream:
            print(f"  NO UPSTREAM MATCH:  {rel}")
        for c in r.changes:
            t = c.get("type")
            if t == "added":
                print(f"  + added function:   {c['name']}")
            elif t == "removed":
                print(f"  - removed function: {c['name']}")
            elif t == "signature_changed":
                added = ", ".join(c.get("added_params", []))
                removed = ", ".join(c.get("removed_params", []))
                print(f"  ~ signature change: {c['name']}  (+[{added}] -[{removed}])")
            elif t == "class_added":
                print(f"  + added class:      {c['name']}")
            elif t == "class_removed":
                print(f"  - removed class:    {c['name']}")
            elif t == "merge_conflict":
                pass  # already printed above
            elif t == "clone_failed":
                print(
                    f"  ! clone failed:     {c['repo']} @ {c['ref']}: {c.get('error')}"
                )
            elif t == "module_missing":
                print(f"  ! module missing locally: {c['module']}")
            elif t == "parse_error":
                print(f"  ! parse error: {c.get('file')}")
            elif t == "no_base":
                print(f"  ~ no base recorded: {c['file']} ({c.get('note')})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--module", default=None, help="sync only this module (e.g. 'algorithm')"
    )
    parser.add_argument(
        "--ref",
        default=None,
        help="upstream ref to sync to (default: recorded commit in VENDORED.md)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="report changes without writing files"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPORT_JSON,
        help=f"write JSON report to this path (default: {REPORT_JSON})",
    )
    args = parser.parse_args()

    entries = parse_registry()
    if args.module:
        entries = [e for e in entries if e.local_module.endswith("/" + args.module)]
        if not entries:
            print(f"No module matching '{args.module}'", file=sys.stderr)
            return 1

    reports: list[ModuleReport] = []
    for entry in entries:
        print(f"Syncing {entry.local_module} <- {entry.repo_slug} ...")
        reports.append(sync_module(entry, args.ref, args.dry_run))

    print_summary(reports)

    report_data = {
        "generated": __import__("datetime").datetime.now().isoformat(),
        "ref_overrides": args.ref,
        "dry_run": args.dry_run,
        "modules": [
            {
                "module": r.module,
                "repo": r.repo,
                "base_ref": r.base_ref,
                "target_ref": r.target_ref,
                "upstream_subdir": r.upstream_subdir,
                "files_merged": r.files_merged,
                "files_conflict": r.files_conflict,
                "files_new_upstream": r.files_new_upstream,
                "files_missing_upstream": r.files_missing_upstream,
                "changes": r.changes,
            }
            for r in reports
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\nJSON report written to {args.report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
