#!/usr/bin/env python3
"""LEGACY: Detect inline code that could be converted to Sphinx cross-references.

This script is superseded by ``validate_refs.py`` and ``fix_refs.py``.
It is kept for reference only.

Finds:
1. Short cross-references without module path (e.g. :meth:`Mobject.scale`)
   that should be :meth:`~manim.mobject.mobject.Mobject.scale`
2. Plain inline code like ``ClassName.method()`` or ``ClassName.attribute``
   that could become cross-references

Outputs both a human-readable report and structured JSON for the fix script.
"""

import ast
import importlib
import json
import re
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

    return classes_map, functions_map


def find_short_xrefs(filepath: Path) -> list[dict]:
    """Find Sphinx cross-references without module paths."""
    results = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            for m in re.finditer(
                r'(:(?:class|meth|func|attr|mod|exc|obj):)`([^`]+)`', line
            ):
                role = m.group(1)
                target = m.group(2)
                if target.startswith("~") or target.startswith("."):
                    continue
                if target in SKIP_NAMES:
                    continue
                if "." not in target:
                    results.append({
                        "lineno": lineno,
                        "role": role,
                        "target": target,
                        "match_start": m.start(),
                        "match_end": m.end(),
                    })
    return results


def find_inline_code(filepath: Path) -> list[dict]:
    """Find inline code that looks like API references but isn't a cross-ref."""
    results = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            for m in re.finditer(
                r'`{1,2}([A-Z][a-zA-Z_0-9]*(?:\.[a-zA-Z_][a-zA-Z_0-9]*(?:\(\))?)+)`{1,2}',
                line,
            ):
                full = m.group(1)
                if full.startswith("~"):
                    continue
                if full in SKIP_NAMES:
                    continue
                if full.count(".") >= 1:
                    results.append({
                        "lineno": lineno,
                        "code": full,
                        "match_start": m.start(),
                        "match_end": m.end(),
                    })
    return results


def find_class_context(filepath: Path) -> dict:
    """Parse a .py file to find which class/function each docstring belongs to.

    Returns a mapping: {lineno: {"class": "ClassName", "module": "module.path"}}
    """
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
            self._func_stack = []

        def visit_ClassDef(self, node):
            self._class_stack.append(node.name)
            docstring = ast.get_docstring(node)
            if docstring:
                start_line = node.lineno
                end_line = (node.body[0].lineno if node.body else node.end_lineno) or node.lineno
                if node.end_lineno:
                    end_line = node.end_lineno
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


def main():
    print("Building name maps...")
    classes_map, functions_map = build_name_map()
    print(f"  Classes: {len(classes_map)}")
    print(f"  Functions/Methods: {len(functions_map)}")

    short_xrefs = []
    inline_code = []

    py_files = list(SRC.rglob("*.py"))
    rst_files = list(DOCS.rglob("*.rst"))
    targets = py_files + rst_files

    all_contexts = {}

    for filepath in sorted(targets):
        if "__pycache__" in str(filepath):
            continue
        rel = str(filepath.relative_to(ROOT))

        if filepath.suffix == ".py":
            all_contexts[rel] = find_class_context(filepath)

        for item in find_short_xrefs(filepath):
            short_xrefs.append({
                "file": rel,
                **item,
            })

        for item in find_inline_code(filepath):
            inline_code.append({
                "file": rel,
                **item,
            })

    output_lines = []
    output_lines.append(
        f"=== Short cross-references (no module path): {len(short_xrefs)} ==="
    )
    for item in short_xrefs:
        output_lines.append(
            f"  {item['file']}:{item['lineno']}  "
            f"{item['role']}`{item['target']}`"
        )

    output_lines.append(
        f"\n=== Potential inline code to convert: {len(inline_code)} ==="
    )
    for item in inline_code:
        output_lines.append(f"  {item['file']}:{item['lineno']}  `{item['code']}`")

    output = "\n".join(output_lines)
    outfile = ROOT / "workflow" / "_inline_refs_result.txt"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(output)
    print(output)

    data = {
        "short_xrefs": short_xrefs,
        "inline_code": inline_code,
        "contexts": all_contexts,
        "classes_map": classes_map,
        "functions_map": functions_map,
    }
    json_file = ROOT / "workflow" / "_inline_refs_data.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nData written to {json_file}")


if __name__ == "__main__":
    main()