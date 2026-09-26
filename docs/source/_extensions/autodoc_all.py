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

import importlib
import inspect
import json
import pkgutil
import types
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


def defining_dotted(module, name, obj):
    """Canonical ``module.name`` used as the snapshot key.

    Aliases of the same object resolve to the same key regardless of
    which module is being enumerated.
    """
    mod = getattr(obj, "__module__", None)
    if not mod or not mod.startswith("manim_extensions"):
        mod = module.__name__
    return f"{mod}.{name}"


def public_names(module):
    """Return ``(name, object)`` pairs for the module's public API.

    ``__all__`` wins when defined; otherwise names defined in this very
    module (not imported elsewhere). Submodules are never included.
    """
    if hasattr(module, "__all__"):
        candidates = list(module.__all__)
    else:
        candidates = [
            n
            for n in dir(module)
            if not n.startswith("_")
            and getattr(module, n).__class__ is not types.ModuleType
            and getattr(getattr(module, n), "__module__", None) == module.__name__
        ]
    out = []
    for name in candidates:
        try:
            obj = getattr(module, name)
        except AttributeError:
            continue
        if isinstance(obj, types.ModuleType) or name.startswith("_"):
            continue
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
    return "data"


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
    }

    def _documented_set(self):
        env = self.state.document.settings.env
        conf = env.app.config
        snap_path = Path(confdir_of(env)) / getattr(conf, "autodoc_all_snapshot", DEFAULT_SNAPSHOT)
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

        modules = iter_package_modules(module) if "recursive" in self.options else iter([module])

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
                else:
                    lines += [f".. autodata:: {key}", ""]

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
    app.add_directive("autoall", AutoAllDirective)
    app.add_config_value("autodoc_all_snapshot", DEFAULT_SNAPSHOT, "env")
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
