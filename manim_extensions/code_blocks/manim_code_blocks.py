# SPDX-FileCopyrightText: 2024 Casual Coders
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Utilities for the manim_code_blocks module."""

from __future__ import annotations
from collections.abc import Callable, Sequence
from typing import Any, Protocol, cast

# patched: bundled GitHub language colours locally, removed the import-time
# patched: network request, and made tokenize-all-code a lazy optional extra

# unlinked-class-ok: CodeBlock


"""A syntax-highlighted code block for Manim.

The upstream module fetched GitHub's language colour table over the network
while being imported.  The colour table is now bundled for the languages this
package exposes, and ``tokenize-all-code`` is imported only when a
programming-language tokenizer is actually used.
"""


import re as regex
from abc import ABC as abstract

from manim import (
    Animation,
    AddTextLetterByLetter,
    BackgroundRectangle,
    DOWN,
    FadeIn,
    FadeOut,
    GRAY_C,
    LEFT,
    MarkupText,
    UP,
    Uncreate,
    VGroup,
    Text,
    VMobject,
)
import numpy as np

from ..utils.deps import require


class Theme:
    """A theme used to syntax highlight a :class:`~manim_extensions.code_blocks.manim_code_blocks.CodeBlock`.

    Parameters
    ----------
    colors
        Mapping from hex colours to the token types drawn in that colour.
    group_matchers
        Colours cycled through for matched bracket groups.

    Examples
    --------
    .. manim:: ThemeOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.code_blocks.manim_code_blocks import Theme

       ThemeTarget = Theme

       class ThemeOverview(Scene):
           def construct(self):
               public = [n for n in dir(ThemeTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('Theme', font_size=36),
                   Text('module: manim_extensions.code_blocks.manim_code_blocks', font_size=18, color=GREY),
                   Text('A theme used to syntax highlight a manim_extensions.code_blocks.manim_code_blocks.CodeBlock', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.code_blocks.manim_code_blocks import Theme

        theme = Theme(colors={"#ff0000": ["keyword"]}, group_matchers=["#00ff00"])
    """

    colors: dict[str, list[str | Callable[[TokenLike], bool]]]
    """
    The colors of this theme represented as a dictionary. The keys of the dictionary are hexidecimal colors (such as `"#FFFFFF"`), and the values are lists of token types that should be colored with that color (such as `["keyword", "operation"]`).
    """

    group_matchers: list[str]

    def __init__(
        self,
        colors: dict[str, list[str | Callable[[TokenLike], bool]]],
        group_matchers: list[str],
    ) -> None:
        self.colors = colors
        self.group_matchers = group_matchers

    def color_for(self, token: TokenLike) -> str:
        """Return the theme colour assigned to a token.

        Parameters
        ----------
        token
            The token whose type selects the colour.

        Returns
        -------
            The matching hex colour, or white when no rule matches.
        """
        for key, value in self.colors.items():
            if token.type in value:
                return key
        return "#FFFFFF"


#: The 'One Dark' theme from the `Atom` text editor.
OneDark = Theme(
    colors={
        "#C678DD": ["keyword", "directive"],  # Purple
        "#61AFEF": ["function"],  # Blue
        "#E06C75": ["identifier"],  # Red
        "#98C379": ["string"],  # Green
        "#56B6C2": ["symbol"],  # Cyan
        "#D19A66": ["number", "keyword literal"],  # Orange
        "#E5C07B": ["class name"],  # Yellow
        str(GRAY_C): ["comment"],  # Gray
    },
    group_matchers=["#D19A66", "#C678DD", "#56B6C2"],  # Orange  # Purple  # Cyan
)


#: GitHub language colours bundled for the languages exposed by this module.
#:
#: The upstream module downloaded this table from ``ozh/github-colors`` on
#: import.  Only the fourteen languages constructed below are included here, so the
#: module works offline and does not need to parse a network response.
language_colors = {
    "C": {"color": "#555555"},
    "C++": {"color": "#f34b7d"},
    "C#": {"color": "#178600"},
    "Fortran": {"color": "#4d41b1"},
    "Go": {"color": "#00ADD8"},
    "Haskell": {"color": "#5e5086"},
    "Java": {"color": "#b07219"},
    "JavaScript": {"color": "#f1e05a"},
    "Lua": {"color": "#000080"},
    "Python": {"color": "#3572A5"},
    "Ruby": {"color": "#701516"},
    "Rust": {"color": "#dea584"},
    "SQL": {"color": "#e38c00"},
    "TypeScript": {"color": "#3178c6"},
}


class TokenLike(Protocol):
    """A tokenizer token with a type name."""

    type: str
    value: str


class TokenizerLike(Protocol):
    """A tokenizer that splits one line into tokens."""

    def tokenize(self, line: str) -> Sequence[TokenLike]: ...


class ProgrammingLanguage(abstract):
    """A programming language used to render `CodeBlocks`.

    Parameters
    ----------
    name
        Display name of the language.
    tokenize_name
        Tokenizer attribute name; defaults to ``name``.

    Examples
    --------
    .. manim:: ProgrammingLanguageOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.code_blocks.manim_code_blocks import ProgrammingLanguage

       ProgrammingLanguageTarget = ProgrammingLanguage

       class ProgrammingLanguageOverview(Scene):
           def construct(self):
               public = [n for n in dir(ProgrammingLanguageTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('ProgrammingLanguage', font_size=36),
                   Text('module: manim_extensions.code_blocks.manim_code_blocks', font_size=18, color=GREY),
                   Text('A programming language used to render CodeBlocks', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.code_blocks.manim_code_blocks import ProgrammingLanguage

        class Python(ProgrammingLanguage):
            name = "Python"
            color = "#3572A5"
    """

    name: str
    """The name of the programming language. The name is displayed on the title card above the code block."""

    color: str
    """
    The color of the programming language. The color is used when displaying the name in the title card above the code block. by default, the official GitHub language colors are used for supported languages, see https://github.com/ozh/github-colors/blob/master/colors.json.
    """

    def __init__(self, name: str, tokenize_name: str | None = None) -> None:
        self.name = name
        self._tokenize_name = tokenize_name if tokenize_name else name
        self.color = language_colors.get(name, {}).get("color", "#FFFFFF")

        if self.color == "#FFFFFF":
            print(f"Warning: no color found for {name}")

    @property
    def language(self) -> TokenizerLike | None:
        """Return the tokenizer for this language.

        Returns
        -------
            The tokenizer object, importing ``tokenize-all-code`` on first use.
        """
        tokenize_all = require("code_blocks", "tokenize_all")
        language = getattr(tokenize_all, self._tokenize_name, None)
        if language is None:
            print(f"Warning: no tokenization found for {self.name}")
        return cast("TokenizerLike | None", language)


class CodeBlock(VGroup):
    """A block of code. By default code blocks are rendered as :class:`~manim.mobject.text.text_mobject.MarkupText` objects with `BackgroundRectangles` behind them. Furthermore, a title with the name and color of the language is rendered above the code block on the left-hand side. Syntax highlighting is done using `TextMates` by extracting `.tmLanguage.json` files from `microsoft/vscode`. See https://github.com/microsoft/vscode/tree/main/extensions.

    .. doc-example-covers: create, uncreate

    Parameters
    ----------
    text
        The source code shown in the block.
    language
        Language used for syntax highlighting.
    theme
        Colour theme applied to the tokens.
    font
        Font family used for the code.
    **kwargs
        Keyword arguments forwarded to the markup text.

    Examples
    --------
    .. manim:: CodeBlockScene
       :save_last_frame:

       from manim import *
       from manim import Scene
       from manim_extensions.code_blocks import CodeBlock

       class CodeBlockScene(Scene):
           def construct(self):
               block = CodeBlock('print("Hello World!")')
               block.scale(2.5)
               self.add(block)
    """

    code: MarkupText
    """The primary :class:`~manim.mobject.text.text_mobject.MarkupText` object that makes up the code block. Equivalent to indexing at `[1]`."""

    title: MarkupText | None
    """
    The title :class:`~manim.mobject.text.text_mobject.MarkupText` object that makes up the langauge name title at the top of the code block. Equivalent to indexing at `[3]`.
    """

    code_background: BackgroundRectangle
    """The :class:`~manim.mobject.geometry.shape_matchers.BackgroundRectangle` for the code block markup object. Equivalent to indexing at `[0]`."""

    title_background: BackgroundRectangle | None
    """
    The :class:`~manim.mobject.geometry.shape_matchers.BackgroundRectangle` for the `title` object that lists the language name above the code block. Equivalent to indexing at `[2]`.
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        text: str,
        language: ProgrammingLanguage | None = None,
        theme: Theme = OneDark,
        font: str = "consolas",
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:

        if language:
            lines = text.split("\n")
            tokenizer = language.language
            assert tokenizer is not None
            group_count = 0
            finished: list[str] = []
            for line in lines:
                tokens = tokenizer.tokenize(line)
                for token in tokens:
                    if token.type.startswith("left"):
                        finished.append(
                            '<span foreground="'
                            + theme.group_matchers[
                                group_count % len(theme.group_matchers)
                            ]
                            + '">'
                            + token.value
                            + "</span>"
                        )
                        group_count += 1
                    elif token.type.startswith("right"):
                        group_count -= 1
                        finished.append(
                            '<span foreground="'
                            + theme.group_matchers[
                                group_count % len(theme.group_matchers)
                            ]
                            + '">'
                            + token.value
                            + "</span>"
                        )
                    elif token.type == "whitespace":
                        finished.append(token.value)
                    else:
                        safe_value = regex.sub("&", "&amp;", token.value)
                        safe_value = regex.sub("<", "&lt;", safe_value)
                        safe_value = regex.sub(">", "&gt;", safe_value)
                        finished.append(
                            '<span foreground="'
                            + theme.color_for(token=token)
                            + '">'
                            + safe_value
                            + "</span>"
                        )
                finished.append("\r")

            finished_text = "".join(finished)
        else:
            safe_text = regex.sub("&", "&amp;", text)
            safe_text = regex.sub("<", "&lt;", safe_text)
            safe_text = regex.sub(">", "&gt;", safe_text)
            finished_text = '<span foreground="#FFFFFF">' + safe_text + "</span>"

        markup = MarkupText(
            f'<span font="{font}">' + finished_text + "</span>", z_index=3
        ).scale(0.4)
        background_rect = BackgroundRectangle(
            markup, color="#282C34", buff=0.2, fill_opacity=1
        )

        if language:
            lang_name = (
                MarkupText(f'<span font="{font}">{language.name}</span>', z_index=3)
                .next_to(background_rect, UP)
                .set_color(language.color)
            )
            lang_name.scale(0.3, about_point=lang_name.get_corner(DOWN + LEFT))

            lang_background = BackgroundRectangle(
                lang_name, color="#282C34", buff=0.15, fill_opacity=1
            )
            pos = background_rect.get_corner(UP + LEFT) + np.array(
                [lang_background.width / 2, lang_background.height / 2 - 0.005, 0]
            )

            VGroup(lang_name, lang_background).move_to(pos)

            self.title = lang_name
            self.title_background = lang_background

            super().__init__(
                background_rect, markup, lang_background, lang_name, **kwargs
            )
        else:
            self.title = None
            self.title_background = None
            super().__init__(background_rect, markup, **kwargs)

        self.code = markup
        self.code_background = background_rect

    def create(
        self, **kwargs: Any
    ) -> tuple[
        Animation, ...
    ]:  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
        """Return a tuple of animations for creating the code block.

        Use the returned animations with :meth:`~manim.scene.scene.Scene.play`:

        .. code-block:: python

            python = CodeBlock('print("Hello World!")', language=Python)
            self.play(*python.create())

        By default the animation fades in the background and title background, and
        writes the code and title letter by letter.

        Parameters
        ----------
        **kwargs
            Keyword arguments forwarded to each animation.

        Returns
        -------
            A tuple of animations that create the block, including the title
            animations when a title is present.
        """
        title = self.title
        title_background = self.title_background
        if title is not None and title_background is not None:
            return (
                FadeIn(self.code_background, **kwargs),
                AddTextLetterByLetter(cast(Text, self.code), **kwargs),
                FadeIn(title_background, **kwargs),
                AddTextLetterByLetter(cast(Text, title), **kwargs),
            )

        return (
            FadeIn(self.code_background, **kwargs),
            AddTextLetterByLetter(cast(Text, self.code), **kwargs),
        )

    def uncreate(
        self, **kwargs: Any
    ) -> tuple[
        Animation, ...
    ]:  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
        """Return a tuple of animations for uncreating the code block. Use such as:
                ```
                python = CodeBlock('print("Hello World!")', language = Python)
                self.play(*python.uncreate())
                ```
                By default the animation will :class:`~manim.animation.fading.FadeOut` the `background` and `title_background`, and :class:`~manim.animation.creation.Uncreate` the `code` and `title`.

        Parameters
        ----------
        **kwargs
            Keyword arguments forwarded to each animation.

        Returns
        -------
            A tuple of animations that remove the block, including the title
            animations when a title is present.
        """
        title = self.title
        title_background = self.title_background
        if title is not None and title_background is not None:
            return (
                FadeOut(self.code_background, **kwargs),
                Uncreate(cast(VMobject, self.code), **kwargs),
                FadeOut(title_background, **kwargs),
                Uncreate(cast(VMobject, self.title), **kwargs),
            )

        return (
            FadeOut(self.code_background, **kwargs),
            Uncreate(cast(VMobject, self.code), **kwargs),
        )


#: The C programming language, used to render C code in code blocks.
C = ProgrammingLanguage("C")

#: The `C++` programming language, used to render `C++` code in `CodeBlocks`.
Cpp = ProgrammingLanguage("C++", tokenize_name="Cpp")

#: The `C#` programming language, used to render `C#` code in `CodeBlocks`.
CSharp = ProgrammingLanguage("C#", tokenize_name="CSharp")

#: The `Fortran` programming language, used to render Fortran code in `CodeBlocks`.
Fortran = ProgrammingLanguage("Fortran")

#: The `Go` programming language, used to render `Go` code in `CodeBlocks`.
Go = ProgrammingLanguage("Go")

#: The `Haskell` programming language, used to render `Haskell` code in `CodeBlocks`.
Haskell = ProgrammingLanguage("Haskell")

#: The `Java` programming language, used to render `Java` code in `CodeBlocks`.
Java = ProgrammingLanguage("Java")

#: The `JavaScript` programming language, used to render `JavaScript` code in `CodeBlocks`.
JavaScript = ProgrammingLanguage("JavaScript")

#: The `Lua` programming language, used to render `Lua` code in `CodeBlocks`.
Lua = ProgrammingLanguage("Lua")

#: The `Python` programming language, used to render `Python` code in `CodeBlocks`.
Python = ProgrammingLanguage("Python")

#: The `Ruby` programming language, used to render `Ruby` code in `CodeBlocks`.
Ruby = ProgrammingLanguage("Ruby")

#: The `Rust` programming language, used to render `Rust` code in `CodeBlocks`.
Rust = ProgrammingLanguage("Rust")

#: The `SQL` programming language, used to render `SQL` code in `CodeBlocks`.
SQL = ProgrammingLanguage("SQL")

#: The `TypeScript` programming language, used to render `TypeScript` code in `CodeBlocks`.
TypeScript = ProgrammingLanguage("TypeScript")
