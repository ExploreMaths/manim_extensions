# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Guards for the Sphinx alias-preservation extension."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "source" / "_extensions"))

from autodoc_all import (
    _discover_project_type_aliases,
    _generic_alias_annotation,
    _qualified_alias_target,
)


def test_project_type_aliases_are_discovered() -> None:
    aliases = _discover_project_type_aliases()
    assert aliases["ColorRamp"] == "~manim_extensions.three_d.core.ColorRamp"
    assert aliases["SurfaceConfig"] == "~manim_extensions.three_d.core.SurfaceConfig"


def test_direct_alias_renders_as_link() -> None:
    from manim_extensions.three_d.core import ColorRamp

    assert _generic_alias_annotation(ColorRamp) == (
        ":py:obj:`~manim_extensions.three_d.core.ColorRamp`"
    )


def test_generic_alias_keeps_wrapper() -> None:
    from manim_extensions.three_d.core import SurfaceConfig

    assert _generic_alias_annotation(type[SurfaceConfig]) == (
        ":py:obj:`type`\\ \\[:py:obj:`~manim_extensions.three_d.core.SurfaceConfig`]"
    )


def test_imported_alias_names_keep_full_targets() -> None:
    import manim_extensions.algorithm.node as node

    assert _qualified_alias_target(node, "Square") == (
        "manim.mobject.geometry.polygram.Square",
        "class",
    )
    assert _qualified_alias_target(node, "Circle") == (
        "manim.mobject.geometry.arc.Circle",
        "class",
    )
    # Builtins already resolve in the py domain and must stay bare.
    assert _qualified_alias_target(node, "str") == (None, None)
    # ``type`` is a builtin wrapper, not an alias to link.
    assert _qualified_alias_target(node, "type") == (None, None)


def test_typing_data_uses_data_role() -> None:
    import manim_extensions.data_structures.m_array as m_array

    assert _qualified_alias_target(m_array, "Any") == ("typing.Any", "data")
    assert _qualified_alias_target(m_array, "List") == ("typing.List", "class")


def test_local_alias_keeps_its_own_name() -> None:
    from manim_extensions.chemistry.utils.parsers import base_parser
    from manim_extensions.meshes import types

    assert _qualified_alias_target(base_parser, "MoleculeData") == (
        "manim_extensions.chemistry.utils.parsers.base_parser.MoleculeData",
        "type",
    )
    # ``Faces`` and ``VarArray`` share one runtime object; the target must
    # follow the name written in the alias, not whichever assignment is
    # found first by identity.
    assert _qualified_alias_target(types, "Faces") == (
        "manim_extensions.meshes.types.Faces",
        "type",
    )
