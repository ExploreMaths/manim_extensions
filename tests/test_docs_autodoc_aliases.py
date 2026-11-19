# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Guards for the Sphinx alias-preservation extension."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "source" / "_extensions"))

from autodoc_all import _discover_project_type_aliases, _generic_alias_annotation


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
