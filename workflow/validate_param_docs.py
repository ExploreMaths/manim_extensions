# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate that class constructor parameters are documented in the class docstring.

Rules:
    - Parameter documentation MUST be in the class docstring (not in __init__).
    - Every parameter in __init__ (except ``self`` and bare ``*args``) MUST
      have a corresponding entry in the class docstring's numpydoc
      ``Parameters`` section.
    - The __init__ docstring should only be a brief description, not full
      param docs.

The checker is AST-based, so it handles classes whose ``__init__`` is not the
first method, multi-line signatures, keyword-only parameters, and nested
classes. Numpydoc sections are detected by their ``----------`` underline, so
free-form description lines (e.g. "A Manim color") cannot be mistaken for
section headers.

Violations may be exempted via ``workflow/param_docs_exemptions.json``, which
maps a repository-relative file path to a list of qualified class names. This
is intended mainly for vendored subpackages that are kept in sync with
upstream projects.

Usage:
    python validate_param_docs.py [directory ...]
    python validate_param_docs.py --write-exemptions

If no directory is given, scans ``manim_extensions/`` by default.
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXEMPTIONS_FILE = Path(__file__).resolve().parent / "param_docs_exemptions.json"

SKIP_FILES = {'__init__.py'}

SKIP_CLASSES = {'ABC'}

KNOWN_NO_PARAMS = {
    'ManimAnimations',
    'ManimTuringMachine',
    'PushDownAutomatonRule',
}

PARAM_ENTRY_RE = re.compile(r"^(\*{0,2}[\w.]+)\s*:(?!:)\s*(.*)$")
BARE_ENTRY_RE = re.compile(r"^(\*{0,2}[\w.]+)$")
SECTION_UNDERLINE_RE = re.compile(r"^\s*-{3,}\s*$")


def find_init(node: ast.ClassDef) -> ast.FunctionDef | None:
    """Return the class's own ``__init__`` method, or None."""
    return next(
        (item for item in node.body
         if isinstance(item, ast.FunctionDef) and item.name == "__init__"),
        None,
    )


def required_params(init: ast.FunctionDef) -> list:
    """Return constructor parameter names that must be documented.

    ``self`` and bare ``*args`` are conventionally undocumented; ``**kwargs``
    is required as an entry named ``kwargs``.
    """
    params = [
        a.arg
        for a in init.args.posonlyargs + init.args.args + init.args.kwonlyargs
        if a.arg != "self"
    ]
    if init.args.kwarg:
        params.append(init.args.kwarg.arg)
    return params


def documented_params(docstring: str) -> set:
    """Extract parameter names documented in a numpydoc Parameters section.

    A line only counts as a section header when it is followed by a
    ``----------`` underline, so description text like "A Manim color" is
    never mistaken for a header.
    """
    params = set()
    if not docstring:
        return params
    lines = docstring.splitlines()
    in_params = False
    item_indent = None
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not in_params:
            if (
                stripped == "Parameters"
                and idx + 1 < len(lines)
                and SECTION_UNDERLINE_RE.match(lines[idx + 1])
            ):
                in_params = True
                item_indent = None
            continue
        if not stripped:
            continue
        if SECTION_UNDERLINE_RE.match(stripped):
            continue  # section underline itself (first line after the header)
        indent = len(line) - len(line.lstrip(" \t"))
        if item_indent is None:
            item_indent = indent
        if indent < item_indent:
            in_params = False  # dedented past the entries: section ended
            continue
        if indent > item_indent:
            continue  # continuation line of the previous entry
        # An underlined header line (e.g. the next section) ends Parameters.
        if (
            idx + 1 < len(lines)
            and SECTION_UNDERLINE_RE.match(lines[idx + 1])
        ):
            in_params = False
            continue
        m = PARAM_ENTRY_RE.match(stripped)
        if m:
            params.add(m.group(1).lstrip("*"))
        elif BARE_ENTRY_RE.match(stripped):
            params.add(stripped.lstrip("*"))
    return params


def init_docstring_has_params(docstring: str) -> bool:
    """Check if the __init__ docstring contains parameter documentation."""
    if not docstring:
        return False
    has_params_section = bool(
        re.search(r"^Parameters\s*$", docstring, re.MULTILINE)
    )
    # "name : type" content lines, where the type looks like a type
    # (uppercase/class reference/builtin) — this avoids matching prose
    # such as "TODO: add docstring for __init__.".
    has_param_content = bool(
        re.search(
            r"^\*{0,2}[\w.]+\s*:\s*(?:[A-Z`]~|(?:str|int|float|bool|list|"
            r"dict|tuple|set|None)\b)",
            docstring,
            re.MULTILINE,
        )
    )
    return has_params_section or has_param_content


def check_file(file_path: Path) -> list:
    """Check a single file for parameter documentation issues."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        # Hard-fail instead of skipping: a parse error must not disable
        # the parameter checks for a whole file.
        return [f"<syntax error: {exc}>"]

    issues = []

    def visit(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                check_class(child, prefix)
                visit(child, f"{prefix}{child.name}.")
            else:
                visit(child, prefix)

    def check_class(node: ast.ClassDef, prefix: str) -> None:
        class_name = node.name
        if class_name in SKIP_CLASSES or class_name in KNOWN_NO_PARAMS:
            return
        if class_name.startswith("_"):
            return
        qualname = f"{prefix}{class_name}"
        init = find_init(node)
        if init is None:
            return  # no own __init__; nothing to document here

        init_doc = ast.get_docstring(init) or ""
        if init_doc and init_docstring_has_params(init_doc):
            issues.append({
                'type': 'INIT_HAS_PARAM_DOCS',
                'line': node.lineno,
                'class_name': qualname,
                'message': (
                    '__init__ docstring contains parameter documentation. '
                    'Move it to the class docstring.'
                ),
            })

        params = required_params(init)
        documented = documented_params(ast.get_docstring(node) or "")

        for param in params:
            if param not in documented:
                issues.append({
                    'type': 'MISSING_PARAM_DOC',
                    'line': node.lineno,
                    'class_name': qualname,
                    'message': f"Parameter '{param}' not documented "
                               f"in class docstring.",
                })

    visit(tree, "")
    return issues


def load_exemptions() -> dict:
    """Load the exemptions JSON; return {relative_path: set(qualnames)}."""
    if not EXEMPTIONS_FILE.exists():
        return {}
    data = json.loads(EXEMPTIONS_FILE.read_text(encoding="utf-8"))
    return {path: set(names) for path, names in data.items()}


def collect_files(targets: list) -> list:
    """Resolve CLI targets to a sorted list of Python files."""
    py_files = []
    for target in targets:
        path = Path(target)
        if path.is_file() and path.suffix == '.py':
            py_files.append(path)
        elif path.is_dir():
            py_files.extend(path.rglob('*.py'))
    return sorted(set(py_files))


def main() -> int:
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate that __init__ parameters are documented in the "
                    "class docstring; optionally (re)write the exemptions file."
    )
    parser.add_argument(
        "targets", nargs="*",
        help="Files or directories to scan (default: manim_extensions/)",
    )
    parser.add_argument(
        "--write-exemptions", action="store_true",
        help="Write ALL current violations to the exemptions file. "
             "This blesses the current state — review the diff carefully.",
    )
    args = parser.parse_args()

    targets = args.targets or [str(ROOT / 'manim_extensions')]
    py_files = [
        fp for fp in collect_files(targets) if fp.name not in SKIP_FILES
    ]

    all_issues = {}
    for fp in py_files:
        issues = check_file(fp)
        if issues:
            all_issues[fp] = issues

    if args.write_exemptions:
        data = {}
        for fp, issues in all_issues.items():
            rel = fp.resolve().relative_to(ROOT).as_posix()
            data[rel] = sorted({i['class_name'] for i in issues})
        EXEMPTIONS_FILE.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        total = sum(len(v) for v in data.values())
        print(f"Wrote {total} exempted classes for {len(data)} files to "
              f"{EXEMPTIONS_FILE.name}. Review the diff before committing!")
        return 0

    exemptions = load_exemptions()
    unexempted = {}
    for fp, issues in all_issues.items():
        rel = fp.resolve().relative_to(ROOT).as_posix()
        exempt = exemptions.get(rel, set())
        leftover = [i for i in issues if i['class_name'] not in exempt]
        if leftover:
            unexempted[rel] = leftover

    print("=" * 70)
    print("PARAMETER DOCUMENTATION VALIDATOR")
    print("=" * 70)
    print(f"\nFiles scanned:           {len(py_files)}")

    if unexempted:
        total_issues = sum(len(v) for v in unexempted.values())
        print(f"\nISSUES FOUND: {total_issues}\n")
        print("-" * 70)
        for fp, issues in unexempted.items():
            print(f"\nFILE: {fp}")
            for issue in issues:
                if issue['type'] == 'INIT_HAS_PARAM_DOCS':
                    icon = "PARAMS IN __init__ (move to class docstring)"
                else:
                    icon = "MISSING PARAM DOC (add to class docstring)"
                print(f"  Line {issue['line']:4d} | {icon}")
                print(f"         Class: {issue['class_name']}")
                print(f"         {issue['message']}")
        print("\n" + "=" * 70)
        print(f"VALIDATION FAILED - {total_issues} issue(s) found")
        print("=" * 70)
        return 1

    print("\nAll parameter documentation is correct!")
    print("=" * 70)
    print("VALIDATION PASSED")
    print("=" * 70)
    return 0


if __name__ == '__main__':
    sys.exit(main())
