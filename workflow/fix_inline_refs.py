#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""LEGACY: Fix inline code that could be converted to Sphinx cross-references.

This script is superseded by ``validate_refs.py`` and ``fix_refs.py``.
It is kept for reference only.

Reads detection data from find_inline_refs.py and applies fixes:
1. Short cross-references without module path -> add fully qualified path
2. Plain inline code -> convert to Sphinx cross-references

Usage:
    python workflow/fix_inline_refs.py            # use cached JSON data
    python workflow/find_inline_refs.py && python workflow/fix_inline_refs.py
"""

import ast
import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "manim_extensions"
DOCS = ROOT / "docs"

SKIP_NAMES = {
    "int", "float", "str", "bool", "list", "dict", "tuple", "set",
    "numpy.ndarray", "ndarray", "NotImplementedError", "ValueError",
    "TypeError", "KeyError", "IndexError", "AttributeError",
    "RuntimeError", "Exception", "object",
}

SKIP_PREFIXES = (
    "~typing.", "~numpy.", "~matplotlib.", "~collections.",
    "~builtins.", "~os.", "~re.", "~sys.", "~pathlib.",
)

EXTERNAL_FALLBACKS = {
    "NotImplementedError": "builtins.NotImplementedError",
    "ValueError": "builtins.ValueError",
    "TypeError": "builtins.TypeError",
    "KeyError": "builtins.KeyError",
    "IndexError": "builtins.IndexError",
    "AttributeError": "builtins.AttributeError",
    "RuntimeError": "builtins.RuntimeError",
    "Exception": "builtins.Exception",
    "object": "builtins.object",
}


class _ClassVisitor(ast.NodeVisitor):
    def __init__(self, mod_path):
        self.mod_path = mod_path
        self.classes = {}
        self.functions = {}
        self._class_stack = []

    def visit_ClassDef(self, node):
        class_fqn = f"{self.mod_path}.{node.name}" if self.mod_path else node.name
        self.classes[node.name] = class_fqn
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node):
        if self._class_stack:
            class_name = self._class_stack[-1]
            method_fqn = f"{self.mod_path}.{class_name}.{node.name}"
            key = f"{class_name}.{node.name}"
            self.functions[key] = method_fqn
            self.functions[node.name] = method_fqn
        else:
            if self.mod_path:
                func_fqn = f"{self.mod_path}.{node.name}"
                self.functions[node.name] = func_fqn
        self.generic_visit(node)


def scan_package(package_name, classes_map, functions_map):
    """Scan an installed package for classes and functions."""
    try:
        pkg = importlib.import_module(package_name)
    except ImportError:
        return

    pkg_path = Path(pkg.__path__[0]) if hasattr(pkg, "__path__") else None
    if pkg_path is None:
        return

    for py_file in pkg_path.rglob("*.py"):
        if py_file.name.startswith("_") and py_file.name != "__init__.py":
            continue
        if py_file.name == "__pycache__":
            continue
        try:
            rel = py_file.relative_to(pkg_path)
        except ValueError:
            continue
        mod_path = f"{package_name}." + ".".join(rel.with_suffix("").parts)
        mod_path = mod_path.replace(".__init__", "")
        if mod_path.endswith(".__init__"):
            mod_path = mod_path[:-len(".__init__")]

        try:
            with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        visitor = _ClassVisitor(mod_path)
        visitor.visit(tree)
        for k, v in visitor.classes.items():
            if k not in classes_map:
                classes_map[k] = v
        for k, v in visitor.functions.items():
            if k not in functions_map:
                functions_map[k] = v


def build_name_map():
    """Scan manim_extensions and manim for name -> FQN mappings."""
    classes_map = {}
    functions_map = {}

    for py_file in SRC.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        rel = py_file.relative_to(ROOT)
        mod_path = ".".join(rel.with_suffix("").parts)
        mod_path = mod_path.replace(".__init__", "")
        if mod_path.endswith(".__init__"):
            mod_path = mod_path[:-len(".__init__")]

        try:
            with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        visitor = _ClassVisitor(mod_path)
        visitor.visit(tree)
        classes_map.update(visitor.classes)
        functions_map.update(visitor.functions)

    scan_package("manim", classes_map, functions_map)

    for k, v in EXTERNAL_FALLBACKS.items():
        if k not in classes_map:
            classes_map[k] = v

    return classes_map, functions_map


def build_class_attr_map():
    """Build a map of ClassName.attr -> FQN for class data attributes.

    Scans manim_extensions and manim for class-level attributes
    (not methods) so we can resolve references like NodeSolt.SPLIT_PARTS.
    """
    attr_map = {}

    for py_file in SRC.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        rel = py_file.relative_to(ROOT)
        mod_path = ".".join(rel.with_suffix("").parts)
        mod_path = mod_path.replace(".__init__", "")
        if mod_path.endswith(".__init__"):
            mod_path = mod_path[:-len(".__init__")]

        try:
            with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        _extract_attrs(tree, mod_path, attr_map)

    _extract_manim_attrs(attr_map)

    return attr_map


def _extract_attrs(tree, mod_path, attr_map):
    """Extract class-level data attributes from an AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_fqn = f"{mod_path}.{node.name}"
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            key = f"{node.name}.{target.id}"
                            attr_map[key] = f"{class_fqn}.{target.id}"
                            attr_map[target.id] = f"{class_fqn}.{target.id}"
                elif isinstance(item, ast.AnnAssign) and item.target:
                    if isinstance(item.target, ast.Name):
                        key = f"{node.name}.{item.target.id}"
                        attr_map[key] = f"{class_fqn}.{item.target.id}"
                        attr_map[item.target.id] = f"{class_fqn}.{item.target.id}"
                elif isinstance(item, ast.ClassDef):
                    nested_fqn = f"{class_fqn}.{node.name}"
                    for sub_item in item.body:
                        if isinstance(sub_item, ast.Assign):
                            for target in sub_item.targets:
                                if isinstance(target, ast.Name):
                                    key = f"{node.name}.{node.name}.{target.id}"
                                    fqn = f"{nested_fqn}.{target.id}"
                                    attr_map[key] = fqn
                                    attr_map[target.id] = fqn


def _extract_manim_attrs(attr_map):
    """Extract class attributes from installed manim package."""
    try:
        import manim
    except ImportError:
        return

    pkg_path = Path(manim.__path__[0]) if hasattr(manim, "__path__") else None
    if pkg_path is None:
        return

    for py_file in pkg_path.rglob("*.py"):
        if py_file.name.startswith("_") and py_file.name != "__init__.py":
            continue
        if py_file.name == "__pycache__":
            continue
        try:
            rel = py_file.relative_to(pkg_path)
        except ValueError:
            continue
        mod_path = f"manim." + ".".join(rel.with_suffix("").parts)
        mod_path = mod_path.replace(".__init__", "")
        if mod_path.endswith(".__init__"):
            mod_path = mod_path[:-len(".__init__")]

        try:
            with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        _extract_attrs(tree, mod_path, attr_map)


def build_file_context(filepath: Path) -> dict:
    """Build line->class context map for a .py file."""
    rel = filepath.relative_to(ROOT)
    mod_path = ".".join(rel.with_suffix("").parts)
    mod_path = mod_path.replace(".__init__", "")
    if mod_path.endswith(".__init__"):
        mod_path = mod_path[:-len(".__init__")]

    context = {}

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return context

    class _ContextVisitor(ast.NodeVisitor):
        def __init__(self):
            self._class_stack = []

        def visit_ClassDef(self, node):
            self._class_stack.append(node.name)
            docstring = ast.get_docstring(node)
            if docstring:
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                for line in range(start_line, end_line + 1):
                    context[line] = {
                        "class": ".".join(self._class_stack),
                        "module": mod_path,
                    }
            self.generic_visit(node)
            self._class_stack.pop()

        def visit_FunctionDef(self, node):
            docstring = ast.get_docstring(node)
            if docstring and self._class_stack:
                class_name = ".".join(self._class_stack)
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                for line in range(start_line, end_line + 1):
                    context[line] = {
                        "class": class_name,
                        "module": mod_path,
                    }
            self.generic_visit(node)

    visitor = _ContextVisitor()
    visitor.visit(tree)
    return context


def resolve_short_xref(
    target: str,
    role: str,
    file_context: dict | None,
    classes_map: dict,
    functions_map: dict,
    attr_map: dict,
) -> str | None:
    """Resolve a short cross-reference to its fully qualified path.

    For targets without dots (e.g. '__mob_index'), uses file context
    to determine the enclosing class, then resolves the attribute.
    """
    if "." not in target:
        if file_context and file_context.get("class"):
            class_name = file_context["class"]
            key = f"{class_name}.{target}"
            if key in attr_map:
                fqn = attr_map[key]
                return f"~{fqn}"
            if target in attr_map:
                return f"~{attr_map[target]}"

        if target in attr_map:
            return f"~{attr_map[target]}"

        context_cls = file_context.get("class") if file_context else None
        if context_cls:
            parts = context_cls.split(".")
            for i in range(len(parts), 0, -1):
                cls_key = ".".join(parts[:i])
                full_cls = classes_map.get(cls_key)
                if full_cls:
                    fqn = f"{full_cls}.{target}"
                    return f"~{fqn}"

        for cls_name, cls_fqn in classes_map.items():
            key = f"{cls_name}.{target}"
            if key in attr_map:
                return f"~{attr_map[key]}"

        return None

    parts = target.split(".")
    last = parts[-1]

    context_cls = file_context.get("class") if file_context else None
    if context_cls:
        context_parts = context_cls.split(".")
        for i in range(len(context_parts), 0, -1):
            cls_name = ".".join(context_parts[:i])
            if cls_name == parts[0]:
                key = target
                if key in functions_map:
                    return f"~{functions_map[key]}"
                if key in attr_map:
                    return f"~{attr_map[key]}"
                full_cls = classes_map.get(cls_name)
                if full_cls:
                    fqn = f"{full_cls}.{'.'.join(parts[1:])}"
                    return f"~{fqn}"

    if target in functions_map:
        return f"~{functions_map[target]}"

    if target in attr_map:
        return f"~{attr_map[target]}"

    if parts[0] in classes_map:
        full_cls = classes_map[parts[0]]
        fqn = f"{full_cls}.{'.'.join(parts[1:])}"
        return f"~{fqn}"

    if parts[0] in attr_map:
        cls_fqn = attr_map[parts[0]]
        fqn = f"{cls_fqn}.{'.'.join(parts[1:])}"
        return f"~{fqn}"

    return None


def resolve_inline_code(
    code: str,
    file_context: dict | None,
    classes_map: dict,
    functions_map: dict,
    attr_map: dict,
) -> tuple[str, str] | None:
    """Resolve plain inline code to (role, fully_qualified_target).

    Returns (role, target_with_tilde) or None if unresolvable.
    """
    if code in functions_map:
        fqn = functions_map[code]
        if "." in code:
            return (":meth:", f"~{fqn}")
        return (":func:", f"~{fqn}")

    if code in attr_map:
        return (":attr:", f"~{attr_map[code]}")

    if code in classes_map:
        return (":class:", f"~{classes_map[code]}")

    parts = code.split(".")
    if len(parts) >= 2:
        class_part = parts[0]
        rest = ".".join(parts[1:])

        context_cls = file_context.get("class") if file_context else None
        if context_cls:
            context_parts = context_cls.split(".")
            for i in range(len(context_parts), 0, -1):
                cls_name = ".".join(context_parts[:i])
                if cls_name == class_part:
                    full_cls = classes_map.get(cls_name) or attr_map.get(cls_name)
                    if full_cls:
                        fqn = f"{full_cls}.{rest}"
                        key = f"{class_part}.{rest}"
                        if key in functions_map:
                            return (":meth:", f"~{functions_map[key]}")
                        return (":attr:", f"~{fqn}")

        key = f"{class_part}.{rest}"
        if key in functions_map:
            return (":meth:", f"~{functions_map[key]}")

        if key in attr_map:
            return (":attr:", f"~{attr_map[key]}")

        if class_part in classes_map:
            full_cls = classes_map[class_part]
            test_key = rest
            if test_key in functions_map:
                return (":meth:", f"~{functions_map[test_key]}")
            fqn = f"{full_cls}.{rest}"
            return (":attr:", f"~{fqn}")

        if class_part in attr_map:
            cls_fqn = attr_map[class_part]
            fqn = f"{cls_fqn}.{rest}"
            return (":attr:", f"~{fqn}")

    return None


def fix_file(
    filepath: Path,
    classes_map: dict,
    functions_map: dict,
    attr_map: dict,
) -> int:
    """Fix a single file. Returns number of changes made."""
    rel = str(filepath.relative_to(ROOT))

    if filepath.suffix == ".py":
        file_context = build_file_context(filepath)
    else:
        file_context = {}

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    changes = 0
    new_lines = []

    for lineno, line in enumerate(lines, 1):
        ctx = file_context.get(lineno, {}) if file_context else {}

        new_line = line

        def fix_short_xref(match):
            nonlocal changes
            role = match.group(1)
            target = match.group(2)

            if target.startswith("~") or target.startswith("."):
                return match.group(0)
            if target in SKIP_NAMES:
                return match.group(0)

            resolved = resolve_short_xref(
                target, role, ctx, classes_map, functions_map, attr_map
            )
            if resolved is None:
                return match.group(0)

            changes += 1
            return f"{role}`{resolved}`"

        new_line = re.sub(
            r'(:(?:class|meth|func|attr|mod|exc|obj):)`([^`]+)`',
            fix_short_xref,
            new_line,
        )

        def fix_inline_code(match):
            nonlocal changes
            code = match.group(1)

            if code.startswith("~"):
                return match.group(0)
            if code in SKIP_NAMES:
                return match.group(0)
            if "." not in code:
                return match.group(0)

            result = resolve_inline_code(
                code, ctx, classes_map, functions_map, attr_map
            )
            if result is None:
                return match.group(0)

            role, fqn = result
            changes += 1
            return f"{role}`{fqn}`"

        new_line = re.sub(
            r'`{1,2}([A-Z][a-zA-Z_0-9]*(?:\.[a-zA-Z_][a-zA-Z_0-9]*(?:\(\))?)+)`{1,2}',
            fix_inline_code,
            new_line,
        )

        new_lines.append(new_line)

    if changes > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"  {rel}: {changes} fix(es)")

    return changes


def main():
    print("Building name maps...")
    classes_map, functions_map = build_name_map()
    print(f"  Classes: {len(classes_map)}")
    print(f"  Functions/Methods: {len(functions_map)}")

    print("Building class attribute map...")
    attr_map = build_class_attr_map()
    print(f"  Class attributes: {len(attr_map)}")

    total = 0
    files_changed = 0

    targets = list(SRC.rglob("*.py")) + list(DOCS.rglob("*.rst"))

    for filepath in sorted(targets):
        if "__pycache__" in str(filepath):
            continue
        changes = fix_file(filepath, classes_map, functions_map, attr_map)
        if changes > 0:
            total += changes
            files_changed += 1

    print(f"\nDone: {total} fixes in {files_changed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())