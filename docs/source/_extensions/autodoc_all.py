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
:types:      comma list of ``class``, ``function``, ``data``
              (default: all three). Use one directive per heading when
              a page documents Classes / Functions / Constants in
              separate sections.
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

import html
import importlib
import inspect
import json
import re
import pkgutil
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
    """Return ``(name, object)`` pairs for the module's documented API.

    Order: ``__all__`` wins when defined (author order); otherwise names
    appear in **source definition order** (from :func:`_defined_top_level_names`),
    followed by any qualifying names discovered via ``dir()`` that are not in
    the source (dynamically created or re-exported with a matching
    ``__module__``). Submodules are never included. Private names (a single
    leading underscore) are kept; dunder names are still skipped.
    """
    if hasattr(module, "__all__"):
        candidates = list(module.__all__)
    else:
        defined = _defined_top_level_names(module)
        defined_set = set(defined)
        candidates = list(defined)
        for n in dir(module):
            if _is_dunder(n) or n in defined_set:
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


def classify(obj):
    if inspect.isclass(obj):
        return "class"
    if inspect.isroutine(obj):
        return "function"
    # Type variables (TypeVar / ParamSpec / TypeVarTuple) and type aliases
    # (GenericAlias) are not data constants; keep them out of Constants pages.
    if isinstance(
        obj,
        (typing.TypeVar, typing.ParamSpec, typing.TypeVarTuple, types.GenericAlias),
    ):
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
            for name, obj in public_names(mod):
                kind = classify(obj)
                if kind not in want or name in skip:
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
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
