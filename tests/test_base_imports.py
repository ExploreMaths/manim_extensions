# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""The base package must import cleanly when every optional extra is absent.

Heavy dependencies (pymunk, shapely, kociemba, trimesh, moderngl, opencv,
pandas, and the ``ml`` extra) were split out of the core requirements into
``[project.optional-dependencies]`` and are lazy-imported at use time.
These tests spawn a subprocess that blocks those top-level packages via a
meta-path finder — emulating an environment where only the base package is
installed — and verify that importing ``manim_extensions`` and walking all
of its submodules still succeeds, and that a missing dependency produces
an error message naming the right extra.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_BLOCKER = """
import importlib.abc
import sys

BLOCKED = frozenset({
    "pymunk", "shapely", "kociemba", "trimesh",
    "cv2", "pandas", "matplotlib", "seaborn", "sklearn",
    "segno", "svgpathtools", "xmltodict", "requests",
    "docutils", "sphinx",
})


class _Blocker(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in BLOCKED:
            raise ImportError(f"No module named {name!r}")


sys.meta_path.insert(0, _Blocker())
"""

_WALKER = """
import importlib
import pkgutil

DOCS_TOOLS = {"docbuild", "testing"}


def walk(module):
    yield module.__name__
    if hasattr(module, "__path__"):
        prefix = module.__name__ + "."
        for info in pkgutil.iter_modules(module.__path__, prefix):
            if any(part in DOCS_TOOLS for part in info.name.split(".")):
                continue
            yield from walk(importlib.import_module(info.name))


import manim_extensions

modules = list(walk(manim_extensions))
print(f"WALKED {len(modules)}")
"""


def test_base_package_imports_without_extras():
    """Every submodule must import with all extras missing."""
    result = subprocess.run(
        [sys.executable, "-c", _BLOCKER + "\n" + _WALKER],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        "base import failed without extras:\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    assert "WALKED" in result.stdout


def test_missing_dependency_error_names_the_extra():
    """require() must tell the user which extra provides the package."""
    script = _BLOCKER + """
from manim_extensions.utils.deps import require

for name, extra in [("pymunk", "physics"), ("shapely", "physics"),
                    ("kociemba", "rubikscube"), ("trimesh", "meshes"),
                    ("cv2", "video"), ("pandas", "chemistry"),
                    ("segno", "qr"), ("svgpathtools", "svg"),
                    ("xmltodict", "automata"), ("requests", "chemistry")]:
    try:
        require(extra, name)
    except ImportError as exc:
        message = str(exc)
        assert f"manim_extensions[{extra}]" in message, message
    else:
        raise SystemExit(f"require({extra!r}, {name!r}) did not raise for a blocked module")
print("MESSAGES OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    assert "MESSAGES OK" in result.stdout
