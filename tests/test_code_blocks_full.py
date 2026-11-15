# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Broad coverage for the vendored ``manim-code-blocks-redux`` renderer."""

from types import SimpleNamespace

from manim_extensions.code_blocks import (
    C,
    Cpp,
    CSharp,
    CodeBlock,
    Fortran,
    Go,
    Haskell,
    Java,
    JavaScript,
    Lua,
    OneDark,
    ProgrammingLanguage,
    Python,
    Ruby,
    Rust,
    SQL,
    Theme,
    TypeScript,
)
from manim_extensions.code_blocks.manim_code_blocks import language_colors

PRESETS = (
    C,
    Cpp,
    CSharp,
    Fortran,
    Go,
    Haskell,
    Java,
    JavaScript,
    Lua,
    Python,
    Ruby,
    Rust,
    SQL,
    TypeScript,
)


def test_theme_color_for_hit_and_fallback():
    theme = Theme(
        colors={"#123456": ["keyword"], "#ABCDEF": [lambda token: True]},
        group_matchers=["#123456"],
    )
    assert theme.color_for(SimpleNamespace(type="keyword")) == "#123456"
    assert theme.color_for(SimpleNamespace(type="unknown")) == "#FFFFFF"


def test_language_presets_metadata():
    assert len(language_colors) == 14
    for language in PRESETS:
        assert language.name in language_colors
        assert language.color == language_colors[language.name]["color"]
    assert Cpp._tokenize_name == "Cpp"
    assert CSharp._tokenize_name == "CSharp"
    assert Python._tokenize_name == "Python"
    assert Python.language is not None
    assert Python.language.tokenize("x = 1")


def test_unknown_language_color_and_tokenizer_warn(capsys):
    unknown = ProgrammingLanguage("Brainfuck")
    assert unknown.color == "#FFFFFF"
    assert "no color found for Brainfuck" in capsys.readouterr().out
    assert unknown.language is None
    assert "no tokenization found for Brainfuck" in capsys.readouterr().out
    named = ProgrammingLanguage("Custom", tokenize_name="Python")
    assert named._tokenize_name == "Python"
    assert named.language is not None


def test_code_block_with_language_covers_all_token_branches():
    code = 'def f(a):\n    return "x" & <tag>  # comment\nx = [1, 2]\n'
    block = CodeBlock(code, language=Python)
    assert block.title is not None
    assert block.title_background is not None
    assert block.code is not None
    assert block.code_background is not None
    assert len(block) == 4
    create = block.create()
    assert len(create) == 4
    uncreate = block.uncreate()
    assert len(uncreate) == 4


def test_code_block_without_language_and_theme_override():
    block = CodeBlock(
        "plain text & more", language=None, theme=OneDark, font="consolas"
    )
    assert block.title is None
    assert block.title_background is None
    assert len(block) == 2
    assert len(block.create()) == 2
    assert len(block.uncreate()) == 2


def test_code_block_respects_group_counter_wraparound():
    # nested brackets drive the group counter past the matcher list length
    code = "((((x))))"
    tokens = ProgrammingLanguage("Custom", tokenize_name="Python")
    block = CodeBlock(code, language=tokens)
    assert block.code is not None
