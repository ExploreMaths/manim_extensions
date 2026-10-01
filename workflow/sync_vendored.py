# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Sync vendored modules from upstream, preserving local annotations and docstrings.

For every module listed in ``VENDORED.md`` this script:

1. Clones the upstream repository at the recorded sync commit (or a ref
   supplied via ``--ref``).
2. Maps each local ``.py`` file to its upstream counterpart by relative
   path inside the module directory.
3. Merges each matching file:
   - the local **signature** (parameter list with type annotations and
     the return annotation) is kept;
   - the local **docstring** is kept;
   - the upstream **function body** is taken (bug fixes / new logic).
   When a function's parameter names differ between local and upstream
   the function is left untouched and the change is reported for manual
   review.
4. Reports API surface changes (added / removed functions, methods,
   classes and parameters) as a human-readable summary and a machine
   readable JSON file.

The file header (SPDX tags, module docstring), imports and module-level
statements are always taken from the local copy — upstream star imports
and other style differences are intentionally not reintroduced.

Usage::

    python workflow/sync_vendored.py                        # all modules, recorded refs
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
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "VENDORED.md"
REPORT_JSON = ROOT / "workflow" / "_sync_report.json"

GITHUB_API = "https://api.github.com"


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
        # Local module cell may list multiple files joined by ", " — take
        # the first directory-style entry for sync purposes.
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


def clone_upstream(slug: str, ref: str, dest: Path) -> None:
    """Shallow-clone *slug* at *ref* into *dest*."""
    url = f"https://github.com/{slug}.git"
    if dest.exists():
        import shutil

        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    # Fetch the ref explicitly so commit SHAs work with shallow clones.
    subprocess.run(
        ["git", "init", "-q", str(dest)],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(dest), "remote", "add", "origin", url],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(dest), "fetch", "-q", "--depth", "1", "origin", ref],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"],
        check=True,
    )


def detect_upstream_subdir(upstream_root: Path, local_module: Path) -> Path:
    """Find the upstream subdirectory whose file layout best matches local."""
    local_files = {
        p.relative_to(local_module).as_posix()
        for p in local_module.rglob("*.py")
        if "__pycache__" not in str(p)
    }
    if not local_files:
        return upstream_root

    best: tuple[int, Path] = (0, upstream_root)
    for candidate in [upstream_root, *upstream_root.rglob("*")]:
        if not candidate.is_dir():
            continue
        if ".git" in candidate.parts:
            continue
        upstream_files = {
            p.relative_to(candidate).as_posix()
            for p in candidate.rglob("*.py")
            if "__pycache__" not in str(p)
        }
        overlap = len(local_files & upstream_files)
        if overlap > best[0]:
            best = (overlap, candidate)
    return best[1]


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _qualified_name(node: ast.AST, prefix: str = "") -> str:
    """Return a dotted name for a class/function node under *prefix*."""
    name = getattr(node, "name", "")
    return f"{prefix}.{name}" if prefix else name


def collect_functions(
    tree: ast.AST,
) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    """Map dotted qualified name -> function node (module + class methods)."""
    result: dict[str, Any] = {}

    def visit(node: ast.AST, prefix: str = "") -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = _qualified_name(child, prefix)
                result[qn] = child
                visit(child, qn)
            elif isinstance(child, ast.ClassDef):
                qn = _qualified_name(child, prefix)
                visit(child, qn)
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
    """Return parameter names in declaration order (excluding self/cls)."""
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
    """Compare parameter sets; return added/removed parameter names."""
    lp = param_names(local)
    up = param_names(upstream)
    return {
        "added": [p for p in up if p not in lp],
        "removed": [p for p in lp if p not in up],
    }


# ---------------------------------------------------------------------------
# Text-level merge
# ---------------------------------------------------------------------------


def _find_def_line(lines: list[str], node: ast.AST) -> int:
    """1-based line number of the ``def``/``async def`` keyword."""
    start = node.lineno - 1
    for i in range(start, min(start + 20, len(lines))):
        stripped = lines[i].lstrip()
        if stripped.startswith(("def ", "async def ")):
            return i + 1
    return node.lineno


def _docstring_node(node: ast.AST) -> ast.Expr | None:
    """Return the docstring expression node if the first stmt is a string."""
    body = getattr(node, "body", [])
    if not body:
        return None
    first = body[0]
    if (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        return first
    return None


def _body_start_line(node: ast.AST, lines: list[str]) -> int:
    """1-based line number where the function body begins (after docstring)."""
    doc = _docstring_node(node)
    if doc is not None:
        return doc.end_lineno + 1
    # No docstring: scan forward from the def line for the line ending with ':'.
    def_line = _find_def_line(lines, node) - 1
    for i in range(def_line, min(def_line + 40, len(lines))):
        if lines[i].rstrip().endswith(":"):
            return i + 2  # body starts on the next line
    return node.lineno + 1


def _reindent(text: str, target_indent: int) -> str:
    """Re-indent *text* (a block of code) so its first non-blank line has *target_indent* spaces."""
    src_lines = text.splitlines(keepends=True)
    if not src_lines:
        return text
    current_indent = 0
    for ln in src_lines:
        if ln.strip():
            current_indent = len(ln) - len(ln.lstrip(" "))
            break
    delta = target_indent - current_indent
    if delta == 0:
        return text
    out = []
    for ln in src_lines:
        if ln.strip() == "":
            out.append("\n" if ln.endswith("\n") else "")
            continue
        if delta > 0:
            out.append(" " * delta + ln)
        else:
            stripped = ln.lstrip(" ")
            out.append(" " * max(0, len(ln) - len(stripped) + delta) + stripped)
    return "".join(out)


def merge_file(local_path: Path, upstream_path: Path) -> tuple[str, list[dict]]:
    """Merge *upstream_path* into *local_path*.

    Returns ``(merged_text, changes)`` where *changes* is a list of API
    change records for this file.
    """
    local_src = local_path.read_text(encoding="utf-8")
    upstream_src = upstream_path.read_text(encoding="utf-8")

    try:
        local_tree = ast.parse(local_src)
        upstream_tree = ast.parse(upstream_src)
    except SyntaxError:
        return local_src, [{"type": "parse_error", "file": str(local_path)}]

    local_funcs = collect_functions(local_tree)
    upstream_funcs = collect_functions(upstream_tree)

    changes: list[dict] = []
    # We collect body swaps as (start_line, end_line, replacement_text)
    # using 1-based, inclusive line numbers on the LOCAL file.
    swaps: list[tuple[int, int, str]] = []

    local_lines = local_src.splitlines(keepends=True)
    upstream_lines = upstream_src.splitlines(keepends=True)

    # --- functions present in both ---
    for qn, up_node in upstream_funcs.items():
        if qn not in local_funcs:
            changes.append(
                {
                    "type": "added",
                    "file": str(local_path.relative_to(ROOT)),
                    "name": qn,
                }
            )
            continue
        loc_node = local_funcs[qn]
        diff = signature_diff(loc_node, up_node)
        if diff["added"] or diff["removed"]:
            changes.append(
                {
                    "type": "signature_changed",
                    "file": str(local_path.relative_to(ROOT)),
                    "name": qn,
                    "added_params": diff["added"],
                    "removed_params": diff["removed"],
                }
            )
            continue  # leave local untouched for manual review

        # Same parameter names: take upstream body, keep local signature + docstring.
        loc_body_start = _body_start_line(loc_node, local_lines)
        loc_body_end = loc_node.end_lineno  # inclusive
        up_body_start = _body_start_line(up_node, upstream_lines)
        up_body_end = up_node.end_lineno  # inclusive

        if up_body_start > up_body_end:
            # Upstream function has no body (e.g. "pass" only, or docstring-only).
            upstream_body = ""
        else:
            upstream_body = "".join(upstream_lines[up_body_start - 1 : up_body_end])

        # Determine local body indentation from the first non-blank body line.
        local_indent = 4
        for ln_idx in range(loc_body_start - 1, min(loc_body_end, len(local_lines))):
            candidate = local_lines[ln_idx]
            if candidate.strip():
                local_indent = len(candidate) - len(candidate.lstrip(" "))
                break

        if upstream_body.strip():
            replacement = _reindent(upstream_body, local_indent)
        else:
            replacement = ""

        swaps.append((loc_body_start, loc_body_end, replacement))

    # --- functions only in local (removed upstream) ---
    for qn in local_funcs:
        if qn not in upstream_funcs:
            changes.append(
                {
                    "type": "removed",
                    "file": str(local_path.relative_to(ROOT)),
                    "name": qn,
                }
            )

    # --- class-level changes (added / removed) ---
    local_classes = collect_classes(local_tree)
    upstream_classes = collect_classes(upstream_tree)
    for qn in upstream_classes:
        if qn not in local_classes:
            changes.append(
                {
                    "type": "class_added",
                    "file": str(local_path.relative_to(ROOT)),
                    "name": qn,
                }
            )
    for qn in local_classes:
        if qn not in upstream_classes:
            changes.append(
                {
                    "type": "class_removed",
                    "file": str(local_path.relative_to(ROOT)),
                    "name": qn,
                }
            )

    # --- apply swaps from bottom to top so line numbers stay valid ---
    swaps.sort(key=lambda s: s[0], reverse=True)
    for start, end, repl in swaps:
        # Convert to 0-based slice
        local_lines[start - 1 : end] = [repl] if repl else []

    return "".join(local_lines), changes


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


@dataclass
class ModuleReport:
    module: str
    repo: str
    ref: str
    upstream_subdir: str = ""
    files_merged: list[str] = field(default_factory=list)
    files_missing_upstream: list[str] = field(default_factory=list)
    files_new_upstream: list[str] = field(default_factory=list)
    changes: list[dict] = field(default_factory=list)


def sync_module(
    entry: VendoredEntry, target_ref: str | None, dry_run: bool
) -> ModuleReport:
    repo = entry.repo_slug
    ref = target_ref or entry.sync_ref or "HEAD"
    report = ModuleReport(entry.local_module, repo, ref)

    local_module = ROOT / entry.local_module
    if not local_module.exists():
        report.changes.append({"type": "module_missing", "module": entry.local_module})
        return report

    with tempfile.TemporaryDirectory() as tmp:
        upstream_root = Path(tmp) / "upstream"
        try:
            clone_upstream(repo, ref, upstream_root)
        except subprocess.CalledProcessError as exc:
            report.changes.append(
                {
                    "type": "clone_failed",
                    "repo": repo,
                    "ref": ref,
                    "error": str(exc),
                }
            )
            return report

        subdir = detect_upstream_subdir(upstream_root, local_module)
        report.upstream_subdir = str(subdir.relative_to(upstream_root))

        local_files = {
            p.relative_to(local_module).as_posix()
            for p in local_module.rglob("*.py")
            if "__pycache__" not in str(p)
            and not p.name.startswith("_")
            and p.name != "__init__.py"
        }
        # include __init__.py files explicitly
        local_files |= {
            p.relative_to(local_module).as_posix()
            for p in local_module.rglob("__init__.py")
        }

        upstream_files = {
            p.relative_to(subdir).as_posix()
            for p in subdir.rglob("*.py")
            if "__pycache__" not in str(p)
        }

        for rel in sorted(local_files):
            local_path = local_module / rel
            upstream_path = subdir / rel
            if not upstream_path.exists():
                report.files_missing_upstream.append(rel)
                continue
            merged, changes = merge_file(local_path, upstream_path)
            report.changes.extend(changes)
            report.files_merged.append(rel)
            if not dry_run and merged != local_path.read_text(encoding="utf-8"):
                local_path.write_text(merged, encoding="utf-8")

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
        print(f"\n[{r.module}]  {r.repo} @ {r.ref}")
        if r.files_merged:
            print(f"  merged {len(r.files_merged)} file(s)")
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
                print(
                    f"  ~ signature change: {c['name']}  " f"(+[{added}] -[{removed}])"
                )
            elif t == "class_added":
                print(f"  + added class:      {c['name']}")
            elif t == "class_removed":
                print(f"  - removed class:    {c['name']}")
            elif t == "clone_failed":
                print(
                    f"  ! clone failed:     {c['repo']} @ {c['ref']}: {c.get('error')}"
                )
            elif t == "module_missing":
                print(f"  ! module missing locally: {c['module']}")
            elif t == "parse_error":
                print(f"  ! parse error: {c.get('file')}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--module",
        default=None,
        help="sync only this module (e.g. 'algorithm')",
    )
    parser.add_argument(
        "--ref",
        default=None,
        help="upstream ref to sync to (default: recorded commit in VENDORED.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report changes without writing files",
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

    # Write JSON report
    report_data = {
        "generated": __import__("datetime").datetime.now().isoformat(),
        "ref_overrides": args.ref,
        "dry_run": args.dry_run,
        "modules": [
            {
                "module": r.module,
                "repo": r.repo,
                "ref": r.ref,
                "upstream_subdir": r.upstream_subdir,
                "files_merged": r.files_merged,
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
