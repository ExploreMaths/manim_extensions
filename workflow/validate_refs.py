#!/usr/bin/env python3
"""Detect Sphinx cross-reference issues without modifying files.

Scans .py and .rst files for three categories of problems:

1. broken_refs   - references whose target cannot be imported/resolved
                   (e.g. :attr:`~manim_extensions.foo.Bar.baz` where
                    ``baz`` does not exist on ``Bar``).

2. short_xrefs    - Sphinx roles that lack a module path
                   (e.g. :attr:`__mob_index` instead of
                    :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index`).

3. inline_code    - back-ticked API names that should be cross-references
                   (e.g. `Mobject.scale` -> :meth:`~manim.mobject.mobject.Mobject.scale`).

Outputs a structured JSON report (``_refs_report.json``) consumable by
``fix_refs.py``, plus a human-readable summary on stdout /
``_validate_result.txt``.
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
# 1. AST-based name-map builders (shared by all detection categories)
# ---------------------------------------------------------------------------


class _ClassVisitor(ast.NodeVisitor):
    """Collect classes and top-level / methods from a module AST."""

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
    """Collect class-level data attributes (Assign / AnnAssign)."""

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


class _ContextVisitor(ast.NodeVisitor):
    """Map every line inside a class / method docstring to its enclosing
    class and module – used to resolve bare attribute names like
    ``__mob_index``."""

    def __init__(self, mod_path: str):
        self.mod_path = mod_path
        self.context: dict[int, dict[str, str]] = {}
        self._class_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        docstring = ast.get_docstring(node)
        if docstring:
            start = node.lineno
            end = node.end_lineno or start
            for line in range(start, end + 1):
                self.context[line] = {
                    "class": ".".join(self._class_stack),
                    "module": self.mod_path,
                }
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        docstring = ast.get_docstring(node)
        if docstring and self._class_stack:
            class_name = ".".join(self._class_stack)
            start = node.lineno
            end = node.end_lineno or start
            for line in range(start, end + 1):
                self.context[line] = {
                    "class": class_name,
                    "module": self.mod_path,
                }
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
    """Scan ``manim_extensions`` + installed ``manim`` and return
    ``(classes_map, functions_map, attr_map, contexts)``."""

    classes_map: dict[str, str] = {}
    functions_map: dict[str, str] = {}
    attr_map: dict[str, str] = {}
    contexts: dict[str, dict[int, dict[str, str]]] = {}

    # --- manim_extensions (highest priority) ---
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

        attr_collector = _AttrCollector(mod_path)
        attr_collector.visit(tree)
        for k, v in attr_collector.attrs.items():
            attr_map.setdefault(k, v)

        rel = str(py_file.relative_to(ROOT))
        ctx_visitor = _ContextVisitor(mod_path)
        ctx_visitor.visit(tree)
        if ctx_visitor.context:
            contexts[rel] = ctx_visitor.context

    # --- installed manim ---
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

            attr_collector = _AttrCollector(mod_path)
            attr_collector.visit(tree)
            for k, v in attr_collector.attrs.items():
                attr_map.setdefault(k, v)

    return classes_map, functions_map, attr_map, contexts


# ---------------------------------------------------------------------------
# 2. Broken-reference detection
# ---------------------------------------------------------------------------


def validate_reference(target: str) -> tuple[bool, str]:
    """Try to import / walk the target. Returns ``(ok, message)``.

    Only flags references whose *module* cannot be imported or whose
    *class* (first non-module segment after the module) cannot be found.
    Deep attribute chains are skipped because manim / manim_extensions
    use lazy-loading descriptors that make ``getattr`` unreliable.
    """
    if any(target.startswith(p) for p in SKIP_PREFIXES):
        return True, "skipped (external)"

    if not target.startswith("~"):
        return True, "skipped (relative or short)"

    fqn = target[1:]
    if fqn.startswith("."):
        return True, "skipped (relative)"

    parts = fqn.split(".")
    last_error: str | None = None

    for i in range(len(parts), 0, -1):
        mod_candidate = ".".join(parts[:i])
        rest = parts[i:] if i < len(parts) else []

        try:
            mod = importlib.import_module(mod_candidate)
        except (ImportError, ModuleNotFoundError) as e:
            last_error = str(e)
            continue

        if not rest:
            return True, f"module {mod_candidate}"

        # Module loaded; verify that the first remaining name exists
        # (it should be a class / top-level object).
        first = rest[0]
        if hasattr(mod, first):
            return True, f"class {fqn}"

        # Module imported but does not expose ``first``.  This target
        # may be broken; keep track of the error but try shorter module
        # prefixes (handles the case where the "real" module is deeper).
        last_error = (
            f"'{first}' not found in module '{mod_candidate}'"
        )
        # Don't break: fall through to try a shorter module prefix.

    return False, f"cannot resolve: {last_error}"


# ---------------------------------------------------------------------------
# 3. Short cross-reference detection
# ---------------------------------------------------------------------------


def _find_short_xrefs(filepath: Path) -> list[dict]:
    """Return every Sphinx role whose target lacks a module path.

    A target is considered "short" when:
    * it has no dots at all (``__mob_index``, ``Scene``), or
    * it has dots but the first segment is a simple name that is neither
      a known top-level package nor a built-in/skipped name (e.g.
      ``Mobject.scale`` – the class name, without a module).
    """
    results: list[dict] = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            for m in REF_PATTERN.finditer(line):
                role = m.group(1)
                target = m.group(2)
                if target.startswith("~") or target.startswith("."):
                    continue
                if target in SKIP_NAMES:
                    continue
                if any(target.startswith(p) for p in SKIP_PREFIXES):
                    continue

                head = target.split(".")[0]

                # Case A: no module path at all (bare name).
                if "." not in target:
                    results.append({
                        "lineno": lineno,
                        "role": role,
                        "target": target,
                        "match_start": m.start(),
                        "match_end": m.end(),
                    })
                    continue

                # Case B: has dots, but the first segment is likely a class
                #         name (starts with uppercase) rather than a module.
                #         Module names start lowercase by convention.
                if head and head[0].isupper() and head not in SKIP_NAMES:
                    results.append({
                        "lineno": lineno,
                        "role": role,
                        "target": target,
                        "match_start": m.start(),
                        "match_end": m.end(),
                    })
    return results


# ---------------------------------------------------------------------------
# 4. Inline-code detection
# ---------------------------------------------------------------------------


def _find_inline_code(
    filepath: Path, classes_map: dict, attr_map: dict
) -> list[dict]:
    """Return every back-ticked API-looking token inside *filepath*."""
    results: list[dict] = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            for m in INLINE_CODE_PATTERN.finditer(line):
                full = m.group(1)
                if full.startswith("~"):
                    continue
                if full in SKIP_NAMES:
                    continue
                # Include if:
                #   - contains dots (qualified-looking name), or
                #   - is a known class / attribute / method in our maps
                if "." in full or full in classes_map or full in attr_map:
                    results.append({
                        "lineno": lineno,
                        "code": full,
                        "match_start": m.start(),
                        "match_end": m.end(),
                    })
    return results


# ---------------------------------------------------------------------------
# 5. Orchestration
# ---------------------------------------------------------------------------


def main() -> int:
    print("Building name maps...")
    classes_map, functions_map, attr_map, contexts = build_name_maps()
    print(f"  Classes: {len(classes_map)}")
    print(f"  Functions/Methods: {len(functions_map)}")
    print(f"  Class attributes: {len(attr_map)}")

    broken_refs: list[dict] = []
    short_xrefs: list[dict] = []
    inline_code: list[dict] = []

    py_files = list(SRC.rglob("*.py"))
    rst_files = list(DOCS.rglob("*.rst"))
    targets = py_files + rst_files

    for filepath in sorted(targets):
        if "__pycache__" in str(filepath):
            continue
        rel = str(filepath.relative_to(ROOT)).replace("\\", "/")

        # --- broken refs (only for fully-qualified ones) ---
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        for lineno, line in enumerate(content.splitlines(), 1):
            for m in REF_PATTERN.finditer(line):
                target = m.group(2)
                if target.startswith("~") and not any(
                    target.startswith(p) for p in SKIP_PREFIXES
                ):
                    ok, msg = validate_reference(target)
                    if not ok:
                        broken_refs.append({
                            "file": rel,
                            "lineno": lineno,
                            "role": m.group(1),
                            "target": target,
                            "error": msg,
                        })

        # --- short xrefs ---
        for item in _find_short_xrefs(filepath):
            short_xrefs.append({"file": rel, **item})

        # --- inline code ---
        for item in _find_inline_code(filepath, classes_map, attr_map):
            inline_code.append({"file": rel, **item})

    # --- write JSON report ---
    report = {
        "broken_refs": broken_refs,
        "short_xrefs": short_xrefs,
        "inline_code": inline_code,
        "contexts": contexts,
    }
    json_file = ROOT / "workflow" / "_refs_report.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    # --- human-readable summary ---
    lines: list[str] = []
    lines.append("=== Validation Summary ===")
    lines.append(f"Broken references:     {len(broken_refs)}")
    lines.append(f"Short cross-references: {len(short_xrefs)}")
    lines.append(f"Inline code candidates: {len(inline_code)}")

    if broken_refs:
        lines.append("\n--- Broken references ---")
        for item in broken_refs:
            lines.append(
                f"  ERROR  {item['file']}:{item['lineno']}  "
                f"{item['target']}  -- {item['error']}"
            )

    if short_xrefs:
        lines.append("\n--- Short cross-references ---")
        for item in short_xrefs:
            lines.append(
                f"  {item['file']}:{item['lineno']}  "
                f"{item['role']}`{item['target']}`"
            )

    if inline_code:
        lines.append("\n--- Inline code candidates ---")
        for item in inline_code:
            lines.append(f"  {item['file']}:{item['lineno']}  `{item['code']}`")

    total_issues = len(broken_refs) + len(short_xrefs) + len(inline_code)
    if total_issues:
        lines.append(f"\nFAILED: {total_issues} issue(s) found.")
        lines.append("Run `python workflow/fix_refs.py` to auto-fix what it can.")
    else:
        lines.append("\nAll references look good!")

    output = "\n".join(lines)
    outfile = ROOT / "workflow" / "_validate_result.txt"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(output + f"\n\n(Detailed JSON: {json_file.name})\n")
    print(output)

    return 1 if total_issues else 0


if __name__ == "__main__":
    sys.exit(main())