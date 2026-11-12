# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

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

4. ambiguous_classes - back-ticked class names that resolve to several
                   project classes (e.g. ``Gear`` names both
                   ``manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear``
                   and ``manim_extensions.pymunk.custom_mobjects.gear.Gear``).
                   Ambiguous names are never auto-linked by the Sphinx
                   extension, so a bare back-tick leaves the reader with a
                   plain code span.  Disambiguate by writing an explicit
                   role with the full module path (``:class:`~...``).

5. unlinked_classes - plain words in prose that are project class names
                   (or their plural, ``+s``) and are NOT written as a
                   cross-reference.  E.g. a docstring sentence saying
                   ``MCAtoms`` instead of :class:`~...MCAtom`.
                   Every spelling counts, including names that are also
                   ordinary English words (``Node``, ``Layout``). Code
                   blocks, directives, doctests, section titles and
                   back-ticked (inline code) spans are skipped.

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

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REF_PATTERN = re.compile(r"(:(?:class|meth|func|attr|mod|exc|obj):)`([^`]+)`")

INLINE_CODE_PATTERN = re.compile(
    r"`{1,2}([A-Z][a-zA-Z_0-9]*(?:\.[a-zA-Z_][a-zA-Z_0-9]*(?:\(\))?)*)`{1,2}"
)

SKIP_NAMES = frozenset(
    {
        "int",
        "float",
        "str",
        "bool",
        "list",
        "dict",
        "tuple",
        "set",
        "numpy.ndarray",
        "ndarray",
        "NotImplementedError",
        "ValueError",
        "TypeError",
        "KeyError",
        "IndexError",
        "AttributeError",
        "RuntimeError",
        "Exception",
        "object",
    }
)

SKIP_SUFFIXES = (".md", ".rst", ".py", ".toml", ".yml", ".yaml", ".cfg", ".ini", ".txt")


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
    ``(classes_map, functions_map, attr_map, contexts, project_classes_map,
    ambiguous_classes)``."""

    classes_map: dict[str, str] = {}
    functions_map: dict[str, str] = {}
    attr_map: dict[str, str] = {}
    contexts: dict[str, dict[int, dict[str, str]]] = {}
    project_classes_map: dict[str, str] = {}
    class_fqns: dict[str, set[str]] = {}

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
        project_classes_map.update(visitor.classes)
        for name, fqn in visitor.classes.items():
            class_fqns.setdefault(name, set()).add(fqn)
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

    ambiguous_classes = {
        name: sorted(fqns) for name, fqns in class_fqns.items() if len(fqns) > 1
    }

    return (
        classes_map,
        functions_map,
        attr_map,
        contexts,
        project_classes_map,
        ambiguous_classes,
    )


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
    if not target.startswith("~"):
        return True, "skipped (relative or short)"

    fqn = target[1:]
    if fqn.startswith("."):
        return True, "skipped (relative)"

    parts = fqn.split(".")
    if parts[0] in SKIP_NAMES:
        return True, f"skipped (builtin / known name {parts[0]})"

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
        last_error = f"'{first}' not found in module '{mod_candidate}'"
        # Don't break: fall through to try a shorter module prefix.

    return False, f"cannot resolve: {last_error}"


# ---------------------------------------------------------------------------
# 3. Short cross-reference detection
# ---------------------------------------------------------------------------


def _role_target(raw: str) -> str:
    """Return the target of a role, unwrapping ``Text <target>`` titles."""
    if raw.endswith(">") and "<" in raw:
        return raw[raw.rindex("<") + 1 : -1].strip()
    return raw


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
                target = _role_target(m.group(2))
                if target.startswith("~") or target.startswith("."):
                    continue
                if target in SKIP_NAMES:
                    continue

                head = target.split(".")[0]

                # Case A: no module path at all (bare name).
                if "." not in target:
                    results.append(
                        {
                            "lineno": lineno,
                            "role": role,
                            "target": target,
                            "match_start": m.start(),
                            "match_end": m.end(),
                        }
                    )
                    continue

                # Case B: has dots, but the first segment is likely a class
                #         name (starts with uppercase) rather than a module.
                #         Module names start lowercase by convention.
                if head and head[0].isupper() and head not in SKIP_NAMES:
                    results.append(
                        {
                            "lineno": lineno,
                            "role": role,
                            "target": target,
                            "match_start": m.start(),
                            "match_end": m.end(),
                        }
                    )
    return results


# ---------------------------------------------------------------------------
# 4. Inline-code detection
# ---------------------------------------------------------------------------


def _find_inline_code(filepath: Path, classes_map: dict, attr_map: dict) -> list[dict]:
    """Return every back-ticked API-looking token inside ``filepath``."""
    results: list[dict] = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            for m in INLINE_CODE_PATTERN.finditer(line):
                full = m.group(1)
                if full.startswith("~"):
                    continue
                if full in SKIP_NAMES:
                    continue
                if any(full.endswith(suf) for suf in SKIP_SUFFIXES):
                    continue
                # Include if:
                #   - contains dots (qualified-looking name), or
                #   - is a known class / attribute / method in our maps
                if "." in full or full in classes_map or full in attr_map:
                    results.append(
                        {
                            "lineno": lineno,
                            "code": full,
                            "match_start": m.start(),
                            "match_end": m.end(),
                        }
                    )
    return results


# ---------------------------------------------------------------------------
# 5. Ambiguous-class detection
# ---------------------------------------------------------------------------


ROLE_ROLE_PREFIX = re.compile(r":(?:class|meth|func|attr|mod|exc|obj|data):$")


def _find_ambiguous_classes(
    filepath: Path, ambiguous_classes: dict[str, list[str]]
) -> list[dict]:
    """Return every bare back-ticked name that names several project
    classes.  A name preceded by an explicit Sphinx role (``:class:``,
    ``:data:``, ...) is already disambiguated and skipped."""
    results: list[dict] = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, 1):
            for m in INLINE_CODE_PATTERN.finditer(line):
                full = m.group(1)
                if full in SKIP_NAMES:
                    continue
                if any(full.endswith(suf) for suf in SKIP_SUFFIXES):
                    continue
                if full not in ambiguous_classes:
                    continue
                # Skip names written as explicit roles (`:class:`Gear``).
                if ROLE_ROLE_PREFIX.search(line[: m.start()]):
                    continue
                results.append(
                    {
                        "lineno": lineno,
                        "code": full,
                        "targets": ambiguous_classes[full],
                        "match_start": m.start(),
                        "match_end": m.end(),
                    }
                )
    return results


# ---------------------------------------------------------------------------
# 6. Unlinked class-name detection (plain prose words)
# ---------------------------------------------------------------------------

WORD_PATTERN = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*\b")
DIRECTIVE_START = re.compile(r"\s*\.\.\s+[\w-]+")
BACKTICK_SPAN = re.compile(r"`+[^`]*`+")
BOLD_SPAN = re.compile(r"\*\*[^*]+\*\*")
UNLINKED_OK = re.compile(r"^[ \t]*\.\.[ \t]+unlinked-class-ok[ \t]+(.*)$")
UNLINKED_OK_FILE = re.compile(r"^[ \t]*\.\.[ \t]+unlinked-class-ok-file[ \t]+(.*)$")
UNLINKED_OK_COMMENT = re.compile(r"#[ \t]*unlinked-class-ok:[ \t]*(.*)$")
PARAM_DECL = re.compile(r"^[ \t]*[A-Za-z_*][\w.{}\[\], ]*[ \t]*:[ \t]")
UNDERLINE = re.compile(r"^[=\-~^\"'`#*+<>_]{3,}\s*$")


def _paragraph_ids(lines: list[str]) -> list[int]:
    """Return the paragraph number of every line (``-1`` for blank lines)."""
    ids: list[int] = []
    current = -1
    in_paragraph = False
    for line in lines:
        if not line.strip():
            in_paragraph = False
            ids.append(-1)
            continue
        if not in_paragraph:
            current += 1
            in_paragraph = True
        ids.append(current)
    return ids


def _prose_lines(text: str) -> list[tuple[int, str, int]]:
    """Return ``(line_offset, line, paragraph)`` for prose lines of ``text``.

    Code samples are dropped: directive bodies (``.. code-block::``,
    ``.. manim::``, ``.. note::`` ...), literal blocks introduced by a
    trailing ``::``, doctest input and field lists (``:param x:``).
    Section titles (a word followed by an underline) are skipped too,
    because a class name used as a heading is not prose.
    """
    lines = text.splitlines()
    titles: set[int] = set()
    for index, line in enumerate(lines):
        if not UNDERLINE.match(line):
            continue
        before = lines[index - 1] if index >= 1 else ""
        after = lines[index + 1] if index + 1 < len(lines) else ""
        if index >= 1 and before.strip() and not UNDERLINE.match(before):
            # title above the underline
            titles.add(index - 1)
            titles.add(index)
        elif after.strip() and after.strip() and index + 2 < len(lines):
            if UNDERLINE.match(lines[index + 2]):
                # overlined title
                titles.add(index + 1)
                titles.add(index + 2)

    paragraphs = _paragraph_ids(lines)
    prose: list[tuple[int, str, int]] = []
    skip = False
    base = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if skip:
            if stripped == "" or indent > base:
                continue
            skip = False
        if UNLINKED_OK.match(line) or UNLINKED_OK_FILE.match(line):
            continue
        if DIRECTIVE_START.match(line):
            base = indent
            skip = True
            continue
        if (
            stripped.endswith(":")
            and not stripped.endswith("::")
            and not stripped.startswith("..")
        ):
            base = indent
            skip = True
            continue
        if stripped.endswith("::") and not stripped.startswith(".."):
            base = indent
            skip = True
            continue
        if index in titles:
            continue
        if stripped.startswith((">>>", "...", ":")):
            continue
        prose.append((index, line, paragraphs[index]))
    return prose


def _iter_docstrings(filepath: Path):
    """Yield ``(docstring_text, first_line_number)`` for every docstring.

    The text is taken from the source literal rather than from
    ``ast.get_docstring``: ``cleandoc`` strips the leading blank lines and
    dedents, which makes the line numbers unusable for reporting.
    """
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        if not ast.get_docstring(node) or not getattr(node, "body", None):
            continue
        literal = node.body[0].value
        raw = ast.get_source_segment(source, literal)
        if not raw:
            continue
        prefix = re.match(r"[rRuUbBfF]{0,3}", raw).end()
        raw = raw[prefix:]
        quote = 3 * '"' if raw.startswith(3 * '"') else 3 * "'"
        body = raw[len(quote) :]
        if body.endswith(quote):
            body = body[: -len(quote)]
        yield body, literal.lineno


def _find_unlinked_classes(
    filepath: Path,
    project_classes_map: dict[str, str],
    is_rst: bool,
) -> list[dict]:
    """Return class names mentioned as plain words instead of as a
    cross-reference.

    A word counts when it matches a project class name exactly (case
    sensitive) or is that name with a trailing ``s`` (plural).  Text
    inside back-ticks is skipped: it is inline code, already reported by
    ``inline_code``, not prose.
    """
    plural_targets: dict[str, str] = {}
    for name, fqn in project_classes_map.items():
        plural_targets[name] = fqn
        plural_targets[f"{name}s"] = fqn

    if is_rst:
        sources = [(filepath.read_text(encoding="utf-8", errors="replace"), 1)]
    else:
        sources = list(_iter_docstrings(filepath))

    def _words(payload: str) -> set[str]:
        return {w for w in re.split(r"[ ,]+", payload) if w}

    file_allowed: set[str] = set()
    scoped: dict[tuple[int, int], set[str]] = {}
    for index, (text, _first_line) in enumerate(sources):
        lines = text.splitlines()
        paragraphs = _paragraph_ids(lines)
        for line_no, line in enumerate(lines):
            marker = UNLINKED_OK_FILE.match(line)
            if marker:
                file_allowed |= _words(marker.group(1))
                continue
            marker = UNLINKED_OK.match(line)
            if not marker:
                continue
            words = _words(marker.group(1))
            paragraph = paragraphs[line_no]
            # A marker alone between blank lines applies to the paragraph
            # that follows it; one embedded in a paragraph applies to that
            # paragraph only.
            has_text = any(
                paragraphs[i] == paragraph
                and not UNLINKED_OK.match(lines[i])
                and not UNLINKED_OK_FILE.match(lines[i])
                for i in range(len(lines))
            )
            scope = paragraph if has_text else paragraph + 1
            scoped.setdefault((index, scope), set()).update(words)
    if not is_rst:
        # Explicit whole-file escape hatch.
        for line in filepath.read_text(encoding="utf-8", errors="replace").splitlines():
            marker = UNLINKED_OK_COMMENT.search(line)
            if marker:
                file_allowed |= _words(marker.group(1))

    results: list[dict] = []
    for index, (text, first_line) in enumerate(sources):
        for offset, line, paragraph in _prose_lines(text):
            if UNLINKED_OK.match(line) or UNLINKED_OK_FILE.match(line):
                continue
            cleaned = BACKTICK_SPAN.sub(" ", line)
            cleaned = BOLD_SPAN.sub(" ", cleaned)
            bare = cleaned.strip().rstrip(".,;:")
            for match in WORD_PATTERN.finditer(cleaned):
                word = match.group()
                target = plural_targets.get(word)
                if target is None:
                    continue
                if word in file_allowed:
                    continue
                if word in scoped.get((index, paragraph), ()):
                    continue
                # A line holding nothing but the name is a type
                # declaration (``Returns`` / ``Raises`` sections), not
                # prose.
                if bare == word:
                    continue
                # ``name : Type`` parameter/attribute declarations name a
                # type; they are not prose either.
                decl = PARAM_DECL.match(cleaned)
                if decl and decl.end() <= match.start():
                    continue
                results.append(
                    {
                        "lineno": first_line + offset,
                        "code": word,
                        "target": target,
                        "match_start": match.start(),
                        "match_end": match.end(),
                    }
                )
    return results


# ---------------------------------------------------------------------------
# 7. Orchestration
# ---------------------------------------------------------------------------


def main() -> int:
    (
        classes_map,
        functions_map,
        attr_map,
        contexts,
        project_classes_map,
        ambiguous_classes,
    ) = build_name_maps()

    broken_refs: list[dict] = []
    short_xrefs: list[dict] = []
    inline_code: list[dict] = []
    ambiguous: list[dict] = []
    unlinked: list[dict] = []

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
                if target.startswith("~"):
                    ok, msg = validate_reference(target)
                    if not ok:
                        broken_refs.append(
                            {
                                "file": rel,
                                "lineno": lineno,
                                "role": m.group(1),
                                "target": target,
                                "error": msg,
                            }
                        )

        # --- short xrefs ---
        for item in _find_short_xrefs(filepath):
            short_xrefs.append({"file": rel, **item})

        # --- inline code ---
        for item in _find_inline_code(filepath, project_classes_map, attr_map):
            inline_code.append({"file": rel, **item})

        # --- ambiguous classes ---
        for item in _find_ambiguous_classes(filepath, ambiguous_classes):
            ambiguous.append({"file": rel, **item})

        # --- plain-word class mentions (not written as a reference) ---
        # The changelog records history verbatim; class names there are
        # not documentation cross-references.
        if rel == "docs/source/changelog.rst":
            continue
        for item in _find_unlinked_classes(
            filepath, project_classes_map, is_rst=filepath.suffix == ".rst"
        ):
            unlinked.append({"file": rel, **item})

    # --- write JSON report ---
    report = {
        "broken_refs": broken_refs,
        "short_xrefs": short_xrefs,
        "inline_code": inline_code,
        "ambiguous_classes": ambiguous,
        "unlinked_classes": unlinked,
        "contexts": contexts,
    }
    # --- human-readable summary ---
    total_issues = (
        len(broken_refs)
        + len(short_xrefs)
        + len(inline_code)
        + len(ambiguous)
        + len(unlinked)
    )
    if total_issues:
        print(f"FAIL  cross-refs  {total_issues} issue(s)\n")
        for item in broken_refs:
            print(
                f"  {item['file']}:{item['lineno']}  cannot-resolve: {item['target']} -- {item['error']}"
            )
        for item in short_xrefs:
            print(
                f"  {item['file']}:{item['lineno']}  short-xref: {item['role']}`{item['target']}`"
            )
        for item in inline_code:
            print(f"  {item['file']}:{item['lineno']}  inline-code: `{item['code']}`")
        for item in ambiguous:
            print(
                f"  {item['file']}:{item['lineno']}  ambiguous-class: "
                f"`{item['code']}` -> " + ", ".join(item["targets"])
            )
        for item in unlinked:
            print(
                f"  {item['file']}:{item['lineno']}  unlinked-class: "
                f"{item['code']} -> :class:`~{item['target']}`"
            )
        print(f"\nTotal: {total_issues} issue(s)")
        print("Run `python workflow/fix_refs.py` to auto-fix what it can.")
    else:
        print("PASS  cross-refs")

    # Still write the JSON report for downstream tooling.
    json_file = ROOT / "workflow" / "_refs_report.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    return 1 if total_issues else 0


if __name__ == "__main__":
    sys.exit(main())
