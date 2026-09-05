"""Check and fix intra-package absolute imports.

Every import that targets a module inside the ``manim_extensions`` package
can (and should) be written as a relative import. This includes vendored
third-party modules that still import themselves under their upstream
package name:

  manim_arabic     -> manim_extensions.arabic
  manim_chemistry  -> manim_extensions.chemistry
  manim_ml         -> manim_extensions.machine_learning
  manim_pymunk     -> manim_extensions.pymunk

Docstring examples (e.g. ``from manim_extensions import Table`` shown to
users) are ignored: only real import statements are analysed.

Two modes:
  check (default) - report convertible imports and exit non-zero if any
                    are found.
  fix             - rewrite them as relative imports.
"""

import argparse
import ast
import sys
from pathlib import Path

PACKAGE_NAME = "manim_extensions"

# Upstream package names of vendored subpackages -> vendored path parts.
# Only converted when the importing file lives inside that subtree.
VENDORED_ALIASES = {
    "manim_arabic": ("arabic",),
    "manim_chemistry": ("chemistry",),
    "manim_ml": ("machine_learning",),
    "manim_pymunk": ("pymunk",),
}


def file_module_parts(filepath: Path):
    """Dotted package parts of the *package* containing ``filepath``.

    For ``manim_extensions/pymunk/space/VSpace.py`` this returns
    ``["manim_extensions", "pymunk", "space"]``; for an ``__init__.py``
    it returns the parts of the package itself.
    """
    rel = filepath.relative_to(Path(PACKAGE_NAME))
    parts = list(rel.parts[:-1])
    if rel.name != "__init__.py":
        parts.append(rel.stem)
    return [PACKAGE_NAME, *parts]


def package_parts_of_file(filepath: Path):
    """Parts of the package that the file belongs to."""
    rel = filepath.relative_to(Path(PACKAGE_NAME))
    if rel.name == "__init__.py":
        return [PACKAGE_NAME, *list(rel.parts[:-1])]
    return [PACKAGE_NAME, *list(rel.parts[:-1])]


def resolve_target(module: str, filepath: Path):
    """Resolve an imported absolute module path to in-package parts.

    Returns a tuple ``(parts, alias_used)`` where ``parts`` is the full
    dotted module path inside ``manim_extensions``, or ``None`` when the
    import does not target a vendored/in-package module.
    """
    top = module.split(".")[0]
    if top == PACKAGE_NAME:
        return tuple(module.split(".")), None
    if top in VENDORED_ALIASES:
        alias_root = VENDORED_ALIASES[top]
        # Only convert when the importing file is inside that subtree.
        rel_parts = filepath.relative_to(Path(PACKAGE_NAME)).parts
        if rel_parts[: len(alias_root)] == alias_root:
            return (PACKAGE_NAME, *alias_root, *module.split(".")[1:]), top
    return None, None


def module_exists(parts):
    """Check whether a module path inside the package exists on disk."""
    base = Path(*parts)
    return (base.with_suffix(".py")).exists() or (base / "__init__.py").exists()


def to_relative(pkg_parts, target_parts):
    """Compute (level, remaining_module) for a relative import."""
    common = 0
    for a, b in zip(pkg_parts, target_parts):
        if a != b:
            break
        common += 1
    level = len(pkg_parts) - common + 1
    remaining = ".".join(target_parts[common:])
    return level, remaining


def format_relative_import(level, module, names):
    """Render a relative ``from ... import ...`` statement."""
    dots = "." * level
    prefix = f"from {dots}{module}" if module else f"from {dots}"
    rendered = ", ".join(
        f"{n.name} as {n.asname}" if n.asname else n.name for n in names
    )
    return f"{prefix} import {rendered}"


def analyse_file(filepath: Path):
    """Return a list of issue dicts for one file."""
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception:
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    pkg_parts = package_parts_of_file(filepath)
    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                continue  # already relative
            if not node.module:
                continue
            target_parts, alias = resolve_target(node.module, filepath)
            if target_parts is None:
                continue
            if not module_exists(target_parts):
                issues.append({
                    "kind": "missing-target",
                    "lineno": node.lineno,
                    "original": f"from {node.module} import ...",
                    "detail": f"resolved target {'.'.join(target_parts)} not found",
                })
                continue
            level, remaining = to_relative(pkg_parts, target_parts)
            names = [("*" if a.name == "*" else a.name) for a in node.names]
            issues.append({
                "kind": "import-from",
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "col_offset": node.col_offset,
                "module": node.module,
                "alias": alias,
                "level": level,
                "remaining": remaining,
                "names": names,
                "original": f"from {node.module} import {', '.join(names)}",
                "replacement": format_relative_import(
                    level, remaining, node.names
                ),
            })
        elif isinstance(node, ast.Import):
            for alias_node in node.names:
                target_parts, alias = resolve_target(alias_node.name, filepath)
                if target_parts is None:
                    continue
                if not module_exists(target_parts):
                    issues.append({
                        "kind": "missing-target",
                        "lineno": node.lineno,
                        "original": f"import {alias_node.name}",
                        "detail": f"resolved target {'.'.join(target_parts)} not found",
                    })
                    continue
                imported_parts = tuple(alias_node.name.split("."))
                bound_name = alias_node.asname or imported_parts[0]
                is_alias_root = (
                    alias is not None and imported_parts == (alias,)
                )
                if alias_node.asname is None and not is_alias_root:
                    # `import a.b.c` binds the top-level name `a`; the
                    # relative equivalent needs manual judgement.
                    issues.append({
                        "kind": "plain-import",
                        "lineno": node.lineno,
                        "original": f"import {alias_node.name}",
                        "detail": "plain import without alias needs manual conversion",
                    })
                    continue
                level, remaining = to_relative(pkg_parts, target_parts)
                dots = "." * level
                leaf = target_parts[-1]
                if alias_node.asname:
                    # import x.y.z as name -> from <dots>[.y] import z [as name]
                    if remaining and remaining != leaf:
                        mod_part, leaf_part = remaining.rsplit(".", 1)
                        replacement = (
                            f"from {dots}{mod_part} import {leaf_part}"
                        )
                        if alias_node.asname != leaf_part:
                            replacement += f" as {alias_node.asname}"
                    else:
                        replacement = f"from {dots} import {leaf}"
                        if alias_node.asname != leaf:
                            replacement += f" as {alias_node.asname}"
                else:
                    # import <alias_root> -> from <dots> import <leaf> as <alias>
                    replacement = f"from {dots}{remaining} import {leaf} as {bound_name}"
                issues.append({
                    "kind": "plain-import-fixable",
                    "lineno": node.lineno,
                    "end_lineno": getattr(node, "end_lineno", node.lineno),
                    "col_offset": node.col_offset,
                    "original": f"import {alias_node.name}"
                                + (f" as {alias_node.asname}" if alias_node.asname else ""),
                    "replacement": replacement,
                })
    issues.sort(key=lambda i: i["lineno"])
    return issues


def fix_file(filepath: Path, issues, dry_run=False):
    """Rewrite convertible imports in one file, bottom-up by line."""
    source = filepath.read_text(encoding="utf-8")
    lines = source.split("\n")
    messages = []
    for issue in sorted(issues, key=lambda i: i["lineno"], reverse=True):
        if issue["kind"] not in ("import-from", "plain-import-fixable"):
            continue
        start = issue["lineno"] - 1
        end = issue.get("end_lineno", issue["lineno"]) - 1
        block = "\n".join(lines[start:end + 1])
        indent = block[: len(block) - len(block.lstrip(" "))]
        new_block = indent + issue["replacement"]
        if not dry_run:
            lines[start:end + 1] = [new_block]
        messages.append(
            f"  L{issue['lineno']}: {issue['original'].strip()}\n"
            f"      -> {issue['replacement'].strip()}"
        )
    if not dry_run and messages:
        new_source = "\n".join(lines)
        ast.parse(new_source)  # safety: must stay valid Python
        filepath.write_text(new_source, encoding="utf-8")
    return messages


def main():
    parser = argparse.ArgumentParser(
        description="Check that all in-package imports use relative imports."
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Auto-fix convertible imports to relative imports",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="With --fix, show changes without writing files",
    )
    args = parser.parse_args()

    root = Path(PACKAGE_NAME)
    if not root.is_dir():
        print(f"ERROR: {PACKAGE_NAME}/ package directory not found.")
        return 1

    targets = sorted(
        p for p in root.rglob("*.py") if "__pycache__" not in p.parts
    )

    files_with_issues = 0
    fixable = 0
    manual = 0
    for filepath in targets:
        issues = analyse_file(filepath)
        if not issues:
            continue
        files_with_issues += 1
        print(f"\n{filepath}")
        for issue in issues:
            if issue["kind"] == "missing-target":
                manual += 1
                print(f"  L{issue['lineno']}: BROKEN? {issue['original']}")
                print(f"      {issue['detail']}")
            elif issue["kind"] in ("plain-import",):
                manual += 1
                print(f"  L{issue['lineno']}: MANUAL {issue['original']}")
                print(f"      {issue['detail']}")
            else:
                fixable += 1
                print(f"  L{issue['lineno']}: {issue['original'].strip()}")
                print(f"      -> {issue['replacement'].strip()}")
        if args.fix:
            for msg in fix_file(filepath, issues, dry_run=args.dry_run):
                print(msg)

    print("\n" + "=" * 70)
    if files_with_issues == 0:
        print("All in-package imports already use relative imports. OK.")
        return 0
    print(f"Files with convertible imports: {files_with_issues}")
    print(f"Auto-fixable statements: {fixable}, needs manual review: {manual}")
    if args.fix:
        print("Applied fixes (dry-run)." if args.dry_run else "Applied fixes.")
        return 1 if manual else 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
