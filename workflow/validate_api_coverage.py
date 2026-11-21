# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Verify every public constant, function, and class is API-documented and
maintain the snapshot that ``autodoc_all``'s ``:missing-only:`` mode
filters against.

Scans the whole ``manim_extensions`` package for every name bound at a
module's top level (plus ``__all__`` entries), then resolves every ``autoclass`` / ``autofunction`` / ``autodata`` /
``autoall`` directive in ``docs/source`` and matches by canonical
defining-module dotted name.

A name counts as documented when either
  * an explicit autodoc directive reaches it,
  * an ``.. autoall::`` block without ``:missing-only:`` enumerates it
    (its full expansion is injected into the docs at build time), or
  * an ``.. autoall::`` block with ``:missing-only:`` enumerates it
    (the block injects it into the docs at build time).

The snapshot (documented names only) is what ``:missing-only:`` blocks
filter against at Sphinx build time:

    python workflow/validate_api_coverage.py --write-snapshot

A percentage can be written as a shields.io endpoint badge:

    python workflow/validate_api_coverage.py --badge .github/badges/docs-coverage.json

Usage:
    python workflow/validate_api_coverage.py              # check
    python workflow/validate_api_coverage.py --write-snapshot
"""

import argparse
import importlib
import json
import pkgutil
import re
import sys
import types
import typing
from pathlib import Path

from _context import DOCS, PACKAGE, ROOT, SRC
from coverage_badge import build_badge

sys.path.insert(0, str(SRC.parent))  # pin the local package over any installed copy
SNAPSHOT_PATH = DOCS / "_extensions" / "api_documented.json"

sys.path.insert(0, str(DOCS / "_extensions"))

from autodoc_all import (  # noqa: E402
    classify,
    defining_dotted,
    iter_package_modules,
    public_names,
)

DOCS_TOOLS = {"docbuild", "testing", "custom_mobjects", "__pycache__"}

# Public names deliberately excluded from the API docs (recorded
# decisions; keep in sync with :skip: options in the rst sources).
IGNORED_PUBLIC_NAMES: set[str] = set()

DIRECTIVE_RE = re.compile(
    r"^\.\.\s+(autoclass|autofunction|autodata|autoall)::\s+(\S+)\s*$",
    re.MULTILINE,
)
OPTION_RE = re.compile(r"^\s+:(\w[\w-]*):\s*(.*)$")
# A reST section underline: a run of the same adornment character.
UNDERLINE_RE = re.compile(r"^\s*[-=~^+#*:]{3,}\s*$")


def iter_modules():
    for info in pkgutil.walk_packages([str(SRC)], f"{PACKAGE}."):
        if any(part in DOCS_TOOLS for part in info.name.split(".")):
            continue
        if info.name.endswith(".__main__"):
            continue
        try:
            yield importlib.import_module(info.name)
        except Exception:
            continue


def resolve_dotted(dotted):
    """Import 'a.b.c' progressively; return the object or None."""
    parts = dotted.split(".")
    last_error = None
    for cut in range(len(parts), 0, -1):
        try:
            module = importlib.import_module(".".join(parts[:cut]))
        except Exception as exc:
            last_error = exc
            continue
        obj = module
        try:
            for attr in parts[cut:]:
                obj = getattr(obj, attr)
        except AttributeError:
            return None
        return obj
    # fallback: walk attributes from the top-level package (uses whatever
    # is already imported; robust against transient import failures)
    try:
        obj = importlib.import_module(parts[0])
        for attr in parts[1:]:
            obj = getattr(obj, attr)
        return obj
    except Exception:
        print(f"WARNING: resolve_dotted({dotted!r}) failed: {last_error!r}")
        return None


def parse_directives():
    """Yield ``(rst, directive, target, options, line_no)`` for every directive."""
    for rst in sorted(DOCS.rglob("*.rst")):
        text = rst.read_text(encoding="utf-8")
        for match in DIRECTIVE_RE.finditer(text):
            directive, target = match.group(1), match.group(2)
            line_no = text.count("\n", 0, match.start()) + 1
            options = {}
            rest = text[match.end() :]
            for line in rest.splitlines()[1:]:
                om = OPTION_RE.match(line)
                if not om:
                    break
                options[om.group(1)] = om.group(2).strip()
            yield rst, directive, target, options, line_no


def section_heading(text: str, line_no: int) -> str:
    """Return the underlined section heading above *line_no*, if any."""
    lines = text.splitlines()
    for index in range(line_no - 1, -1, -1):
        if index + 1 < len(lines) and UNDERLINE_RE.match(lines[index + 1]):
            return lines[index].strip()
    return ""


def autoall_expansion_keys(target, options):
    """Canonical dotted names an ``autoall`` block expands to.

    Mirrors AutoAllDirective's enumeration (types filter + skip list +
    recursion), without the ``:missing-only:`` snapshot filter.
    """
    keys = set()
    warnings = []
    obj = resolve_dotted(target)
    if not isinstance(obj, types.ModuleType):
        warnings.append(f"autoall target {target} is not a module")
        return keys, warnings
    want = {
        t.strip()
        for t in (options.get("types") or "class,function,data").split(",")
        if t.strip()
    }
    skip = set((options.get("skip") or "").split())
    modules = iter_package_modules(obj) if "recursive" in options else iter([obj])
    for mod in modules:
        for name, member in public_names(mod):
            if classify(member) not in want or name in skip:
                continue
            keys.add(defining_dotted(mod, name, member))
    return keys, warnings


def documented_keys():
    """Canonical dotted names reachable from explicit autodoc directives
    and from full (non-``:missing-only:``) ``autoall`` expansions."""
    keys = set()
    warnings = []
    for rst, directive, target, options, _line in parse_directives():
        if directive == "autoall":
            if "missing-only" in options:
                continue  # handled separately (see missing_only_coverage)
            expanded, w = autoall_expansion_keys(target, options)
            keys |= expanded
            warnings.extend(f"{w_} ({rst.relative_to(ROOT)})" for w_ in w)
            continue
        obj = resolve_dotted(target)
        if obj is None:
            warnings.append(
                f"cannot resolve {directive} target {target} ({rst.relative_to(ROOT)})"
            )
            continue
        mod = getattr(obj, "__module__", None)
        if not mod or not mod.startswith(PACKAGE):
            mod = target.rsplit(".", 1)[0]
        keys.add(f"{mod}.{target.rsplit('.', 1)[-1]}")
    return keys, warnings


def missing_only_coverage():
    """Canonical dotted names that :missing-only: autoall blocks inject."""
    keys = set()
    warnings = []
    for rst, directive, target, options, _line in parse_directives():
        if directive != "autoall" or "missing-only" not in options:
            continue
        expanded, w = autoall_expansion_keys(target, options)
        keys |= expanded
        warnings.extend(f"{w_} ({rst.relative_to(ROOT)})" for w_ in w)
    return keys, warnings


def empty_autoall_sections():
    """Full (non-``:missing-only:``) autoall blocks that expand to zero entries.

    Such a block leaves its section heading (e.g. "Constants") empty on the
    rendered page.  The section and directive must be removed, or the module
    must actually expose the advertised names.  ``:missing-only:`` blocks are
    exempt: an empty one means every entry is already curated elsewhere.
    """
    issues = []
    for rst, directive, target, options, line_no in parse_directives():
        if directive != "autoall" or "missing-only" in options:
            continue
        keys, warnings = autoall_expansion_keys(target, options)
        if keys or warnings:
            continue  # unresolved targets are reported as warnings above
        heading = section_heading(rst.read_text(encoding="utf-8"), line_no)
        issues.append((rst, line_no, heading or target, target))
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-snapshot",
        action="store_true",
        help=f"write the documented-names snapshot to {SNAPSHOT_PATH.relative_to(ROOT)}",
    )
    parser.add_argument(
        "--badge",
        default=None,
        help="write a shields.io endpoint badge JSON for the coverage percentage",
    )
    args = parser.parse_args()

    explicit, warnings = documented_keys()
    for w in warnings:
        print(f"WARNING: {w}")

    empty = empty_autoall_sections()

    if args.write_snapshot:
        SNAPSHOT_PATH.write_text(
            json.dumps(sorted(explicit), indent=1) + "\n", encoding="utf-8"
        )
        print(
            f"Wrote {len(explicit)} documented names to {SNAPSHOT_PATH.relative_to(ROOT)}"
        )
        return 0
    else:
        if not SNAPSHOT_PATH.exists():
            print("FAIL  api-coverage  1 issue(s)\n")
            print(
                "  -:-  stale-snapshot: api_documented.json missing; run with --write-snapshot"
            )
            return 1
        else:
            on_disk = set(json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")))
            if on_disk != explicit:
                print("FAIL  api-coverage  1 issue(s)\n")
                print(
                    f"  -:-  stale-snapshot: api_documented.json is stale "
                    f"({len(on_disk)} on disk vs {len(explicit)} computed). "
                    "Run: python workflow/validate_api_coverage.py --write-snapshot"
                )
                return 1

    injected, warnings = missing_only_coverage()
    for w in warnings:
        print(f"WARNING: {w}")

    covered = explicit | injected
    total = 0
    missing = []
    for module in iter_modules():
        for name, obj in public_names(module):
            # Type variables and type aliases are not part of the
            # class/function/constant coverage: aliases have their own
            # ``Type Aliases`` section (``autodoc_all`` classifies them as
            # ``typealias``) and are checked by the reference build.
            if (
                isinstance(
                    obj,
                    (typing.TypeVar, typing.ParamSpec, typing.TypeVarTuple),
                )
                or classify(obj) == "typealias"
                or name.startswith("_")
            ):
                continue
            total += 1
            key = defining_dotted(module, name, obj)
            if key not in covered and key not in IGNORED_PUBLIC_NAMES:
                missing.append(f"{module.__name__}.{name}")

    covered_count = total - len(missing)
    percent = 100.0 * covered_count / total if total else 100.0
    if args.badge:
        out = Path(args.badge)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(build_badge(percent, "Docs Coverage"), indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {out}: {percent:.1f}%")

    if missing or empty:
        total_issues = len(missing) + len(empty)
        print(
            f"FAIL  api-coverage  {percent:.1f}% "
            f"({covered_count}/{total} names documented)\n"
        )
        for dotted in sorted(missing):
            print(f"  -:-  undocumented-api: {dotted}")
        for rst, line_no, heading, target in sorted(
            empty, key=lambda issue: (str(issue[0]), issue[1])
        ):
            rel = rst.relative_to(ROOT)
            print(
                f"  {rel}:{line_no}  empty-autoall-section: '{heading}' "
                f"({target}) expands to 0 entries; remove the empty section "
                "or expose the advertised names"
            )
        print(f"\nTotal: {total_issues} issue(s)")
        return 1
    print(
        f"PASS  api-coverage  {percent:.1f}% "
        f"({covered_count}/{total} names checked)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
