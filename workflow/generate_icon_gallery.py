# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Generate the Nerd Font Icon Gallery body from SYMBOLS_UNICODE.

Writes docs/source/reference/nerdfont/_icon_gallery_body.html, a fragment
consumed by icon_gallery.rst via ``.. raw:: html :file:``.

Each icon becomes a grid card: the glyph (Nerd Font Symbols), its name and
its U+ codepoint. Cards carry data-name / data-codepoint attributes for the
search filter in _static/icon_gallery.js.
"""

from __future__ import annotations

import html
from pathlib import Path

from manim_extensions.nerdfont.icons_dict import SYMBOLS_UNICODE

OUT = (
    Path(__file__).resolve().parent.parent
    / "docs/source/reference/nerdfont/_icon_gallery_body.html"
)


def card(name: str, codepoint: int) -> str:
    glyph = chr(codepoint)
    return (
        '<div class="ig-card" data-name="{name}" data-codepoint="{cp}" '
        'title="{name}">'
        '<span class="ig-glyph" aria-hidden="true">{glyph}</span>'
        '<span class="ig-name">{name}</span>'
        '<span class="ig-cp">U+{cp:04X}</span>'
        "</div>"
    ).format(
        name=html.escape(name, quote=True),
        cp=codepoint,
        glyph=html.escape(glyph),
    )


LICENSE = "MIT"
# Split the tag name so reuse does not read the f-string template below as
# an SPDX expression; the generated HTML still carries the full tags.
SPDX_KEY = "SPDX-License-" + "Identifier"


def main() -> None:
    items = sorted(SYMBOLS_UNICODE.items(), key=lambda kv: kv[1])
    body = "\n".join(card(name, cp) for name, cp in items)
    fragment = (
        "<!-- SPDX-FileCopyrightText: 2026 ExploreMaths -->\n"
        f"<!-- {SPDX_KEY}: {LICENSE} -->\n"
        '<div class="ig-toolbar">'
        '<input id="ig-search" class="ig-search" type="search" '
        'placeholder="Search icons\u2026" autocomplete="off" spellcheck="false">'
        '<span id="ig-count" class="ig-count" aria-live="polite"></span>'
        "</div>\n"
        f'<div id="ig-grid" class="ig-grid" data-total="{len(items)}">\n{body}\n</div>'
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(fragment, encoding="utf-8")
    print(f"wrote {OUT} ({len(items)} icons, {OUT.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
