"""Check and fix redundant/manual manim imports.

Two modes:
  check (default) - detect files that have explicit manim imports
                    without `from manim import *`, or have redundant
                    imports after `from manim import *`.
  fix             - auto-convert explicit manim imports to
                    `from manim import *`, preserving imports of
                    names not covered by star exports.
"""

import ast
import re
import sys
import argparse
from pathlib import Path


def get_manim_star_exports():
    try:
        import manim
        names = set()
        if hasattr(manim, "__all__"):
            names.update(manim.__all__)
        for attr in dir(manim):
            if not attr.startswith("_"):
                names.add(attr)
        return names
    except ImportError:
        return set()


def collect_import_blocks(source: str):
    """Collect manim import statement blocks with full line ranges.

    Returns:
        has_star: bool - whether `from manim import *` exists
        blocks: list of dicts with keys:
            start, end (inclusive), module, names, covered, uncovered
    """
    star_exports = get_manim_star_exports()
    has_star = False
    blocks = []

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "manim" or module.startswith("manim."):
                covered = []
                uncovered = []
                for alias in node.names:
                    if alias.name == "*" and module == "manim":
                        has_star = True
                    elif alias.name == "*":
                        pass
                    else:
                        name = alias.name
                        in_star = name in star_exports if star_exports else False
                        if in_star:
                            covered.append(name)
                        else:
                            uncovered.append(name)

                if node.lineno is None:
                    continue

                end_lineno = getattr(node, "end_lineno", node.lineno)
                blocks.append({
                    "start": node.lineno,
                    "end": end_lineno if end_lineno else node.lineno,
                    "module": module,
                    "names": [alias.name for alias in node.names if alias.name != "*"],
                    "covered": covered,
                    "uncovered": uncovered,
                })

    return has_star, blocks


def find_issues_in_file(filepath: Path):
    """Detect import issues in a Python file.

    Returns dict with keys:
        has_star: whether `from manim import *` is present
        blocks: list of import block dicts
        needs_fix: bool
    """
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    star_exports = get_manim_star_exports()
    if not star_exports:
        return None

    has_star, blocks = collect_import_blocks(source)

    result = {
        "path": filepath,
        "has_star": has_star,
        "blocks": blocks,
        "needs_fix": False,
    }

    if has_star:
        result["needs_fix"] = any(b["covered"] for b in blocks)
    else:
        result["needs_fix"] = any(b["covered"] or b["uncovered"] for b in blocks)

    return result


def _is_initial_comment_or_docstring(lines, idx):
    """Check if lines up to idx are only comments, blank lines, or docstrings."""
    in_docstring = False
    docstring_char = None
    for i in range(idx):
        stripped = lines[i].strip()
        if in_docstring:
            if docstring_char in stripped and not stripped.startswith(docstring_char):
                in_docstring = False
            elif stripped.endswith(docstring_char) and len(stripped) >= 3:
                in_docstring = False
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        for dq in ('"""', "'''"):
            if stripped.startswith(dq):
                if stripped.count(dq) >= 2 and len(stripped) >= 6:
                    pass
                else:
                    in_docstring = True
                    docstring_char = dq
                break
        else:
            return False
    return True


def _find_insertion_point(lines):
    """Find the best position to insert `from manim import *`.

    Returns the index (0-based) where the star import should be inserted.
    Skips comments, blank lines, and module docstrings.
    """
    insert_idx = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        if in_docstring:
            if docstring_char in stripped[1:] if len(stripped) > 1 else False:
                in_docstring = False
                docstring_char = None
            elif stripped.endswith(docstring_char) and len(stripped) >= 3:
                in_docstring = False
                docstring_char = None
            continue

        if not stripped:
            insert_idx = i + 1
            continue

        if stripped.startswith("#"):
            insert_idx = i + 1
            continue

        for dq in ('"""', "'''"):
            if stripped.startswith(dq):
                in_docstring = True
                docstring_char = dq
                insert_idx = i
                if stripped.count(dq) >= 2 and len(stripped) >= 6:
                    in_docstring = False
                    docstring_char = None
                break
        else:
            if stripped.startswith("from __future__") or stripped.startswith("from typing"):
                insert_idx = i + 1
                continue
            if stripped.startswith("import ") or stripped.startswith("from "):
                insert_idx = i
                break
            insert_idx = i
            break

    return insert_idx


def fix_file(filepath: Path, dry_run: bool = False):
    """Fix import issues in a Python file.

    Returns (success, messages) tuple.
    """
    result = find_issues_in_file(filepath)
    if result is None or not result["needs_fix"]:
        return True, []

    messages = []
    source = filepath.read_text(encoding="utf-8")
    lines = source.split("\n")

    has_star = result["has_star"]
    blocks = result["blocks"]

    remove_ranges = set()
    all_uncovered = {}

    for block in blocks:
        is_star_line = (
            block["start"] == block["end"]
            and block["module"] == "manim"
            and len(block["names"]) == 0
        )
        if is_star_line:
            continue
        if block["covered"] or block["uncovered"]:
            for line_no in range(block["start"], block["end"] + 1):
                remove_ranges.add(line_no)
        for name in block["uncovered"]:
            mod = block["module"]
            if mod not in all_uncovered:
                all_uncovered[mod] = set()
            all_uncovered[mod].add(name)

    new_lines = []
    star_inserted = False
    star_done = has_star

    for i, line in enumerate(lines, 1):
        if i in remove_ranges:
            stripped = line.strip()
            messages.append(f"  Removed line {i}: {stripped}")
            continue

        if not star_done and not star_inserted:
            stripped = line.strip()
            is_manim_import = (
                stripped.startswith("from manim.") or
                stripped.startswith("from manim import")
            )
            is_future = stripped.startswith("from __future__")
            is_typing = stripped.startswith("from typing")

            is_initial_comment_or_doc = (
                not stripped
                or stripped.startswith("#")
                or stripped.startswith('"""')
                or stripped.startswith("'''")
            )

            if not is_manim_import and not is_future and not is_typing:
                if not is_initial_comment_or_doc:
                    new_lines.append("from manim import *")
                    if all_uncovered:
                        for module, names in sorted(all_uncovered.items()):
                            name_list = ", ".join(sorted(names))
                            if module == "manim":
                                new_lines.append(f"from manim import {name_list}")
                            else:
                                new_lines.append(f"from {module} import {name_list}")
                    star_done = True
                    star_inserted = True
                    new_lines.append(line)
                    continue

        new_lines.append(line)

    if not star_done:
        insert_idx = _find_insertion_point(new_lines)

        new_lines.insert(insert_idx, "from manim import *")
        if all_uncovered:
            offset = insert_idx + 1
            for module, names in sorted(all_uncovered.items()):
                name_list = ", ".join(sorted(names))
                if module == "manim":
                    new_lines.insert(offset, f"from manim import {name_list}")
                else:
                    new_lines.insert(offset, f"from {module} import {name_list}")
                offset += 1
        messages.append(f"  Added `from manim import *`")

    new_source = "\n".join(new_lines)

    try:
        ast.parse(new_source)
    except SyntaxError as e:
        messages.append(f"  ERROR: Would produce invalid Python: {e}")
        return False, messages

    if not dry_run:
        filepath.write_text(new_source, encoding="utf-8")
        messages.append(f"  Fixed and written to {filepath}")

    return True, messages


def find_manim_code_blocks(source: str):
    """Find .. manim:: code blocks in RST source and check imports."""
    blocks = []
    lines = source.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if re.match(r"^\.\.\s+manim::\s*", stripped):
            i += 1
            while i < len(lines) and lines[i].strip() == "":
                i += 1
            start_line = i + 1
            block_lines = []
            while i < len(lines):
                current = lines[i]
                if current.strip() == "":
                    block_lines.append(current)
                    i += 1
                    continue
                if not current.startswith("   "):
                    break
                block_lines.append(current[3:])
                i += 1

            dedented = _dedent_block(block_lines)
            block_source = "\n".join(dedented)
            trimmed = _trim_to_valid_python(block_source)
            if trimmed.strip():
                blocks.append((trimmed, start_line))
        else:
            i += 1

    return blocks


def _trim_to_valid_python(block_source: str):
    lines = block_source.split("\n")
    for end in range(len(lines), 0, -1):
        candidate = "\n".join(lines[:end])
        try:
            ast.parse(candidate)
            return candidate
        except SyntaxError:
            continue
    return ""


def _dedent_block(block_lines):
    non_empty = [l for l in block_lines if l.strip()]
    if not non_empty:
        return block_lines
    min_indent = min(
        len(l) - len(l.lstrip(" "))
        for l in non_empty
    )
    if min_indent == 0:
        return block_lines
    return [l[min_indent:] if len(l) >= min_indent else l for l in block_lines]


def check_rst_file(filepath: Path):
    """Check RST files for manim code blocks with import issues."""
    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    blocks = find_manim_code_blocks(source)
    issues = []

    for block_source, start_line in blocks:
        try:
            has_star, block_imports = collect_import_blocks(block_source)
            if not has_star and block_imports:
                for block in block_imports:
                    if block["covered"] or block["uncovered"]:
                        issues.append({
                            "start_line": start_line,
                            "has_star": has_star,
                            "block": block,
                        })
        except SyntaxError:
            pass

    return issues if issues else None


def main():
    parser = argparse.ArgumentParser(
        description="Check and fix manim import style consistency."
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Auto-fix imports to use `from manim import *`"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be changed without writing files"
    )
    parser.add_argument(
        "--rst", action="store_true",
        help="Also check RST files for manim code block issues"
    )
    parser.add_argument(
        "paths", nargs="*",
        help="Specific files/dirs to check (default: entire project)"
    )
    args = parser.parse_args()

    star_exports = get_manim_star_exports()
    if not star_exports:
        print("WARNING: Could not import manim to detect star exports.")
        print("Run this from an environment with manim installed.")
        return 1

    root = Path(".")
    if args.paths:
        targets = []
        for p in args.paths:
            path = Path(p)
            if path.is_dir():
                targets.extend(sorted(path.rglob("*.py")))
                if args.rst:
                    targets.extend(sorted(path.rglob("*.rst")))
            elif path.is_file():
                targets.append(path)
    else:
        targets = list(root.rglob("*.py"))
        if args.rst:
            targets.extend(sorted(root.rglob("*.rst")))

    targets = [
        t for t in targets
        if "__pycache__" not in str(t) and ".git" not in str(t)
    ]

    issues_found = 0
    fixed_count = 0
    error_count = 0

    for target in sorted(targets):
        rel_path = target.relative_to(root)

        if target.suffix == ".rst":
            if not args.rst:
                continue
            issues = check_rst_file(target)
            if issues:
                issues_found += 1
                print(f"\n{'='*70}")
                print(f"FILE: {rel_path}")
                print(f"{'='*70}")
                for issue in issues:
                    block = issue["block"]
                    print(f"  Line {issue['start_line']}: "
                          f"{len(block['covered'])} covered + {len(block['uncovered'])} uncovered")
                    for name in block["covered"]:
                        print(f"    from {block['module']} import {name}  [covered by star]")
                    for name in block["uncovered"]:
                        print(f"    from {block['module']} import {name}  [NOT covered]")
            continue

        result = find_issues_in_file(target)

        if result is None:
            continue

        if not result["needs_fix"]:
            continue

        issues_found += 1
        print(f"\n{'='*70}")
        print(f"FILE: {rel_path}")
        print(f"{'='*70}")

        if result["has_star"]:
            print(f"  Already has `from manim import *`, but has redundant imports:")
            for block in result["blocks"]:
                if block["covered"]:
                    for name in block["covered"]:
                        print(f"    Line {block['start']}-{block['end']}: "
                              f"from {block['module']} import {name}")
        else:
            covered_total = sum(len(b["covered"]) for b in result["blocks"])
            uncovered_total = sum(len(b["uncovered"]) for b in result["blocks"])
            print(f"  No `from manim import *`. Has {covered_total} covered + {uncovered_total} uncovered imports:")
            for block in result["blocks"]:
                for name in block["covered"]:
                    print(f"    Line {block['start']}-{block['end']}: "
                          f"from {block['module']} import {name}  [covered by star]")
                for name in block["uncovered"]:
                    print(f"    Line {block['start']}-{block['end']}: "
                          f"from {block['module']} import {name}  [NOT covered, must stay explicit]")

        if args.fix:
            success, messages = fix_file(target, dry_run=args.dry_run)
            for msg in messages:
                print(msg)
            if success:
                fixed_count += 1
            else:
                error_count += 1

    print(f"\n{'='*70}")
    if issues_found == 0:
        print("No import style issues found.")
    else:
        print(f"Total files with issues: {issues_found}")
        if args.fix:
            action = "would fix" if args.dry_run else "fixed"
            print(f"Files {action}: {fixed_count}")
            if error_count:
                print(f"Files with errors: {error_count}")
    print(f"{'='*70}")

    return 0 if issues_found == 0 or args.fix else 1


if __name__ == "__main__":
    sys.exit(main())