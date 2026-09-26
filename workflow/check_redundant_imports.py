# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Check and fix manim star imports.

Convention: ``from manim import *`` (and ``from manim.<sub> import *``)
is not allowed outside ``__init__.py`` files (which keep star imports
for re-exports). Explicit imports are required instead — they also rid
the codebase of flake8 F403/'unable to detect undefined names' noise.

Two modes:
  check (default) - detect files using star imports.
  fix             - replace star imports with explicit imports of the
                    names actually used in the file.

Usage:
    python check_redundant_imports.py
    python check_redundant_imports.py --fix
"""

import argparse
import ast
import importlib
import sys
from pathlib import Path

STAR_IMPORT_MODULES = ("manim",)


def is_star_import(node):
    return (
        isinstance(node, ast.ImportFrom)
        and node.module is not None
        and any(node.module == m or node.module.startswith(m + ".") for m in STAR_IMPORT_MODULES)
        and any(alias.name == "*" for alias in node.names)
    )


def get_star_exports(module_name):
    """Names a 'from <module_name> import *' would bind."""
    try:
        mod = importlib.import_module(module_name)
    except Exception:
        return set()
    names = set(getattr(mod, "__all__", None) or [])
    if not names:
        names = {n for n in dir(mod) if not n.startswith("_")}
    return names


def find_star_imports(source, filepath="<unknown>"):
    """Return (has_star, [star ImportFrom nodes]) for non-init files."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        # Hard-fail instead of skipping: a parse error must not silently
        # disable the star-import check for a whole file.
        raise SystemExit(f"{filepath}: syntax error: {exc}")
    nodes = [n for n in ast.walk(tree) if is_star_import(n)]
    return bool(nodes), nodes


def collect_used_names(source):
    """All names referenced (loaded) anywhere in the module, minus names
    bound at module level (a module-level assignment/def/class would
    shadow any import of the same name)."""
    tree = ast.parse(source)
    import symtable

    try:
        module_table = symtable.symtable(source, "<file>", "exec")
    except Exception:
        module_table = None

    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            root = node
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name):
                used.add(root.id)

    if module_table is not None:
        for name in list(used):
            try:
                if module_table.lookup(name).is_local():
                    used.discard(name)
            except KeyError:
                pass
    return used


def fix_star_imports(source, filepath):
    """Replace star imports with explicit imports of used names.

    Returns (new_source, num_fixed).
    """
    if "__init__.py" in Path(filepath).name:
        return source, 0
    has_star, star_nodes = find_star_imports(source, filepath)
    if not has_star:
        return source, 0

    used = collect_used_names(source)
    lines = source.splitlines(keepends=False)
    replacements = {}  # start lineno -> list of replacement lines
    claimed = set()

    for node in sorted(star_nodes, key=lambda n: n.lineno):
        exports = get_star_exports(node.module)
        names = sorted((used - claimed) & exports)
        claimed |= set(names)
        indent = " " * node.col_offset
        if names:
            # one name per continuation line to stay readable and
            # well under the line-length limit
            if len(", ".join(names)) <= 76 - len(indent) - len(node.module):
                new_line = indent + f"from {node.module} import " + ", ".join(names)
            else:
                inner = indent + " " * 4
                new_line = (
                    indent + f"from {node.module} import (\n"
                    + ",\n".join(inner + n for n in names)
                    + ",\n" + indent + ")"
                )
            replacements[node.lineno] = new_line
        else:
            replacements[node.lineno] = None  # remove
        # blank out any continuation lines of a multi-line import
        for ln in range(node.lineno + 1, (node.end_lineno or node.lineno) + 1):
            replacements[ln] = None

    new_lines = []
    for i, line in enumerate(lines, 1):
        if i in replacements:
            rep = replacements[i]
            if rep is not None:
                new_lines.append(rep)
        else:
            new_lines.append(line)
    new_source = "\n".join(new_lines)
    if source.endswith("\n"):
        new_source += "\n"
    try:
        ast.parse(new_source)
    except SyntaxError as e:
        print(f"  ERROR: {filepath}: fix would produce invalid Python: {e}", file=sys.stderr)
        return source, 0
    return new_source, len(star_nodes)


def check_file(filepath):
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception:
        return None
    if "__init__.py" in filepath.name:
        return None
    has_star, nodes = find_star_imports(source, filepath)
    if not has_star:
        return None
    return [(n.lineno, n.module) for n in sorted(nodes, key=lambda n: n.lineno)]


def main():
    parser = argparse.ArgumentParser(
        description="Check and fix manim star imports (banned outside __init__.py)."
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Replace star imports with explicit imports of used names",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be changed without writing files",
    )
    parser.add_argument(
        "paths", nargs="*",
        help="Specific files/dirs to check (default: manim_extensions, tests, workflow, docs)",
    )
    args = parser.parse_args()

    root = Path(".")
    if args.paths:
        targets = []
        for p in args.paths:
            path = Path(p)
            if path.is_dir():
                targets.extend(sorted(path.rglob("*.py")))
            elif path.is_file():
                targets.append(path)
    else:
        targets = []
        for base in ("manim_extensions", "tests", "workflow", "docs"):
            b = Path(base)
            if b.exists():
                targets.extend(sorted(b.rglob("*.py")))

    targets = [
        t for t in targets
        if "__pycache__" not in str(t) and ".git" not in str(t)
        and "__init__.py" not in t.name
    ]

    issues_found = 0
    fixed_count = 0

    for target in sorted(targets):
        rel = target.relative_to(root) if target.is_relative_to(root) else target
        issues = check_file(target)
        if not issues:
            continue
        issues_found += 1
        print(f"\n{'='*70}")
        print(f"FILE: {rel}")
        print(f"{'='*70}")
        for lineno, module in issues:
            print(f"  line {lineno}: from {module} import *")

        if args.fix:
            source = target.read_text(encoding="utf-8")
            new_source, num = fix_star_imports(source, target)
            if num and new_source != source:
                if not args.dry_run:
                    target.write_text(new_source, encoding="utf-8")
                print(f"  {'Would fix' if args.dry_run else 'Fixed'} {num} star import(s)")
                fixed_count += 1

    print(f"\n{'='*70}")
    if issues_found == 0:
        print("No star imports found.")
    else:
        action = "would fix" if args.dry_run else "fixed"
        print(f"Files with star imports: {issues_found}")
        if args.fix:
            print(f"Files {action}: {fixed_count}")
    print(f"{'='*70}")

    return 0 if issues_found == 0 or args.fix else 1


if __name__ == "__main__":
    sys.exit(main())
