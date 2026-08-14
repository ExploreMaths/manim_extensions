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
- **Third-party integrations** — selected Manim plugin repositories tracked as Git submodules and exposed through `manim_extensions` namespace shims

## Modules

| Package | Description |
|---------|-------------|
| `manim_extensions.mobjects`   | Custom mobjects (Basic) |
| `manim_extensions.geometry`   | Geometric calculation functions (Basic) |
| `manim_extensions.animations` | Animations and easing functions (Basic) |
| `manim_extensions.gearbox`    | Involute gears and racks |
| `manim_extensions.mindmap`    | Mind maps, timelines, catalog diagrams |
| `manim_extensions.compass`    | Compass, ruler, pencil, and construction animations |
| `manim_extensions.algorithm`  | Third-party algorithm visualisation helpers |
| `manim_extensions.automata`   | Third-party automata visualisation helpers |
| `manim_extensions.circuit`    | Third-party circuit diagram animations |
| `manim_extensions.data_structures` | Third-party data structure animations |
| `manim_extensions.meshes`     | Third-party mesh and geometry visualisation |
| `manim_extensions.neural_network` | Third-party neural-network visualisation |
| `manim_extensions.physics`    | Third-party physics simulation helpers |
| `manim_extensions.rubikscube` | Third-party Rubik's Cube animation toolkit |
| `manim_extensions.sequence_diagram` | Third-party sequence diagram animations |
| `manim_extensions.tikz`       | Third-party TikZ import helpers |

## Third-party submodules

The project maintains the following third-party plugin repositories as Git submodules under `third_party/`:

- `manim-algorithm`
- `manim-automata`
- `manim-circuit`
- `manim-data-structures`
- `manim-meshes`
- `manim-neural-network`
- `manim-physics`
- `manim-rubikscube`
- `manim-sequence-diagram`
- `manim-tikz`

Each one is exposed as a light import shim under the `manim_extensions` package, while the original implementation remains in the corresponding submodule directory for source provenance and updates.

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