# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Regression test for sample assets in the layout probe."""

import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

import check_example_layout as layout  # noqa: E402
from _example_assets import ExampleAsset  # noqa: E402


def test_stage_assets_accepts_example_asset(tmp_path: Path) -> None:
    """The probe stages ``ExampleAsset.path``, not the dataclass itself."""
    source = tmp_path / "sample.mol"
    source.write_text("asset", encoding="utf-8")
    asset = ExampleAsset(
        name=source.name,
        path=source,
        rel_path=f"examples/{source.name}",
        size=source.stat().st_size,
        digest="deadbeef",
    )
    workdir = tmp_path / "work"
    workdir.mkdir()
    layout.stage_assets([asset], workdir)
    assert (workdir / source.name).read_text(encoding="utf-8") == "asset"
