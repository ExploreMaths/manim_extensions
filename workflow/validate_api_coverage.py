# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Verify every public constant, function, and class is API-documented,
and maintain the snapshot that ``autodoc_all``'s ``:missing-only:`` mode
filters against.

Scans the whole ``manim_extensions`` package for public names (same
rules as the ``autodoc_all`` extension: ``__all__`` when defined, else
names defined in the module itself), then resolves every
``autoclass`` / ``autofunction`` / ``autodata`` / ``autoall`` directive
in ``docs/source`` and matches by canonical defining-module dotted name.

A public name counts as documented when either
  * an explicit autodoc directive reaches it,
  * an ``.. autoall::`` block without ``:missing-only:`` enumerates it
    (its full expansion is injected into the docs at build time), or
  * an ``.. autoall::`` block with ``:missing-only:`` enumerates it
    (the block injects it into the docs at build time).

The snapshot (documented names only) is what ``:missing-only:`` blocks
filter against at Sphinx build time:

    python workflow/validate_api_coverage.py --write-snapshot

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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # pin the repo package over any installed copy
SRC = ROOT / "manim_extensions"
DOCS = ROOT / "docs" / "source"
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
IGNORED_PUBLIC_NAMES = {
    # Module-level singleton instance (manim_extensions.machine_learning);
    # skipped via ":skip: config" in reference/machine_learning/constants.rst.
    "manim_extensions.machine_learning.config",
}

DIRECTIVE_RE = re.compile(
    r"^\.\.\s+(autoclass|autofunction|autodata|autoall)::\s+(\S+)\s*$",
    re.MULTILINE,
)
OPTION_RE = re.compile(r"^\s+:(\w[\w-]*):\s*(.*)$")


def iter_modules():
    for info in pkgutil.walk_packages([str(SRC)], "manim_extensions."):
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
    """Yield (directive, target, options) for every autodoc directive."""
    for rst in sorted(DOCS.rglob("*.rst")):
        text = rst.read_text(encoding="utf-8")
        for match in DIRECTIVE_RE.finditer(text):
            directive, target = match.group(1), match.group(2)
            options = {}
            rest = text[match.end():]
            for line in rest.splitlines()[1:]:
                om = OPTION_RE.match(line)
                if not om:
                    break
                options[om.group(1)] = om.group(2).strip()
            yield rst, directive, target, options


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
        for t in (options.get("types") or "class function data").split(",")
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
    for rst, directive, target, options in parse_directives():
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
        if not mod or not mod.startswith("manim_extensions"):
            mod = target.rsplit(".", 1)[0]
        keys.add(f"{mod}.{target.rsplit('.', 1)[-1]}")
    return keys, warnings


def missing_only_coverage():
    """Canonical dotted names that :missing-only: autoall blocks inject."""
    keys = set()
    warnings = []
    for rst, directive, target, options in parse_directives():
        if directive != "autoall" or "missing-only" not in options:
            continue
        expanded, w = autoall_expansion_keys(target, options)
        keys |= expanded
        warnings.extend(f"{w_} ({rst.relative_to(ROOT)})" for w_ in w)
    return keys, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-snapshot",
        action="store_true",
        help=f"write the documented-names snapshot to {SNAPSHOT_PATH.relative_to(ROOT)}",
    )
    args = parser.parse_args()

    explicit, warnings = documented_keys()
    for w in warnings:
        print(f"WARNING: {w}")

    if args.write_snapshot:
        SNAPSHOT_PATH.write_text(
            json.dumps(sorted(explicit), indent=1) + "\n", encoding="utf-8"
        )
        print(f"Wrote {len(explicit)} documented names to {SNAPSHOT_PATH.relative_to(ROOT)}")
    else:
        if not SNAPSHOT_PATH.exists():
            print("WARNING: snapshot missing; run with --write-snapshot")
        else:
            on_disk = set(json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")))
            if on_disk != explicit:
                print(
                    "ERROR: api_documented.json is stale "
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
            total += 1
            key = defining_dotted(module, name, obj)
            if key not in covered and key not in IGNORED_PUBLIC_NAMES:
                missing.append(f"{module.__name__}.{name}")

    print(f"Public names checked: {total}")
    if missing:
        print(f"\nUndocumented public names ({len(missing)}):\n")
        for dotted in sorted(missing):
            print(f"  {dotted}")
        print(f"\nValidation failed: {len(missing)} public names lack API docs.")
        return 1
    print("\nEvery public constant, function, and class is API-documented.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
