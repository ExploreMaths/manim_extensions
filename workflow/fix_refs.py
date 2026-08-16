#!/usr/bin/env python3
"""Fix Sphinx cross-reference issues detected by ``validate_refs.py``.

Reads the JSON report produced by ``validate_refs.py``
(``_refs_report.json``) and attempts to auto-fix two categories of
problems:

1. Short cross-references     – adds a fully qualified module path
                                (e.g. :attr:`__mob_index` →
                                 :attr:`~...MArrayElement.__mob_index`).

2. Plain inline code         – converts back-ticked API names to proper
                                Sphinx cross-references
                                (e.g. `Mobject.scale` →
                                 :meth:`~...Mobject.scale`).

Broken references (category 1 in the report) cannot be auto-fixed –
their targets simply do not exist.  They are printed so a human can
decide what to do.

Usage:
    python workflow/validate_refs.py     # detect, produce _refs_report.json
    python workflow/fix_refs.py          # read report and apply fixes
"""

import ast
import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "manim_extensions"
DOCS = ROOT / "docs"

REPORT_FILE = ROOT / "workflow" / "_refs_report.json"

REF_PATTERN = re.compile(
    r'(:(?:class|meth|func|attr|mod|exc|obj):)`([^`]+)`'
)

INLINE_CODE_PATTERN = re.compile(
    r'`{1,2}([A-Z][a-zA-Z_0-9]*(?:\.[a-zA-Z_][a-zA-Z_0-9]*(?:\(\))?)*)`{1,2}'
)

SKIP_NAMES = frozenset({
    "int", "float", "str", "bool", "list", "dict", "tuple", "set",
    "numpy.ndarray", "ndarray",
    "NotImplementedError", "ValueError", "TypeError", "KeyError",
    "IndexError", "AttributeError", "RuntimeError", "Exception",
    "object",
})

SKIP_PREFIXES = (
    "~typing.", "~numpy.", "~matplotlib.", "~collections.",
    "~builtins.", "~os.", "~re.", "~sys.", "~pathlib.",
)


# ---------------------------------------------------------------------------
# Name-map builders (duplicated from validate_refs.py so the fixer can run
# standalone on an existing JSON report without re-scanning the whole tree).
# ---------------------------------------------------------------------------


class _ClassVisitor(ast.NodeVisitor):
    def __init__(self, mod_path: str):
        self.mod_path = mod_path
        self.classes: dict[str, str] = {}
        self.functions: dict[str, str] = {}
        self._class_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_fqn = f"{self.mod_path}.{node.name}" if self.mod_path else node.name
        self.classes[node.name] = class_fqn
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
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


class _AttrCollector(ast.NodeVisitor):
    def __init__(self, mod_path: str):
        self.mod_path = mod_path
        self.attrs: dict[str, str] = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_fqn = f"{self.mod_path}.{node.name}"
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        key = f"{node.name}.{target.id}"
                        self.attrs[key] = f"{class_fqn}.{target.id}"
                        self.attrs[target.id] = f"{class_fqn}.{target.id}"
            elif isinstance(item, ast.AnnAssign) and item.target:
                if isinstance(item.target, ast.Name):
                    key = f"{node.name}.{item.target.id}"
                    self.attrs[key] = f"{class_fqn}.{item.target.id}"
                    self.attrs[item.target.id] = f"{class_fqn}.{item.target.id}"
        self.generic_visit(node)


def _iter_py_files(root: Path):
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        if py_file.name.startswith("_") and py_file.name != "__init__.py":
            continue
        yield py_file


def _mod_path_for(py_file: Path, base: Path) -> str:
    rel = py_file.relative_to(base)
    mod = ".".join(rel.with_suffix("").parts)
    mod = mod.replace(".__init__", "")
    if mod.endswith(".__init__"):
        mod = mod[: -len(".__init__")]
    return mod


def build_name_maps():
    classes_map: dict[str, str] = {}
    functions_map: dict[str, str] = {}
    attr_map: dict[str, str] = {}

    for py_file in _iter_py_files(SRC):
        mod_path = _mod_path_for(py_file, ROOT)
        try:
            with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        visitor = _ClassVisitor(mod_path)
        visitor.visit(tree)
        classes_map.update(visitor.classes)
        functions_map.update(visitor.functions)

        ac = _AttrCollector(mod_path)
        ac.visit(tree)
        for k, v in ac.attrs.items():
            attr_map.setdefault(k, v)

    try:
        manim_pkg = importlib.import_module("manim")
    except ImportError:
        manim_pkg = None

    if manim_pkg is not None and hasattr(manim_pkg, "__path__"):
        manim_root = Path(manim_pkg.__path__[0])
        for py_file in _iter_py_files(manim_root):
            mod_path = _mod_path_for(py_file, manim_root.parent)
            try:
                with open(py_file, "r", encoding="utf-8", errors="replace") as f:
                    tree = ast.parse(f.read(), filename=str(py_file))
            except (SyntaxError, UnicodeDecodeError):
                continue

            visitor = _ClassVisitor(mod_path)
            visitor.visit(tree)
            for k, v in visitor.classes.items():
                classes_map.setdefault(k, v)
            for k, v in visitor.functions.items():
                functions_map.setdefault(k, v)

            ac = _AttrCollector(mod_path)
            ac.visit(tree)
            for k, v in ac.attrs.items():
                attr_map.setdefault(k, v)

    # Built-in fallbacks
    fallbacks = {
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
    for k, v in fallbacks.items():
        classes_map.setdefault(k, v)

    return classes_map, functions_map, attr_map


# ---------------------------------------------------------------------------
# Resolvers
# ---------------------------------------------------------------------------


def resolve_short_xref(
    target: str,
    file_context: dict | None,
    classes_map: dict,
    functions_map: dict,
    attr_map: dict,
) -> str | None:
    """Resolve a short Sphinx role target to ``~fully.qualified.path``."""

    # Case 1: no dots (bare attribute name, e.g. ``__mob_index``).
    if "." not in target:
        # 1a. Try class-scoped lookup via file context.
        if file_context and file_context.get("class"):
            cls = file_context["class"]
            key = f"{cls}.{target}"
            if key in attr_map:
                return f"~{attr_map[key]}"
            if target in attr_map:
                return f"~{attr_map[target]}"

        # 1b. Try global attr map.
        if target in attr_map:
            return f"~{attr_map[target]}"

        # 1c. Walk up the context class hierarchy looking for the attribute
        #     on any enclosing class that we know about.
        if file_context and file_context.get("class"):
            parts = file_context["class"].split(".")
            for i in range(len(parts), 0, -1):
                cls_key = ".".join(parts[:i])
                full_cls = classes_map.get(cls_key)
                if full_cls:
                    return f"~{full_cls}.{target}"

        # 1d. Last resort: scan all known classes for the attribute.
        for cls_name, cls_fqn in classes_map.items():
            key = f"{cls_name}.{target}"
            if key in attr_map:
                return f"~{attr_map[key]}"
            # Also check attr_map directly for this attribute name on the class
            if cls_name in attr_map and key in attr_map:
                return f"~{attr_map[key]}"

        return None

    # Case 2: has dots (``Class.attr`` or ``module.Class`` etc.).
    parts = target.split(".")

    # 2a. Use file context if the first segment matches an enclosing class.
    if file_context and file_context.get("class"):
        ctx_parts = file_context["class"].split(".")
        for i in range(len(ctx_parts), 0, -1):
            cls_name = ".".join(ctx_parts[:i])
            if cls_name == parts[0]:
                key = target
                if key in functions_map:
                    return f"~{functions_map[key]}"
                if key in attr_map:
                    return f"~{attr_map[key]}"
                full_cls = classes_map.get(cls_name) or attr_map.get(cls_name)
                if full_cls:
                    return f"~{full_cls}.{'.'.join(parts[1:])}"

    # 2b. Straight lookups.
    if target in functions_map:
        return f"~{functions_map[target]}"
    if target in attr_map:
        return f"~{attr_map[target]}"

    # 2c. ClassName.rest
    if parts[0] in classes_map:
        full_cls = classes_map[parts[0]]
        return f"~{full_cls}.{'.'.join(parts[1:])}"
    if parts[0] in attr_map:
        cls_fqn = attr_map[parts[0]]
        return f"~{cls_fqn}.{'.'.join(parts[1:])}"

    return None


def resolve_inline_code(
    code: str,
    file_context: dict | None,
    classes_map: dict,
    functions_map: dict,
    attr_map: dict,
) -> tuple[str, str] | None:
    """Resolve a bare back-ticked API name to ``(role, ~fqn)``."""

    # Exact matches first.
    if code in functions_map:
        fqn = functions_map[code]
        role = ":meth:" if "." in code else ":func:"
        return (role, f"~{fqn}")

    if code in attr_map:
        return (":attr:", f"~{attr_map[code]}")

    if code in classes_map:
        return (":class:", f"~{classes_map[code]}")

    # Class.rest lookups.
    parts = code.split(".")
    if len(parts) < 2:
        return None

    class_part = parts[0]
    rest = ".".join(parts[1:])

    # Context-aware: if class_part matches an enclosing class, resolve
    # relative to it.
    if file_context and file_context.get("class"):
        ctx_parts = file_context["class"].split(".")
        for i in range(len(ctx_parts), 0, -1):
            cls_name = ".".join(ctx_parts[:i])
            if cls_name == class_part:
                full_cls = classes_map.get(cls_name) or attr_map.get(cls_name)
                if full_cls:
                    key = f"{class_part}.{rest}"
                    if key in functions_map:
                        return (":meth:", f"~{functions_map[key]}")
                    if key in attr_map:
                        return (":attr:", f"~{attr_map[key]}")
                    return (":attr:", f"~{full_cls}.{rest}")

    key = f"{class_part}.{rest}"
    if key in functions_map:
        return (":meth:", f"~{functions_map[key]}")
    if key in attr_map:
        return (":attr:", f"~{attr_map[key]}")

    if class_part in classes_map:
        full_cls = classes_map[class_part]
        if rest in functions_map:
            return (":meth:", f"~{functions_map[rest]}")
        return (":attr:", f"~{full_cls}.{rest}")

    if class_part in attr_map:
        cls_fqn = attr_map[class_part]
        return (":attr:", f"~{cls_fqn}.{rest}")

    return None


# ---------------------------------------------------------------------------
# File-level fixer
# ---------------------------------------------------------------------------


def _build_file_context(filepath: Path) -> dict[int, dict[str, str]]:
    rel = str(filepath.relative_to(ROOT))
    mod = ".".join(Path(rel).with_suffix("").parts)
    mod = mod.replace(".__init__", "")
    if mod.endswith(".__init__"):
        mod = mod[: -len(".__init__")]

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return {}

    context: dict[int, dict[str, str]] = {}

    class _V(ast.NodeVisitor):
        def __init__(self):
            self._stack: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self._stack.append(node.name)
            doc = ast.get_docstring(node)
            if doc:
                s = node.lineno
                e = node.end_lineno or s
                for line in range(s, e + 1):
                    context[line] = {"class": ".".join(self._stack), "module": mod}
            self.generic_visit(node)
            self._stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            doc = ast.get_docstring(node)
            if doc and self._stack:
                cls = ".".join(self._stack)
                s = node.lineno
                e = node.end_lineno or s
                for line in range(s, e + 1):
                    context[line] = {"class": cls, "module": mod}
            self.generic_visit(node)

    _V().visit(tree)
    return context


def fix_file(
    filepath: Path,
    rel: str,
    classes_map: dict,
    functions_map: dict,
    attr_map: dict,
) -> int:
    """Fix short xrefs and inline code in a single file. Returns change count."""

    if filepath.suffix == ".py":
        file_context = _build_file_context(filepath)
    else:
        file_context = {}

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    changes = 0
    new_lines: list[str] = []

    for lineno, line in enumerate(lines, 1):
        ctx = file_context.get(lineno, {}) if file_context else {}

        def _fix_short(match: re.Match) -> str:
            nonlocal changes
            role = match.group(1)
            target = match.group(2)
            if target.startswith("~") or target.startswith("."):
                return match.group(0)
            if target in SKIP_NAMES:
                return match.group(0)
            if any(target.startswith(p) for p in SKIP_PREFIXES):
                return match.group(0)

            resolved = resolve_short_xref(
                target, ctx, classes_map, functions_map, attr_map
            )
            if resolved is None:
                return match.group(0)
            changes += 1
            return f"{role}`{resolved}`"

        new_line = REF_PATTERN.sub(_fix_short, line)

        def _fix_inline(match: re.Match) -> str:
            nonlocal changes
            code = match.group(1)
            if code.startswith("~"):
                return match.group(0)
            if code in SKIP_NAMES:
                return match.group(0)

            result = resolve_inline_code(
                code, ctx, classes_map, functions_map, attr_map
            )
            if result is None:
                return match.group(0)
            role, fqn = result
            changes += 1
            return f"{role}`{fqn}`"

        new_line = INLINE_CODE_PATTERN.sub(_fix_inline, new_line)
        new_lines.append(new_line)

    if changes > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"  {rel}: {changes} fix(es)")

    return changes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not REPORT_FILE.exists():
        print(f"ERROR: {REPORT_FILE} not found.  Run `python workflow/validate_refs.py` first.")
        return 1

    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)

    broken_refs = report.get("broken_refs", [])
    short_xrefs = report.get("short_xrefs", [])
    inline_code = report.get("inline_code", [])
    contexts = report.get("contexts", {})

    # Group actionable items by file (unique).
    files_needing_fixes: set[str] = set()
    for item in short_xrefs:
        files_needing_fixes.add(item["file"])
    for item in inline_code:
        files_needing_fixes.add(item["file"])

    if broken_refs:
        print("=== Broken references (cannot be auto-fixed) ===")
        for item in broken_refs:
            print(
                f"  {item['file']}:{item['lineno']}  "
                f"{item['target']}  -- {item['error']}"
            )
        print()

    if not files_needing_fixes:
        print("No auto-fixable issues.")
        if broken_refs:
            print(f"(But {len(broken_refs)} broken reference(s) need manual attention.)")
        return 0

    print("Building name maps for resolution...")
    classes_map, functions_map, attr_map = build_name_maps()
    print(f"  Classes: {len(classes_map)}")
    print(f"  Functions/Methods: {len(functions_map)}")
    print(f"  Class attributes: {len(attr_map)}")

    print(f"\nFixing {len(files_needing_fixes)} file(s)...")
    total = 0

    for rel in sorted(files_needing_fixes):
        filepath = ROOT / rel
        if not filepath.exists():
            print(f"  SKIP (not found): {rel}")
            continue
        changes = fix_file(
            filepath, rel, classes_map, functions_map, attr_map
        )
        total += changes

    print(f"\nDone: {total} fix(es) applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())