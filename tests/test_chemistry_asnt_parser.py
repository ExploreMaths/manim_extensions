# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the ASNT line munging helpers."""

from pathlib import Path

import pytest

from manim_extensions.chemistry.utils.parsers.asnt_parser import ASNTParser


def test_read_file_returns_lines(tmp_path: Path):
    path = tmp_path / "minimal.asnt"
    path.write_text("first\nsecond\n", encoding="utf-8")

    assert ASNTParser.read_file(path) == ["first\n", "second\n"]


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("{", "{"),
        ("}", "}"),
        ("},", "},"),
        ("{ 1, 2, }", "[ 1, 2, ]"),
        ("element", '"element"'),
        ("C,", '"C",'),
        ("foo {", '"foo": {'),
        ("1,", '"1",'),
    ],
)
def test_replace_stuff_line_shapes(raw, expected):
    assert ASNTParser.replace_stuff(raw) == expected


def test_replace_stuff_restores_quote_characters():
    line = '"atom_site" "C",'

    result = ASNTParser.replace_stuff(line)

    assert "'atom_site'" in result
    assert "'C'" in result
