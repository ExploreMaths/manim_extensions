<div align="center">

# manim_extensions

**An extension toolkit for [Manim](https://www.manim.community/)** — reusable mobjects, geometric computations, and animations to help you build mathematical videos faster.

[![PyPI version](https://img.shields.io/pypi/v/manim-extensions.svg)](https://pypi.org/project/manim-extensions/)
[![Python versions](https://img.shields.io/pypi/pyversions/manim-extensions.svg)](https://pypi.org/project/manim-extensions/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docs](https://readthedocs.org/projects/manim-extensions/badge/?version=latest)](https://manim-extensions.readthedocs.io/en/latest/)

</div>

---

`manim_extensions` extends [Manim](https://www.manim.community/) with:

- **Chinese formula support** — render Chinese characters inside `MathTex` via `xelatex` / `xeCJK`
- **Reusable mobjects** — labelled dots, braces and arrows tied to formulas, file trees, motion trails, shadows, 3D vectors, tree diagrams, and more
- **Geometry helpers** — circle / line / arc intersections and tangent points
- **Common animations** — typewriting, random / reverse writes, highlights, sweep effects, and extra easing functions
- **Bundled toolkits** — involute **gears**, **mind maps** / timelines / catalog diagrams, and **compass-and-straightedge** construction scenes

## Modules

| Package | Description |
|---------|-------------|
| `manim_extensions.mobjects`   | Custom mobjects (Basic) |
| `manim_extensions.geometry`   | Geometric calculation functions (Basic) |
| `manim_extensions.animations` | Animations and easing functions (Basic) |
| `manim_extensions.gearbox`    | Involute gears and racks |
| `manim_extensions.mindmap`    | Mind maps, timelines, catalog diagrams |
| `manim_extensions.compass`    | Compass, ruler, pencil, and construction animations |

## Documentation

Full API reference: **[manim-extensions.readthedocs.io](https://manim-extensions.readthedocs.io/)**

## Installation

```bash
pip install manim_extensions
```

Requires [Manim](https://github.com/ManimCommunity/manim). For the Chinese-formula
features you also need `xelatex` with the `xeCJK` package installed.

## License

[MIT](LICENSE)
