# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Check cross-reference style and intersphinx coverage across the docs.

Four rules are enforced on every explicit Python cross-reference (roles
``:class:``, ``:func:``, ``:meth:``, ``:attr:``, ``:mod:``, ``:data:``,
``:exc:``, ``:obj:``) found in docstrings and ``.rst`` files:

1. **Tilde style.** Every explicit Python cross-reference must be written
   with a leading ``~`` (``:class:`~x.y.Z```) so Sphinx shows only the last
   component while the link stays fully qualified.  This applies regardless
   of how long the target path is and also to bare single-identifier targets
   (e.g. ``:class:`~NotImplementedError```): the ``~`` only affects the
   rendered text, never whether the target resolves, so requiring it
   everywhere keeps the displayed name short and uniform.

2. **Fully qualified.** The target must name its full module path; a bare
   single-identifier target is only allowed when it is a Python builtin
   (``~dict``, ``~NotImplementedError``) — the ``python`` intersphinx
   inventory registers builtins by their bare name, so there is no longer
   path to write.  Any other bare name (or the ``~.X`` current-module
   shorthand) leaves the resolution dependent on the current module
   context, which silently produces dead links in autodoc output.

3. **Intersphinx coverage.** A reference whose top-level package is not part
   of this project must be covered by ``intersphinx_mapping`` in the
   configured Sphinx ``conf.py``; otherwise it renders as plain text with no
   link
   (the defect that prompted adding ``pymunk``, ``scipy``, ``scikit-learn``,
   ``segno`` and ``typing_extensions``).

4. **Inventory registration.** A reference to an external package must name an
   object that is actually registered in that package's ``objects.inv``.
   Sphinx only resolves a cross-reference when the *fully qualified* target
   appears in the inventory (e.g. ``:class:`~manim.TexTemplate``` fails
   because Manim registers ``manim.utils.tex.TexTemplate``, not
   ``manim.TexTemplate``); an unregistered target silently renders as an
   unstyled code span with no link.  This check downloads each external
   inventory once (a cache in ``/tmp`` avoids re-fetching on repeat runs) and
   flags every target that is not registered.

5. **Bare-identifier fallback.** Sphinx also accepts a target whose *last*
   component matches a registered name when the full path does not (for
   project-local autodoc names).  We do not chase that fallback for external
   packages: the fully qualified target must exist, otherwise the link is
   ambiguous or dead.

Inventories are fetched over the network.  When an inventory cannot be
downloaded (offline CI or a blocked host) that package's registration check
is skipped with a note — the other rules still run.
"""

from __future__ import annotations

import ast
import builtins
import glob
import os
import re
import sys
import urllib.request
import zlib
from collections import OrderedDict

from _context import DOCS, PACKAGE, SRC

CONF = DOCS / "conf.py"

# Inventories are fetched once per run and cached under this directory so
# repeat local runs and CI retries do not re-download every package.
INV_CACHE = os.path.join(os.environ.get("TMPDIR", "/tmp"), "me_intersphinx_inv")
_UA = "Mozilla/5.0 (validate-intersphinx)"

# Roles that produce a hyperlink to a Python object.
ROLES = {"class", "func", "meth", "attr", "mod", "data", "exc", "obj"}

# Python standard-library / toolchain modules commonly referenced from
# docstrings.  These resolve through the ``python`` intersphinx mapping or
# need no link at all, so they are never reported as missing intersphinx.
PY_STDLIB = {
    "typing",
    "typing_extensions",
    "builtins",
    "os",
    "sys",
    "io",
    "math",
    "functools",
    "itertools",
    "collections",
    "abc",
    "dataclasses",
    "enum",
    "pathlib",
    "json",
    "re",
    "string",
    "types",
    "contextlib",
    "weakref",
    "copy",
    "warnings",
    "inspect",
    "importlib",
    "logging",
    "datetime",
    "time",
    "decimal",
    "fractions",
    "statistics",
    "random",
    "bisect",
    "heapq",
    "array",
    "mmap",
    "struct",
    "ctypes",
    "html",
    "urllib",
    "subprocess",
    "shutil",
    "tempfile",
    "hashlib",
    "socket",
    "unittest",
    "pytest",
    "doctest",
    "operator",
    "numbers",
}

# ``scikit-learn``'s import name is ``sklearn``; keep this alias in sync with
# the ``intersphinx_mapping`` key in conf.py.
INTERSPHINX_PKG_ALIAS = {"scikit-learn": {"sklearn"}}

# A Python object path: ``A.B.C`` (optionally preceded by ``~``).  Anything
# else (math text, prose) is not a cross-reference and is ignored.
_XREF_PATH = re.compile(r"~?[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*$")

# Python builtins resolve through the ``python`` intersphinx inventory by
# their bare name (``~dict``, ``~NotImplementedError``); they have no module
# path to qualify, so they are exempt from the fully-qualified rule.
_BUILTIN_NAMES = frozenset(n for n in dir(builtins) if not n.startswith("_"))


def intersphinx_urls() -> dict[str, str]:
    """Map each intersphinx key to its inventory URL (from conf.py)."""
    src = open(CONF, encoding="utf-8").read()
    m = re.search(r"intersphinx_mapping\s*=\s*\{(.*?)\}", src, re.S)
    if not m:
        sys.stderr.write("ERROR: could not locate intersphinx_mapping in %s\n" % CONF)
        sys.exit(2)
    urls = {}
    for key, url in re.findall(r'"([a-z0-9_-]+)"\s*:\s*\(\s*"([^"]+)"', m.group(1)):
        urls[key] = url.rstrip("/") + "/objects.inv"
    return urls


def load_inventory(url: str) -> set[str] | None:
    """Return the set of registered object names, or ``None`` on failure."""
    os.makedirs(INV_CACHE, exist_ok=True)
    cache_key = url.replace("://", "__").replace("/", "_")
    cache_path = os.path.join(INV_CACHE, cache_key)
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as fh:
            return {line for line in fh.read().splitlines() if line}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        data = urllib.request.urlopen(req, timeout=30).read()
    except Exception as exc:  # network / 403 / timeout: skip this package
        print(
            f"  [note] could not fetch {url}: {exc.__class__.__name__}; "
            f"registration check skipped for this package"
        )
        return None
    if not data.startswith(b"# Sphinx inventory version"):
        print(f"  [note] unexpected inventory format at {url}; skipped")
        return None
    names = set()
    if data.startswith(b"# Sphinx inventory version 2"):
        try:
            body = zlib.decompress(data.split(b"\n", 4)[4]).decode()
            names = {line.split(" ", 1)[0] for line in body.splitlines() if line}
        except zlib.error:
            print(f"  [note] could not decompress inventory at {url}; skipped")
            return None
    else:  # version 1 legacy
        try:
            body = data.decode()
            names = {line.split(" ", 1)[0] for line in body.splitlines() if line}
        except UnicodeDecodeError:
            print(f"  [note] could not decode legacy inventory at {url}; skipped")
            return None
    with open(cache_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(sorted(names)))
    return names


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
    allowed = intersphinx_packages() | PY_STDLIB | {PACKAGE}
    no_tilde: "OrderedDict[str, list]" = OrderedDict()  # any target w/o ~
    not_fq: "OrderedDict[str, list]" = OrderedDict()  # bare name w/o module path
    missing_int: "OrderedDict[str, list]" = OrderedDict()  # unmapped external lib
    not_registered: "OrderedDict[str, list]" = OrderedDict()  # absent from inventory

    py_files = glob.glob(f"{SRC}/**/*.py", recursive=True)
    rst_files = glob.glob(f"{DOCS}/**/*.rst", recursive=True)

    # External inventories keyed by the package name a reference's top-level
    # segment uses (after INTERSPHINX_PKG_ALIAS mapping).
    url_by_key = intersphinx_urls()
    key_by_pkg: dict[str, str] = {}
    for key, url in url_by_key.items():
        for pkg in {key} | INTERSPHINX_PKG_ALIAS.get(key, set()):
            key_by_pkg[pkg] = key
    inventories: dict[str, set[str] | None] = {}

    def _inventory_for(tgt: str) -> set[str] | None:
        top = tgt.split(".", 1)[0]
        key = key_by_pkg.get(top)
        if key is None or key not in url_by_key:
            return None
        if key not in inventories:
            inventories[key] = load_inventory(url_by_key[key])
        return inventories[key]

    def consider(path, raw, role):
        has_tilde = raw.startswith("~")
        tgt = raw.lstrip("~")
        if tgt.startswith("."):  # ``~.X`` current-module shorthand is banned
            not_fq.setdefault(tgt, []).append(f"{path}: `:{role}:`{raw}``")
            return
        if not _XREF_PATH.match(raw):  # math/prose, not a Python path
            return

        if not has_tilde:  # every explicit Python xref needs ~
            no_tilde.setdefault(tgt, []).append(f"{path}: `:{role}:`{tgt}``")

        # Fully-qualified rule: a bare single-identifier target (no module
        # path) is only acceptable for Python builtins, which the ``python``
        # intersphinx inventory registers by their bare name (``~dict``).
        # Anything else must name its full ``module.path`` so the link never
        # depends on the current-module context or a last-component guess.
        if "." not in tgt and tgt not in _BUILTIN_NAMES:
            not_fq.setdefault(tgt, []).append(f"{path}: `:{role}:`{raw}``")

        top = tgt.split(".", 1)[0] if "." in tgt else None
        if top is None:
            return
        # Intersphinx coverage: unmapped external top-level package.
        if top not in allowed:
            missing_int.setdefault(top, []).append(f"{path}: `:{role}:`{raw}``")
        # Registration check: external target must exist in the inventory.
        # Internal (manim_extensions) and stdlib references are resolved
        # elsewhere (validate_refs / python intersphinx), so only mapped
        # third-party packages are checked here.
        if top in PY_STDLIB or top == PACKAGE:
            return
        inv = _inventory_for(tgt)
        if inv is not None and tgt not in inv:
            not_registered.setdefault(tgt, []).append(f"{path}: `:{role}:`{raw}``")

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

    problems = bool(no_tilde or not_fq or missing_int or not_registered)

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
    dump("target without leading ~ (add ~)", no_tilde)
    dump("target not fully qualified (add module path)", not_fq)
    dump("external package missing intersphinx mapping", missing_int)
    dump("target not registered in external inventory", not_registered)
    print("\nTilde rule: every explicit Python cross-reference must be written")
    print("with a leading ~ (`:class:`~x.y.Z``), regardless of path length,")
    print("so the rendered text always shows only the last component.")
    print("Fully-qualified rule: the target must carry its full module path;")
    print("bare names are only allowed for Python builtins (`~dict`).")
    print("A target missing from its package's objects.inv renders as an")
    print("unlinked code span; use the fully qualified name the package")
    print("registers (check the package's docs or objects.inv).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
