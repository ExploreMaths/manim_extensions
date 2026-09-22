# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Validate numpydoc docstring sections and ``.. manim::`` examples.

This script checks that public functions, methods, and classes in
``manim_extensions`` follow the project's documentation conventions:

1. Functions/methods with parameters must have a numpydoc ``Parameters``
   section that documents every parameter (bare ``*args`` exempted).
2. Functions/methods with a non-``None`` return annotation must have a
   ``Returns`` (or ``Yields``) section.
3. Functions/methods that raise exceptions must have a ``Raises`` section
   that mentions every directly raised exception. The ``Raises`` section
   must be the last section of the docstring. For ``__init__``, document
   the exceptions in the class docstring instead.
4. Section headers must use the numpydoc format (a bare header line
   followed by a ``----------`` underline). Google-style inline headers
   such as ``Returns:`` are rejected.
5. Mobject subclasses (including indirect subclasses within the same file)
   must include a ``.. manim::`` example block in the class docstring.
   Pure ``Enum``/``ABC`` classes and non-mobject helpers are exempt.

Violations may be exempted via ``workflow/doc_section_exemptions.json``,
which maps a repository-relative file path to a list of qualified names
(e.g. ``"ClassName"``, ``"ClassName.method"``, ``"function"``). This is
intended mainly for vendored subpackages that are kept in sync with
upstream projects.

Usage:
    python validate_doc_sections.py
    python validate_doc_sections.py --write-exemptions
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "manim_extensions"
EXEMPTIONS_FILE = Path(__file__).resolve().parent / "doc_section_exemptions.json"

SECTION_NAMES = (
    "Parameters",
    "Returns",
    "Yields",
    "Raises",
    "Examples",
    "Attributes",
    "Methods",
)

# Dunder methods that are conventionally left undocumented.
SKIP_DUNDER = {
    '__repr__', '__str__', '__len__', '__getitem__', '__setitem__',
    '__delitem__', '__enter__', '__exit__', '__call__', '__eq__',
    '__ne__', '__lt__', '__le__', '__gt__', '__ge__', '__add__',
    '__sub__', '__mul__', '__truediv__', '__contains__', '__iter__',
    '__next__', '__hash__', '__getattr__', '__setattr__', '__delattr__',
    '__new__', '__bool__', '__abs__', '__pos__', '__neg__', '__invert__',
    '__int__', '__float__', '__complex__', '__round__', '__trunc__',
    '__floor__', '__ceil__', '__index__', '__format__', '__sizeof__',
    '__class_getitem__', '__init_subclass__', '__set_name__',
    '__copy__', '__deepcopy__', '__reduce__', '__reduce_ex__',
    '__getstate__', '__setstate__', '__getattribute__',
    '__dir__', '__subclasshook__', '__instancecheck__',
    '__missing__', '__del__', '__post_init__',
    '__abstractmethods__', '__parameters__',
    '__orig_bases__', '__type_params__',
    '__slots__', '__mro_entries__',
    '__annotations__', '__dict__', '__module__',
}

# Decorator/protocol inner functions where docstrings are optional.
SKIP_NAMES = {
    'wrapper', 'decorator_maker', 'real_test',
}

# Base class names that indicate an mobject (renderable) subclass.
MOBJECT_BASE_NAMES = {
    "Mobject", "VMobject", "VGroup", "SVGMobject", "CMobject", "Group",
    "Mobject1D", "Mobject2D", "Mobject3D",
}

# Additional direct manim mobject subclasses commonly used as bases.
MOBJECT_BASE_NAMES |= {
    "Line", "DashedLine", "Dot", "Circle", "Arc", "Annulus", "Arrow",
    "DoubleArrow", "CurvedArrow", "Vector", "Brace", "Polygram", "Polygon",
    "Rectangle", "Square", "Triangle", "RoundedRectangle", "Text", "Tex",
    "MathTex", "SingleStringMathTex", "Code", "Table", "Matrix", "ImageMobject",
    "Axes", "NumberPlane", "PolarPlane", "Plot", "BarChart",
}

# Classes that never need a renderable example.
# OpenGL-only mobjects cannot be rendered by the cairo-based docs build;
# they are documented with ``.. code-block::`` examples instead.
NON_RENDERABLE_BASES = {
    "Enum", "IntEnum", "StrEnum", "Flag", "IntFlag", "ABC",
    "OpenGLMobject", "OpenGLVMobject", "OpenGLVGroup", "OpenGLGroup",
    "OpenGLSurface",
}

PARAM_ENTRY_RE = re.compile(r"^(\*{0,2}[\w.]+)\s*:(?!:)\s*(.*)$")
BARE_ENTRY_RE = re.compile(r"^(\*{0,2}[\w.]+)$")
SECTION_UNDERLINE_RE = re.compile(r"^\s*-{3,}\s*$")
# Google-style inline section headers such as ``Returns:``; numpydoc
# sections are a bare header line followed by a ``----------`` underline.
INLINE_SECTION_RE = re.compile(
    r"^(Parameters|Returns|Raises|Yields|Examples|Attributes|Methods|Notes|"
    r"See Also|Warnings|References|Other Parameters|Receives)\s*:(?!:)"
)


def base_root_name(base: ast.expr) -> str:
    """Return the root name of a base-class expression."""
    node = base
    if isinstance(node, ast.Subscript):
        node = node.value
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call):
        return base_root_name(node.func)
    return ""


def is_mobject_class(node: ast.ClassDef, local_bases: dict) -> bool:
    """Decide whether a class is a (transitive, file-local) mobject subclass."""
    seen = set()
    stack = [base_root_name(b) for b in node.bases]
    while stack:
        name = stack.pop()
        if not name or name in seen:
            continue
        seen.add(name)
        if name in NON_RENDERABLE_BASES:
            return False
        if name in MOBJECT_BASE_NAMES or name.endswith(("Mobject", "Group")):
            return True
        stack.extend(local_bases.get(name, ()))
    return False


def documented_params(doc: str) -> set:
    """Extract parameter names documented in a numpydoc Parameters section.

    A line only counts as a section header when it is followed by a
    ``----------`` underline, so description text like "A Manim color" is
    never mistaken for a header.
    """
    params = set()
    lines = doc.splitlines()
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


def section_names(doc: str) -> set:
    """Return the numpydoc section headers present in a docstring."""
    return {s.strip() for s in doc.splitlines() if s.strip() in SECTION_NAMES}


def section_positions(doc: str) -> list:
    """Return an ordered list of ``(name, header_line_index)`` numpydoc sections.

    A line only counts as a section header when followed by a ``----------``
    underline.
    """
    sections = []
    lines = doc.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if (
            stripped in SECTION_NAMES
            and idx + 1 < len(lines)
            and SECTION_UNDERLINE_RE.match(lines[idx + 1])
        ):
            sections.append((stripped, idx))
    return sections


def raises_section_body(doc: str) -> str:
    """Return the body text of the Raises section, or an empty string."""
    lines = doc.splitlines()
    sections = section_positions(doc)
    for pos, (name, idx) in enumerate(sections):
        if name == "Raises":
            end = sections[pos + 1][1] if pos + 1 < len(sections) else len(lines)
            return "\n".join(lines[idx + 2:end])
    return ""


def raised_exceptions(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list:
    """Return the names of exceptions raised directly by the function body.

    Nested function/class/lambda definitions are not descended into, and bare
    ``raise`` re-raises are ignored.
    """
    names = set()

    def visit(current):
        for child in ast.iter_child_nodes(current):
            if isinstance(
                child,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda),
            ):
                continue  # don't descend into nested scopes
            if isinstance(child, ast.Raise) and child.exc is not None:
                exc = child.exc
                if isinstance(exc, ast.Call):
                    exc = exc.func
                if isinstance(exc, ast.Name):
                    names.add(exc.id)
                elif isinstance(exc, ast.Attribute):
                    names.add(exc.attr)
            visit(child)

    visit(node)
    return sorted(names)


def annotation_is_none(node: ast.expr | None) -> bool:
    """Return True when the return annotation is None or absent."""
    if node is None:
        return True
    if isinstance(node, ast.Constant) and node.value is None:
        return True
    if isinstance(node, ast.Name) and node.id == "None":
        return True
    return False


def function_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list:
    """Return parameter names excluding ``self``/``cls``."""
    params = [
        a.arg
        for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
        if a.arg not in ("self", "cls")
    ]
    if node.args.vararg:
        params.append(node.args.vararg.arg)
    if node.args.kwarg:
        params.append(node.args.kwarg.arg)
    return params


def check_file(filepath: Path) -> list:
    """Check a single file; return a list of violation dicts."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []

    local_bases = {
        node.name: [base_root_name(b) for b in node.bases]
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }

    violations = []

    def check_inline_sections(doc, qualname, lineno):
        """Flag Google-style inline headers like ``Returns:``."""
        for offset, line in enumerate(doc.splitlines()):
            stripped = line.strip()
            if INLINE_SECTION_RE.match(stripped):
                violations.append({
                    "line": lineno + offset,
                    "qualname": qualname,
                    "type": "INLINE_SECTION_HEADER",
                    "message": f"uses inline '{stripped[:40]}' instead of a "
                               f"numpydoc section header (bare name followed "
                               f"by a '----------' underline)",
                })

    module_doc = ast.get_docstring(tree)
    if module_doc:
        check_inline_sections(module_doc, "<module>", 1)

    def visit_body(body, prefix, in_class):
        for node in body:
            if isinstance(node, ast.ClassDef):
                if node.name.startswith("_"):
                    continue
                check_class(node, prefix)
                visit_body(node.body, f"{prefix}{node.name}.", True)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if in_class:
                    check_function(node, prefix, is_method=True)
                elif not prefix:
                    check_function(node, "", is_method=False)

    def check_function(node, prefix, is_method):
        name = node.name
        if name in SKIP_NAMES:
            return
        if name.startswith("_") and name != "__init__":
            return
        if name in SKIP_DUNDER:
            return
        doc = ast.get_docstring(node)
        if doc is None:
            return  # missing docstrings are enforced by validate_docstrings.py
        qualname = f"{prefix}{name}"
        check_inline_sections(doc, qualname, node.lineno)
        secs = section_names(doc)
        params = function_params(node)
        # __init__ parameters are documented in the class docstring instead;
        # that convention is enforced by validate_param_docs.py.
        if name != "__init__" and params:
            if "Parameters" not in secs:
                violations.append({
                    "line": node.lineno,
                    "qualname": qualname,
                    "type": "MISSING_PARAMETERS_SECTION",
                    "message": "has parameters but no numpydoc 'Parameters' section",
                })
            else:
                documented = documented_params(doc)
                for param in params:
                    if node.args.vararg and param == node.args.vararg.arg:
                        continue  # bare *args is conventionally undocumented
                    if param not in documented:
                        violations.append({
                            "line": node.lineno,
                            "qualname": qualname,
                            "type": "MISSING_PARAM_ENTRY",
                            "message": f"parameter '{param}' not documented "
                                       f"in 'Parameters' section",
                        })
        if (
            not annotation_is_none(node.returns)
            and "Returns" not in secs
            and "Yields" not in secs
        ):
            violations.append({
                "line": node.lineno,
                "qualname": qualname,
                "type": "MISSING_RETURNS_SECTION",
                "message": "has a non-None return annotation but no "
                           "'Returns'/'Yields' section",
            })
        check_raises_last(doc, qualname, node.lineno)
        # __init__ raises are documented in the class docstring instead,
        # consistent with the parameter documentation convention.
        raised = [] if name == "__init__" else raised_exceptions(node)
        if raised:
            if "Raises" not in secs:
                violations.append({
                    "line": node.lineno,
                    "qualname": qualname,
                    "type": "MISSING_RAISES_SECTION",
                    "message": f"raises {', '.join(raised)} but has no "
                               f"'Raises' section",
                })
            else:
                body = raises_section_body(doc)
                # Normalize so that `raise key_error` (a caught KeyError)
                # matches a documented ``KeyError`` entry.
                norm_body = body.lower().replace("_", "")
                for exc in raised:
                    if exc.lower().replace("_", "") not in norm_body:
                        violations.append({
                            "line": node.lineno,
                            "qualname": qualname,
                            "type": "MISSING_RAISE_ENTRY",
                            "message": f"raised exception '{exc}' not mentioned "
                                       f"in 'Raises' section",
                        })

    def check_raises_last(doc, qualname, lineno):
        """The 'Raises' section must be the last section of the docstring."""
        sections = section_positions(doc)
        for pos, (name, _idx) in enumerate(sections[:-1]):
            if name == "Raises":
                nxt = sections[pos + 1][0]
                violations.append({
                    "line": lineno,
                    "qualname": qualname,
                    "type": "RAISES_NOT_LAST",
                    "message": f"'Raises' section must be last, but '{nxt}' "
                               f"follows it",
                })
                return

    def check_class(node, prefix):
        doc = ast.get_docstring(node) or ""
        qualname = f"{prefix}{node.name}"
        check_raises_last(doc, qualname, node.lineno)
        check_inline_sections(doc, qualname, node.lineno)
        if not is_mobject_class(node, local_bases):
            return
        if ".. manim::" not in doc:
            violations.append({
                "line": node.lineno,
                "qualname": qualname,
                "type": "MISSING_MANIM_EXAMPLE",
                "message": "mobject subclass without a '.. manim::' example "
                           "in the class docstring",
            })

    visit_body(tree.body, "", False)
    return violations


def load_exemptions() -> dict:
    """Load the exemptions JSON; return {relative_path: set(qualnames)}."""
    if not EXEMPTIONS_FILE.exists():
        return {}
    data = json.loads(EXEMPTIONS_FILE.read_text(encoding="utf-8"))
    return {path: set(names) for path, names in data.items()}


def iter_py_files():
    """Yield all Python files under manim_extensions, skipping caches."""
    for path in sorted(SRC.rglob("*.py")):
        if path.name == "__init__.py" or "__pycache__" in path.parts:
            continue
        yield path


def main() -> int:
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate numpydoc sections and manim examples; "
                    "optionally (re)write the exemptions file."
    )
    parser.add_argument(
        "--write-exemptions", action="store_true",
        help="Write ALL current violations to the exemptions file. "
             "This blesses the current state — review the diff carefully.",
    )
    args = parser.parse_args()

    exemptions = load_exemptions()
    all_violations = {}

    for filepath in iter_py_files():
        violations = check_file(filepath)
        if violations:
            all_violations[filepath] = violations

    if args.write_exemptions:
        data = {}
        for filepath, violations in all_violations.items():
            rel = filepath.relative_to(ROOT).as_posix()
            names = sorted({v["qualname"] for v in violations})
            data[rel] = names
        EXEMPTIONS_FILE.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        total = sum(len(v) for v in data.values())
        print(f"Wrote {total} exempted names for {len(data)} files to "
              f"{EXEMPTIONS_FILE.name}. Review the diff before committing!")
        return 0

    unexempted = {}
    for filepath, violations in all_violations.items():
        rel = filepath.relative_to(ROOT).as_posix()
        exempt = exemptions.get(rel, set())
        leftover = [v for v in violations if v["qualname"] not in exempt]
        if leftover:
            unexempted[rel] = leftover

    total = sum(len(v) for v in unexempted.values())
    if total:
        print(f"Found {total} docstring section issues "
              f"(Parameters/Returns/manim example):\n")
        for rel, violations in sorted(unexempted.items()):
            print(f"  {rel}")
            for v in violations:
                print(f"    line {v['line']:4d} | {v['qualname']}: "
                      f"{v['message']}")
        print(f"\nTotal: {total} issues")
        print("Validation failed!")
        return 1

    print("All docstring sections are properly documented!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
