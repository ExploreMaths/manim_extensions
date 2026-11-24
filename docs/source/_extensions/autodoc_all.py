# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Auto-document every public name of a module — at build time.

The ``.. autoall:: <dotted.module>`` directive enumerates the module's
public API — classes, functions, and data (constants) — and emits the
equivalent ``autoclass`` / ``autofunction`` / ``autodata`` directives
dynamically when Sphinx parses the page, so reference pages never
contain stale or hand-copied entry lists.

Options
-------
:types:      comma list of ``class``, ``function``, ``data``, or
              ``typealias`` (default: class, function and data). Use one
              directive per heading when a page documents Classes /
              Functions / Type Aliases / Constants in separate sections.
:recursive:  also enumerate every submodule of a package.
:skip:       space separated names to exclude (decisions recorded in
              the page source).
:values:     show each constant's full value instead of only its name
              (used by the colour palette, whose constants are
              uninformative as bare names). Other constants keep a
              normal ``= repr`` signature when the value is short;
              large containers show ``= dict with 10,083 entries``
              plus a ``Show`` toggle that reveals the exact
              value in place.
:missing-only:
              emit entries only for names that are NOT documented
              anywhere else. The set of documented names comes from a
              snapshot JSON produced by
              ``python workflow/validate_api_coverage.py --write-snapshot``
              (path configured via ``autodoc_all_snapshot`` in conf.py,
              default ``_extensions/api_documented.json`` relative to
              the conf directory). This keeps autoall blocks free of
              duplicates next to curated autoclass entries.

Member options (``members``, ``undoc-members`` ...) come from
``autodoc_default_options`` in conf.py; ``:show-inheritance:`` is added
here to classes with a real base class (everything but ``object``),
because the autodoc_inheritance source-read hook only sees autoclass
directives written literally in the .rst sources.

Usage::

    .. autoall:: manim_extensions.mobjects

    .. autoall:: manim_extensions.chemistry
       :recursive:
       :types: class

    .. autoall:: manim_extensions.machine_learning
       :recursive:
       :missing-only:
       :skip: config
"""

from __future__ import annotations

import ast
import html
import importlib
import importlib.util
import inspect
import json
import re
import pkgutil
import sys
import types
import typing
from pathlib import Path

try:
    from docutils import nodes
    from docutils.parsers.rst import Directive, directives
    from docutils.statemachine import StringList

    _HAS_DOCUTILS = True
except ImportError:
    # The coverage checker (workflow/validate_api_coverage.py) imports the
    # pure-python helpers below without docutils installed. Provide stubs
    # so the class body still defines; it is only ever *run* under Sphinx,
    # where docutils is guaranteed.
    _HAS_DOCUTILS = False

    class _Stub:
        def __init__(self, *args, **kwargs):
            pass

    class _StubNamespace:
        unchanged = flag = staticmethod(lambda *a, **k: None)
        container = staticmethod(lambda *a, **k: None)

    Directive = _Stub
    directives = _StubNamespace()
    nodes = _StubNamespace()

    class StringList(list):
        def __init__(self, lines=(), source=None):
            super().__init__(lines)


DEFAULT_SNAPSHOT = "_extensions/api_documented.json"

# Values up to this length stay inline in the signature; longer ones are
# collapsed behind the summary button.
INLINE_VALUE_LIMIT = 1000


def defining_dotted(module, name, obj):
    """Canonical ``module.name`` used as the snapshot key.

    Aliases of the same object resolve to the same key regardless of
    which module is being enumerated.
    """
    mod = getattr(obj, "__module__", None)
    if not mod or not mod.startswith("manim_extensions"):
        mod = module.__name__
    return f"{mod}.{name}"


def _defined_top_level_names(module):
    """Names bound at the module's top level, in **source definition order**.

    Returns a list (first occurrence wins) of names bound by ``def``/``class``/
    assignment at the top level. Imports are excluded because only
    Assign/AnnAssign/def/class statements are collected. The list both drives
    the output order of :func:`public_names` and identifies names whose
    ``__module__`` is foreign but which are defined here (decorator-wrapped
    functions, manim's ``ConvertToOpenGL`` metaclass-rebuilt classes, instance
    constants).
    """
    import ast

    path = getattr(module, "__file__", None)
    if not path or not str(path).endswith(".py"):
        return []
    try:
        source = open(path, encoding="utf-8").read()
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    names: list[str] = []
    seen: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            candidates = [node.name]
        elif isinstance(node, ast.Assign):
            candidates = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            candidates = [node.target.id]
        else:
            continue
        for nm in candidates:
            if nm not in seen:
                seen.add(nm)
                names.append(nm)
    return names


def _is_dunder(name):
    """Return whether *name* is a dunder (special, not merely private)."""
    return name.startswith("__") and name.endswith("__")


def public_names(module):
    """Return ``(name, object)`` pairs for every name in *module*.

    ``__all__`` entries come first when defined, then every name bound at the
    module's top level in **source definition order** (from
    :func:`_defined_top_level_names`) that ``__all__`` did not already list,
    followed by qualifying names discovered via ``dir()`` (dynamically
    created or re-exported with a matching ``__module__``). The reference
    manual and API coverage therefore see the whole module surface, including
    private names, not only the public export list. Submodules are never
    included; dunder names are still skipped.
    """
    candidates = list(getattr(module, "__all__", ()))
    defined = _defined_top_level_names(module)
    defined_set = set(defined)
    candidates.extend(n for n in defined if n not in candidates)
    for n in dir(module):
        if _is_dunder(n) or n in defined_set or n in candidates:
            continue
        obj = getattr(module, n, None)
        if obj is None or isinstance(obj, types.ModuleType):
            continue
        if getattr(obj, "__module__", None) == module.__name__:
            candidates.append(n)

    out = []
    seen: set[str] = set()
    for name in candidates:
        if name in seen or _is_dunder(name):
            continue
        try:
            obj = getattr(module, name)
        except AttributeError:
            continue
        if isinstance(obj, types.ModuleType):
            continue
        seen.add(name)
        out.append((name, obj))
    return out


def iter_package_modules(module):
    """The module itself plus every importable submodule (recursive)."""
    yield module
    if not hasattr(module, "__path__"):
        return
    for info in pkgutil.walk_packages(module.__path__, module.__name__ + "."):
        try:
            yield importlib.import_module(info.name)
        except Exception:
            continue


def is_type_alias(obj):
    """Return whether *obj* is a public type alias rather than a constant.

    ``typing.TypeAliasType`` covers PEP 695 aliases. ``types.GenericAlias``
    covers ``tuple[...]``-style builtins, ``types.UnionType`` covers
    ``X | Y``, and a non-``None`` :func:`typing.get_origin` covers
    ``typing.Union[...]``, ``typing.Callable[...]`` and the other
    subscription-based aliases. Type variables are parameters, not aliases.
    """
    type_alias_type = getattr(typing, "TypeAliasType", None)
    if type_alias_type is not None and isinstance(obj, type_alias_type):
        return True
    if isinstance(obj, (typing.TypeVar, typing.ParamSpec, typing.TypeVarTuple)):
        return False
    if isinstance(obj, (types.GenericAlias, types.UnionType)):
        return True
    return typing.get_origin(obj) is not None


_QUOTED_NAME_RE = re.compile(
    r"'([A-Za-z_][A-Za-z0-9_.]*)'|\"([A-Za-z_][A-Za-z0-9_.]*)\""
)


def _link_quoted_forward_refs(source, module):
    """Turn quoted forward references into resolvable names.

    ``SurfaceConfig`` is written as ``Union["GaussianSurface", ...]``; the
    ``:canonical:`` field parses Python annotation syntax, so a quoted string
    renders as a literal.  Replace the quotes only when the name resolves to a
    class in *module*, which makes Sphinx create a cross-reference to that
    class while leaving ordinary string literals untouched.
    """

    def replace(match):
        name = match.group(1) or match.group(2)
        target = getattr(module, name, None)
        return name if inspect.isclass(target) else match.group(0)

    return _QUOTED_NAME_RE.sub(replace, source)


_IMPORTED_SOURCES: dict[str, dict[str, str]] = {}


def _imported_sources(module) -> dict[str, str]:
    """Map local names of a module to the dotted paths they are imported from.

    ``py:type`` parses ``:canonical:`` in the page's Python-domain context
    (the enclosing package, not the alias's defining module), so names such
    as ``Square`` or ``List`` cannot be resolved from the module itself.
    Reading the ``from ... import ...`` statements gives the exact source
    path for typing helpers and Manim aliases, while classes are qualified
    through ``__module__`` below.
    """
    key = getattr(module, "__name__", "")
    cached = _IMPORTED_SOURCES.get(key)
    if cached is not None:
        return cached
    sources: dict[str, str] = {}
    path = getattr(module, "__file__", None)
    if path and str(path).endswith(".py"):
        try:
            tree = ast.parse(Path(path).read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            tree = None
        if tree is not None:
            for node in tree.body:
                if not isinstance(node, ast.ImportFrom):
                    continue
                base = node.module or ""
                if node.level:
                    package = getattr(module, "__package__", "") or key
                    try:
                        base = importlib.util.resolve_name(
                            "." * node.level + base, package
                        )
                    except (ImportError, ValueError):
                        continue
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    local = alias.asname or alias.name
                    sources[local] = f"{base}.{alias.name}" if base else alias.name
    _IMPORTED_SOURCES[key] = sources
    return sources


_TYPING_DATA_TYPES = {"_AnyMeta", "_CallableType", "_SpecialForm"}


def _qualified_alias_target(module, name: str) -> tuple[str | None, str | None]:
    """Return the absolute py-domain target and role for an alias token.

    Builtins (``str``, ``type``, ``None`` …) already resolve without a
    module prefix and are left alone.  A name defined in the alias module
    maps to that module's own ``py:type`` entry.  Imported classes use their
    defining module, which is more precise than a re-export (``from manim
    import Square`` becomes ``manim.mobject.geometry.polygram.Square``).
    Generic and typing aliases keep the path they were imported from, so
    ``List``/``Point3D`` point at ``typing``/``manim.typing`` instead of
    disappearing as unresolved names; ``Any``/``Callable`` resolve through
    the ``data`` role because that is how Python documents them.
    """
    if name == "None":
        return None, None
    obj = getattr(module, name, None)
    if obj is None or inspect.ismodule(obj):
        return None, None
    if name in _defined_names(module):
        kind = "class" if inspect.isclass(obj) else "type"
        return f"{module.__name__}.{name}", kind
    imported = _imported_sources(module).get(name)
    if type(obj).__name__ in _TYPING_DATA_TYPES:
        return imported, "data"
    if inspect.isclass(obj):
        defined_in = getattr(obj, "__module__", "")
        qualname = getattr(obj, "__qualname__", "")
        if defined_in and qualname and defined_in != "builtins":
            return f"{defined_in}.{qualname}", "class"
    if imported:
        return imported, "class"
    dotted = _alias_dotted_name(obj)
    if dotted:
        return dotted, "type"
    return None, None


def _qualify_type_alias_xrefs(app, doctree) -> None:
    """Give imported names inside ``py:type`` canonical values full targets.

    Sphinx's ``PyTypeAlias`` creates pending cross-references for every
    name in ``:canonical:``, but resolves them against the page's module
    context rather than the alias's defining module.  Re-targeting the
    nodes before references are resolved keeps the displayed short name
    while letting locally defined and imported classes/aliases link.
    """
    from sphinx.addnodes import desc_signature, pending_xref

    for sig in doctree.findall(desc_signature):
        desc = sig.parent
        if getattr(desc, "get", None) is None or desc.get("objtype") != "type":
            continue
        ids = sig.get("ids") or []
        if not ids:
            continue
        module_name, _, _alias_name = ids[0].rpartition(".")
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for xref in sig.findall(pending_xref):
            target = xref.get("reftarget")
            if not target or "." in target or target.startswith("~"):
                continue
            qualified, reftype = _qualified_alias_target(module, target)
            if qualified and qualified != target:
                xref["reftarget"] = qualified
                if reftype:
                    xref["reftype"] = reftype


def alias_definition(module, name):
    """Return ``(canonical_source, description)`` for a module-level alias.

    The source expression is taken from the AST so the page shows exactly
    what the code declares (including quoted forward references) instead of
    runtime spellings such as ``ForwardRef('GaussianSurface')``. A preceding
    ``#:`` comment becomes the entry description, matching the convention for
    module-level constants.
    """
    path = getattr(module, "__file__", None)
    if not path or not str(path).endswith(".py"):
        return None, ""
    try:
        source = open(path, encoding="utf-8").read()
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None, ""

    node = None
    for candidate in tree.body:
        if isinstance(candidate, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == name
                for target in candidate.targets
            ):
                node = candidate
                break
        elif (
            isinstance(candidate, ast.AnnAssign)
            and isinstance(candidate.target, ast.Name)
            and candidate.target.id == name
        ):
            node = candidate
            break
    if node is None or node.value is None:
        return None, ""

    canonical = ast.get_source_segment(source, node.value)
    if canonical:
        canonical = " ".join(canonical.split())
        canonical = _link_quoted_forward_refs(canonical, module)

    lines = source.splitlines()
    comments = []
    index = node.lineno - 2
    while index >= 0:
        stripped = lines[index].strip()
        if not stripped.startswith("#:"):
            break
        comments.append(stripped[2:].strip())
        index -= 1
    description = " ".join(reversed(comments)).strip()
    return canonical, description


def classify(obj):
    if inspect.isclass(obj):
        return "class"
    if inspect.isroutine(obj):
        return "function"
    if is_type_alias(obj):
        return "typealias"
    # Type variables (TypeVar / ParamSpec / TypeVarTuple) are parameters,
    # not data constants or aliases.
    if isinstance(obj, (typing.TypeVar, typing.ParamSpec, typing.TypeVarTuple)):
        return None
    return "data"


def summarize_value(obj):
    """Return a short, RST-safe description of a constant's value.

    Containers are summarised by type and length instead of being expanded
    into the page: the icon dictionary alone has 10 000 entries and would
    otherwise produce a 250 KB signature. The HTML renderer strips the
    double-backtick markup when it needs plain text.
    """
    if isinstance(obj, dict):
        return f"``dict`` with {len(obj):,} entries"
    if isinstance(obj, (list, tuple, set, frozenset)):
        return f"``{type(obj).__name__}`` with {len(obj):,} items"
    if isinstance(obj, str):
        if len(obj) <= 100:
            return "``" + repr(obj).replace("``", "`") + "``"
        return f"``str`` with {len(obj):,} characters"
    if obj is None or isinstance(obj, (bool, int, float, complex)):
        return f"``{obj!r}``"
    text = repr(obj)
    if len(text) <= 100:
        return "``" + text.replace("``", "`") + "``"
    return f"``{type(obj).__name__}`` object"


# Class/type references inside a value are written as ``<class
# 'module.Class'>``, ``type[module.Class]`` or ``ClassName(...)``.  Keep the
# collapsed value's class references, but replace the fully qualified spelling
# with a marker carrying both the lookup target and the short display text.
# ``default_value_links`` resolves the target against the Python domain at
# doctree-resolved time.
_VALUE_LINK_RE = re.compile(
    r"(?P<classrepr><class '(?P<classpath>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)'>)"
    r"|(?P<typeexpr>type\[(?P<typepath>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)\])"
    r"|(?P<dotted>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)"
    r"|(?P<call>[A-Z][A-Za-z0-9_]*(?=\())"
)


def _value_with_link_markers(obj):
    """HTML-escape the full value while marking class/type tokens."""
    text = repr(obj)
    parts = []
    pos = 0
    for match in _VALUE_LINK_RE.finditer(text):
        if match.start() > pos:
            parts.append(html.escape(text[pos : match.start()], quote=False))
        token = match.group(0)
        target = match.group("classpath") or match.group("typepath") or token
        short = target.rsplit(".", 1)[-1]
        if match.group("classrepr"):
            shown = short
        elif match.group("typeexpr"):
            shown = f"type[{short}]"
        else:
            shown = token
        escaped = html.escape(target, quote=True)
        fallback = html.escape(token, quote=True)
        parts.append(
            f'<span class="constant-value-ref" data-target="{escaped}" '
            f'data-fallback="{fallback}">'
            f"{html.escape(shown, quote=False)}</span>"
        )
        pos = match.end()
    if pos < len(text):
        parts.append(html.escape(text[pos:], quote=False))
    return "".join(parts)


def constant_value_payload_html(obj):
    """The hidden full value, revealed by the signature button.

    The summary itself is a ``:value:`` option on the generated
    ``autodatasummary`` directive, so it sits after the constant name in the
    signature. This raw block only contains the collapsed full value.
    ``default_value_links`` turns the marked class/type tokens into real
    cross-references after all Python objects have been registered.
    """
    full = _value_with_link_markers(obj)
    return [
        "   .. raw:: html",
        "",
        '      <div class="constant-value-payload" hidden>',
        '        <span class="constant-value-full-value">',
        '          <span class="constant-value-eq">=</span>',
        f'          <span class="constant-value-repr-text">{full}</span>',
        "        </span>",
        "      </div>",
    ]


class AutoAllDirective(Directive):
    """Expand into autodoc directives for public names of a module."""

    required_arguments = 1
    optional_arguments = 0
    has_content = False
    option_spec = {
        "types": directives.unchanged,
        "skip": directives.unchanged,
        "recursive": directives.flag,
        "missing-only": directives.flag,
        "values": directives.flag,
    }

    def _documented_set(self):
        env = self.state.document.settings.env
        conf = env.app.config
        snap_path = Path(confdir_of(env)) / getattr(
            conf, "autodoc_all_snapshot", DEFAULT_SNAPSHOT
        )
        if not snap_path.exists():
            raise self.severe(
                f"autoall: missing-only requested but snapshot not found: {snap_path}. "
                "Run: python workflow/validate_api_coverage.py --write-snapshot"
            )
        return set(json.loads(snap_path.read_text(encoding="utf-8")))

    def run(self):
        module_path = self.arguments[0]
        try:
            module = importlib.import_module(module_path)
        except Exception as exc:  # build-time guard
            raise self.severe(f"autoall: cannot import {module_path}: {exc}")

        want = {
            t.strip()
            for t in (self.options.get("types") or "class function data").split(",")
            if t.strip()
        }
        skip = set((self.options.get("skip") or "").split())
        missing_only = "missing-only" in self.options
        documented = self._documented_set() if missing_only else set()

        modules = (
            iter_package_modules(module)
            if "recursive" in self.options
            else iter([module])
        )

        lines = []
        seen = set()
        for mod in modules:
            defined_names = set(_defined_top_level_names(mod))
            for name, obj in public_names(mod):
                kind = classify(obj)
                if kind not in want or name in skip:
                    continue
                # A re-exported alias belongs to the module that defines it;
                # documenting it again here would create a second target and
                # duplicate entries under a recursive package directive.
                if kind == "typealias" and name not in defined_names:
                    continue
                key = defining_dotted(mod, name, obj)
                if key in seen:
                    continue
                seen.add(key)
                if missing_only and key in documented:
                    continue
                if kind == "class":
                    lines.append(f".. autoclass:: {key}")
                    # "Bases: object" is noise; only show inheritance for
                    # classes with a meaningful base.
                    meaningful_bases = [
                        b for b in getattr(obj, "__bases__", ()) if b is not object
                    ]
                    if meaningful_bases:
                        lines.append("   :show-inheritance:")
                    lines.append("")
                elif kind == "function":
                    lines += [f".. autofunction:: {key}", ""]
                elif kind == "typealias":
                    canonical, description = alias_definition(mod, name)
                    # ``py:type`` prefixes the enclosing module; use the
                    # short name plus an explicit ``:module:`` so a package
                    # page renders the alias under its real module instead
                    # of prefixing the full target twice.
                    lines.append(f".. py:type:: {name}")
                    lines.append(f"   :module: {mod.__name__}")
                    if canonical:
                        lines.append(f"   :canonical: {canonical}")
                    if description:
                        lines += ["", f"   {description}"]
                    lines.append("")
                elif "values" in self.options:
                    # Opt-in pages (the colour palette) show the full value
                    # next to the name; every other constants page uses the
                    # short-repr / expandable-summary branch below.
                    lines += [f".. autodata:: {key}", ""]
                else:
                    # Small scalars read naturally in the signature. Large
                    # containers are hidden behind a toggle: a full dict
                    # would put thousands of entries into the page, while a
                    # bare ``dict with 10,083 entries`` loses the value.
                    full = repr(obj)
                    if len(full) <= INLINE_VALUE_LIMIT and "\n" not in full:
                        # Let autodoc emit its normal ``= repr`` signature.
                        lines += [f".. autodata:: {key}", ""]
                    else:
                        summary = summarize_value(obj).replace("``", "")
                        lines += [
                            f".. autodatasummary:: {key}",
                            f"   :summary: {summary}",
                            "",
                            *constant_value_payload_html(obj),
                            "",
                        ]

        # legal for every name to be filtered out (skip / missing-only);
        # the directive then simply emits nothing
        if not lines:
            return []

        node = nodes.container()
        self.state.nested_parse(
            StringList(lines, source=module_path),
            self.content_offset,
            node,
        )
        return node.children


def confdir_of(env):
    return env.app.confdir


def _defined_names(module):
    return set(_defined_top_level_names(module))


def _alias_dotted_name(obj):
    """Find the project module-level name that *obj* was assigned to.

    Works for any alias shape (``typing.Union``, ``X | Y``, ``TypeAliasType``
    and builtin generics) by comparing identity against top-level assignments
    in loaded ``manim_extensions`` modules.  The runtime alias object is the
    only identity available after postponed annotations are evaluated, so we
    search the modules that actually define names rather than hardcoding a
    registry of aliases.
    """
    if not is_type_alias(obj):
        return None
    type_alias_type = getattr(typing, "TypeAliasType", None)
    if type_alias_type is not None and isinstance(obj, type_alias_type):
        return f"{obj.__module__}.{obj.__name__}"
    for module_name, module in list(sys.modules.items()):
        if not module_name.startswith("manim_extensions."):
            continue
        if hasattr(module, "__path__"):
            continue
        for name in _defined_names(module):
            if getattr(module, name, None) is obj:
                return f"{module_name}.{name}"
    return None


def _generic_alias_annotation(annotation):
    """Render a project type alias without expanding its definition.

    Direct aliases such as ``ColorRamp`` are matched first.  Generic
    wrappers whose single argument is a project alias, such as
    ``type[SurfaceConfig]``, keep the wrapper and link the alias.  Any other
    annotation falls through to the existing formatter.
    """
    dotted = _alias_dotted_name(annotation)
    if dotted is not None:
        return f":py:obj:`~{dotted}`"
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())
    if origin is not type or len(args) != 1:
        return None
    dotted = _alias_dotted_name(args[0])
    if dotted is None:
        return None
    return f":py:obj:`type`\\ \\[:py:obj:`~{dotted}`]"


_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _looks_like_alias(node):
    """Return whether an assignment value is a typing expression."""
    if isinstance(node, ast.Subscript):
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return True
    if isinstance(node, ast.Call):
        func = node.func
        return isinstance(func, ast.Name) and func.id in {"TypeAlias", "TypeAliasType"}
    return isinstance(node, (ast.Name, ast.Attribute))


def _discover_project_type_aliases():
    """Map public project alias names to their defining modules.

    Sphinx expands aliases after evaluating postponed annotations, so the
    annotation object no longer carries the original name.  ``autodoc_type_aliases``
    is the supported place to tell Sphinx which names are aliases; build that
    mapping from source instead of listing one alias per fix.
    """
    definitions = {}
    package = _PROJECT_ROOT / "manim_extensions"
    if not package.is_dir():
        return {}
    for path in sorted(package.rglob("*.py")):
        relative = path.relative_to(_PROJECT_ROOT).with_suffix("")
        module = ".".join(relative.parts)
        if module.endswith(".__init__"):
            module = module[: -len(".__init__")]
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for node in tree.body:
            if isinstance(node, ast.Assign):
                targets = [
                    target for target in node.targets if isinstance(target, ast.Name)
                ]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target]
                value = node.value
            else:
                continue
            if value is None or not _looks_like_alias(value):
                continue
            for target in targets:
                name = target.id
                if name.startswith("_") or not name[:1].isupper():
                    continue
                definitions.setdefault(name, []).append(f"{module}.{name}")
    # Prefer the shortest qualified path when two modules define the same
    # public alias name; the alias is normally written unqualified in code.
    return {name: f"~{min(paths, key=len)}" for name, paths in definitions.items()}


def _wrap_typehints_formatter(app):
    def on_config_inited(app, config):
        aliases = dict(getattr(config, "autodoc_type_aliases", None) or {})
        for name, dotted in _discover_project_type_aliases().items():
            aliases.setdefault(name, dotted)
        config.autodoc_type_aliases = aliases

        previous = getattr(config, "typehints_formatter", None)

        def formatter(annotation, *args):
            rendered = _generic_alias_annotation(annotation)
            if rendered is not None:
                return rendered
            if previous is None:
                return None
            return previous(annotation, *args)

        config.typehints_formatter = formatter

    app.connect("config-inited", on_config_inited)


def setup(app):
    from docutils.parsers.rst import directives as rst_directives
    from sphinx.ext.autodoc import DataDocumenter

    class SummaryDataDocumenter(DataDocumenter):
        """``autodatasummary``: a data entry with a compact signature value.

        ``autodata`` cannot take a ``:value:`` option, and its automatic
        value is the full ``repr``. This variant suppresses that automatic
        value and adds the supplied summary line instead, so a large dict
        keeps its place after the constant name without dumping thousands of
        entries into the signature.
        """

        objtype = "datasummary"
        directivetype = "data"
        option_spec = dict(DataDocumenter.option_spec)
        option_spec["summary"] = rst_directives.unchanged

        def add_directive_header(self, sig):
            self.options.no_value = True
            super().add_directive_header(sig)
            self.add_line(
                "   :value: " + self.options.summary,
                self.get_sourcename(),
            )

    app.add_autodocumenter(SummaryDataDocumenter)
    app.add_directive("autoall", AutoAllDirective)
    app.add_config_value("autodoc_all_snapshot", DEFAULT_SNAPSHOT, "env")
    _wrap_typehints_formatter(app)
    app.connect("doctree-read", _qualify_type_alias_xrefs)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
