#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Check that cross-references to external libraries have an intersphinx mapping.

sphinx-autodoc-typehints renders types from the code signature, but explicit
cross-references such as ``:class:`scipy.spatial.Voronoi``` only become links
when the referenced library is configured in ``intersphinx_mapping`` in
``docs/source/conf.py``.  A reference to an external package that is not in
that mapping renders as plain text (no link) — exactly the defect that was
recently fixed for ``pymunk``, ``scipy``, ``scikit-learn``, ``segno`` and
``typing_extensions``.

This validator scans every docstring and every ``.rst`` file for explicit
cross-reference roles (``:class:``, ``:func:``, ``:meth:``, ``:attr:``,
``:mod:``, ``:data:``, ``:exc:``, ``:obj:``) and reports any whose top-level
package is neither part of this project nor covered by an intersphinx mapping
nor a Python standard-library module.  The intent is to catch a newly added
reference to a third-party API before it silently loses its link.

The check does not need the intersphinx inventories themselves — it only
mirrors the ``intersphinx_mapping`` keys from ``conf.py``.  Adding a mapping
for a new library in ``conf.py`` is what makes its references resolvable, so
that is the fix this validator nudges toward.
"""

from __future__ import annotations

import ast
import glob
import re
import sys
from collections import OrderedDict

ROOT = "manim_extensions"
CONF = "docs/source/conf.py"

# Roles that produce a hyperlink to a Python object.
ROLES = {"class", "func", "meth", "attr", "mod", "data", "exc", "obj"}

# Python standard-library / toolchain modules commonly referenced from
# docstrings.  These resolve through the ``python`` intersphinx mapping or
# need no link at all, so they are never reported as missing intersphinx.
PY_STDLIB = {
    "typing", "typing_extensions", "builtins", "os", "sys", "io", "math",
    "functools", "itertools", "collections", "abc", "dataclasses", "enum",
    "pathlib", "json", "re", "string", "types", "contextlib", "weakref",
    "copy", "warnings", "inspect", "importlib", "logging", "datetime",
    "time", "decimal", "fractions", "statistics", "random", "bisect",
    "heapq", "array", "mmap", "struct", "ctypes", "html", "urllib",
    "subprocess", "shutil", "tempfile", "hashlib", "socket", "unittest",
    "pytest", "doctest", "operator", "numbers",
}

# ``scikit-learn``'s import name is ``sklearn``; keep this alias in sync with
# the ``intersphinx_mapping`` key in conf.py.
INTERSPHINX_PKG_ALIAS = {"scikit-learn": {"sklearn"}}


def intersphinx_packages() -> set[str]:
    """Read the package names behind each intersphinx_mapping entry in conf.py.

    For most entries the package name equals the mapping key (``numpy``,
    ``scipy``, ...).  A few keys differ from the import name (e.g.
    ``scikit-learn`` -> ``sklearn``); those aliases come from
    INTERSPHINX_PKG_ALIAS.
    """
    src = open(CONF, encoding="utf-8").read()
    m = re.search(r"intersphinx_mapping\s*=\s*\{(.*?)\}", src, re.S)
    if not m:
        sys.stderr.write("ERROR: could not locate intersphinx_mapping in %s\n" % CONF)
        sys.exit(2)
    keys = re.findall(r'"([a-z0-9_-]+)"\s*:\s*\(\s*"', m.group(1))
    pkgs = set(keys)
    for key in keys:
        pkgs |= INTERSPHINX_PKG_ALIAS.get(key, set())
    return pkgs


def docstrings(py_files):
    for path in py_files:
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node)
                if doc:
                    yield path, doc


def find_xrefs(text: str):
    """Yield (target, role) for every explicit Python cross-reference."""
    for m in re.finditer(r":(class|func|meth|attr|mod|data|exc|obj):`([^`]+)`", text):
        yield m.group(2).strip().lstrip("~"), m.group(1)


def main() -> int:
    allowed = intersphinx_packages() | PY_STDLIB
    problems: "OrderedDict[str, list]" = OrderedDict()

    py_files = glob.glob(f"{ROOT}/**/*.py", recursive=True)
    rst_files = glob.glob("docs/source/**/*.rst", recursive=True)

    def consider(path, target, role):
        if target.startswith("."):          # ``~.X`` current-module shorthand
            return
        if "." not in target:               # bare identifier: project or builtin
            return
        top = target.split(".", 1)[0]
        if top == "manim_extensions" or top.startswith("manim_extensions."):
            return
        if top in allowed:
            return
        problems.setdefault(top, []).append(f"{path}: `:{role}:`{target}``")

    for path, doc in docstrings(py_files):
        for target, role in find_xrefs(doc):
            consider(path, target, role)
    for path in rst_files:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        for target, role in find_xrefs(text):
            consider(path, target, role)

    if not problems:
        print("PASS  intersphinx")
        return 0

    print("FAIL  external-library cross-references missing intersphinx mappings")
    for top, items in problems.items():
        print(f"  [{top}] ({len(items)} refs)")
        for it in items:
            print("     ", it)
    print("\nAdd the library to `intersphinx_mapping` in %s (see CONTRIBUTING.md)." % CONF)
    return 1


if __name__ == "__main__":
    sys.exit(main())
