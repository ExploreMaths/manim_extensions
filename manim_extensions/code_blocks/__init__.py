# SPDX-FileCopyrightText: 2024 Casual Coders
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: package entry point for the vendored single-module distribution

""":class:`~manim_extensions.code_blocks.manim_code_blocks.CodeBlock` rendering.

This package bundles the ``manim-code-blocks-redux`` module so that code
blocks can be rendered directly inside a Manim scene.

"""

from .manim_code_blocks import (
    C,
    CSharp,
    CodeBlock,
    Cpp,
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
    language_colors,
)

__all__ = [
    "C",
    "CSharp",
    "CodeBlock",
    "Cpp",
    "Fortran",
    "Go",
    "Haskell",
    "Java",
    "JavaScript",
    "Lua",
    "OneDark",
    "ProgrammingLanguage",
    "Python",
    "Ruby",
    "Rust",
    "SQL",
    "Theme",
    "TypeScript",
    "language_colors",
]
