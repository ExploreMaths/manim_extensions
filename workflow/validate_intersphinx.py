#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Check cross-reference style and intersphinx coverage across the docs.

Two rules are enforced on every explicit Python cross-reference (roles
``:class:``, ``:func:``, ``:meth:``, ``:attr:``, ``:mod:``, ``:data:``,
``:exc:``, ``:obj:``) found in docstrings and ``.rst`` files:

1. **Tilde style.** A target with a module prefix (``x.y.Z``) must be written
   with a leading ``~`` (``:class:`~x.y.Z```) so Sphinx shows only the last
   component while the link stays fully qualified.  A bare single-identifier
   target (e.g. the builtin ``NotImplementedError``) must *not* carry a
   ``~`` — it has no prefix to abbreviate and the python intersphinx
   inventory registers builtins by their bare name, so ``~NotImplementedError``
   neither resolves nor links.

2. **Intersphinx coverage.** A reference whose top-level package is not part
   of this project must be covered by ``intersphinx_mapping`` in
   ``docs/source/conf.py``; otherwise it renders as plain text with no link
   (the defect that prompted adding ``pymunk``, ``scipy``, ``scikit-learn``,
   ``segno`` and ``typing_extensions``).

The check does not need the intersphinx inventories themselves — it only
mirrors the ``intersphinx_mapping`` keys from ``conf.py``.
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

# A Python object path: ``A.B.C`` (optionally preceded by ``~``).  Anything
# else (math text, prose) is not a cross-reference and is ignored.
_XREF_PATH = re.compile(r"~?[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$")


def intersphinx_packages() -> set[str]:
    """Read the package names behind each intersphinx_mapping entry in conf.py."""
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
    """Yield the raw target text and role for every explicit Python xref."""
    for m in re.finditer(r":(class|func|meth|attr|mod|data|exc|obj):`([^`]+)`", text):
        yield m.group(2).strip(), m.group(1)


def main() -> int:
    allowed = intersphinx_packages() | PY_STDLIB | {"manim_extensions"}
    no_tilde: "OrderedDict[str, list]" = OrderedDict()    # module path w/o ~
    bad_tilde: "OrderedDict[str, list]" = OrderedDict()   # bare identifier w/ ~
    missing_int: "OrderedDict[str, list]" = OrderedDict() # unmapped external lib

    py_files = glob.glob(f"{ROOT}/**/*.py", recursive=True)
    rst_files = glob.glob("docs/source/**/*.rst", recursive=True)

    def consider(path, raw, role):
        has_tilde = raw.startswith("~")
        tgt = raw.lstrip("~")
        if tgt.startswith("."):          # ``~.X`` current-module shorthand
            return
        if not _XREF_PATH.match(raw):    # math/prose, not a Python path
            return

        if "." in tgt:                   # module-prefixed target
            if not has_tilde:
                no_tilde.setdefault(tgt, []).append(f"{path}: `:{role}:`{tgt}``")
        else:                            # bare single identifier
            if has_tilde:
                bad_tilde.setdefault(tgt, []).append(f"{path}: `:{role}:`~{tgt}``")

        top = tgt.split(".", 1)[0] if "." in tgt else None
        if top is None or top in allowed:
            return
        missing_int.setdefault(top, []).append(f"{path}: `:{role}:`{raw}``")

    for path, doc in docstrings(py_files):
        for raw, role in find_xrefs(doc):
            consider(path, raw, role)
    for path in rst_files:
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        for raw, role in find_xrefs(text):
            consider(path, raw, role)

    problems = bool(no_tilde or bad_tilde or missing_int)

    def dump(title, table):
        if not table:
            return
        print(f"  [{title}] ({len(table)} unique targets)")
        for tgt, items in table.items():
            print(f"    {tgt}")
            for it in items[:6]:
                print("       ", it)
            if len(items) > 6:
                print(f"       ... and {len(items)-6} more")

    if not problems:
        print("PASS  xref-style and intersphinx")
        return 0

    print("FAIL  xref-style / intersphinx issues")
    dump("module path without leading ~ (add ~)", no_tilde)
    dump("bare identifier with ~ (drop ~)", bad_tilde)
    dump("external package missing intersphinx mapping", missing_int)
    print("\nTilde rule: `:class:`~x.y.Z`` for module-prefixed targets; bare")
    print("names (e.g. builtin NotImplementedError) get no ~. See CONTRIBUTING.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
