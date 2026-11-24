# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for ``workflow/validate_deprecations.py``."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

import validate_deprecations as checker  # noqa: E402


@pytest.fixture
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the checker at a temporary project root."""
    monkeypatch.setattr(checker, "ROOT", tmp_path)
    return tmp_path


def _scan(
    root: Path, source: str, deprecated: dict[str, str] | None = None
) -> list[str]:
    path = root / "sample.py"
    path.write_text(source, encoding="utf-8")
    return checker.scan(path, deprecated)


def test_clean_annotations(project_root: Path) -> None:
    assert (
        _scan(project_root, "from collections.abc import Callable\nx: list[int]\n")
        == []
    )


def test_import_from_typing(project_root: Path) -> None:
    violations = _scan(project_root, "from typing import List\n")
    assert len(violations) == 1
    assert "use `list`" in violations[0]


def test_import_alias_attribute(project_root: Path) -> None:
    violations = _scan(project_root, "import typing as t\nx: t.List[int]\n")
    assert len(violations) == 1
    assert "`typing.List`" in violations[0]


def test_string_annotation(project_root: Path) -> None:
    violations = _scan(
        project_root,
        "import typing as t\n\ndef f(x: 't.List[int]') -> 'typing.Dict[str, int]':\n    pass\n",
    )
    assert len(violations) == 2
    assert any("`typing.List`" in violation for violation in violations)
    assert any("`typing.Dict`" in violation for violation in violations)


def test_star_import_rejected(project_root: Path) -> None:
    violations = _scan(project_root, "from typing import *\n")
    assert len(violations) == 1
    assert "import names explicitly" in violations[0]


def test_typing_registry_is_discovered_from_runtime() -> None:
    aliases = checker._typing_aliases("typing")
    assert aliases["List"] == "list"
    assert aliases["Sequence"] == "collections.abc.Sequence"
    assert aliases["Counter"] == "collections.Counter"
    assert aliases["Text"] == "str"
    # Legal aliases with no parameters must not be rejected.
    assert "Hashable" not in aliases
    assert "Sized" not in aliases
    # Builtin descriptor aliases are not deprecated typing aliases.
    assert "MethodDescriptorType" not in aliases


def test_legal_typing_aliases_are_clean(project_root: Path) -> None:
    assert _scan(project_root, "from typing import Hashable, Sized\n") == []


def test_text_alias_is_deprecated(project_root: Path) -> None:
    violations = _scan(project_root, "from typing import Text\n")
    assert len(violations) == 1
    assert "use `str`" in violations[0]


def _install_fake_deprecated_module(
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    """Install a stdlib-like module whose public function is deprecated."""
    name = "stdlib_fake_deprecated"
    module = types.ModuleType(name)

    def old() -> None:
        """Old API."""

    old.__deprecated__ = "use new()"  # type: ignore[attr-defined]
    module.old = old  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(
        checker, "STDLIB_MODULES", checker.STDLIB_MODULES | frozenset({name})
    )
    return name


def test_other_stdlib_deprecated_import(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    name = _install_fake_deprecated_module(monkeypatch)
    violations = _scan(project_root, f"from {name} import old\n")
    assert len(violations) == 1
    assert "use new()" in violations[0]


def test_other_stdlib_deprecated_attribute(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    name = _install_fake_deprecated_module(monkeypatch)
    violations = _scan(project_root, f"import {name} as module\nmodule.old\n")
    assert len(violations) == 1
    assert "use new()" in violations[0]


def test_project_deprecated_symbol(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = project_root / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "legacy.py").write_text(
        "from manim_extensions.utils.deprecation import deprecated\n\n"
        '@deprecated("use new()")\n'
        "def old() -> None:\n"
        "    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(checker, "PACKAGE_DIR", package)
    assert checker.project_deprecations() == {"pkg.legacy.old": "use new()"}
    violations = _scan(
        project_root,
        "from pkg.legacy import old\n",
        checker.project_deprecations(),
    )
    assert len(violations) == 1
    assert "use new()" in violations[0]


def test_project_deprecated_attribute(
    project_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = project_root / "pkg"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "legacy.py").write_text(
        "from manim_extensions.utils.deprecation import deprecated\n\n"
        '@deprecated("use new()")\n'
        "def old() -> None:\n"
        "    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(checker, "PACKAGE_DIR", package)
    violations = _scan(
        project_root,
        "import pkg.legacy as legacy\nlegacy.old\n",
        checker.project_deprecations(),
    )
    assert len(violations) == 1
    assert "use new()" in violations[0]
