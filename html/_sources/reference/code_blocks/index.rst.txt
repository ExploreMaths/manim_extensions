.. SPDX-FileCopyrightText: 2024 Casual Coders
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Code Blocks
===========

.. module:: manim_extensions.code_blocks

.. vendored-status:: CasualCodersProjects/manim-code-blocks

**Original author:** `Casual Coders <https://github.com/CasualCodersProjects>`_

**Source repository:** `GitHub <https://github.com/CasualCodersProjects/manim-code-blocks>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-code-blocks-redux`` renders syntax-highlighted source code as an
animated Manim mobject.

The code is bundled inside ``manim_extensions`` as the
:mod:`~manim_extensions.code_blocks` subpackage.  The GitHub language-colour
table is bundled locally, and ``tokenize-all-code`` is only imported when a
programming-language tokenizer is used.

Features
--------

- :class:`~manim_extensions.code_blocks.manim_code_blocks.CodeBlock` with create and
  uncreate animations.
- :class:`~manim_extensions.code_blocks.manim_code_blocks.ProgrammingLanguage` presets
  for C, C++, C#, Fortran, Go, Haskell, Java, JavaScript, Lua, Python, Ruby,
  Rust, SQL, and TypeScript.
- :class:`~manim_extensions.code_blocks.manim_code_blocks.OneDark` and custom themes.
- offline language colours and lazy tokenizer imports.

Usage
-----

Render a Python code block:

.. manim:: CodeBlockDemo
   :ref_classes: CodeBlock

   from manim import *
   from manim_extensions.code_blocks import CodeBlock, Python

   class CodeBlockDemo(Scene):
       def construct(self):
           block = CodeBlock('print("hello")', language=Python).scale(2.0)
           self.play(*block.create())

Classes
-------

.. autoall:: manim_extensions.code_blocks
   :types: class

Constants
---------

.. autoall:: manim_extensions.code_blocks
   :types: data

Modules
-------

.. autosummary::
   :nosignatures:

   ~manim_code_blocks

.. toctree::
   :hidden:
   :maxdepth: 1

   manim_code_blocks
