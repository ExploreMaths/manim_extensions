<div align="center">

# <img src="docs/source/_static/favicon.svg" align="top" width=45> Manim Extensions


**An extension toolkit for [Manim](https://www.manim.community/)** — reusable mobjects, geometric computations, and animations to help you build mathematical videos faster.

<table>
  <tr>
    <td><strong>📦 Package</strong></td>
    <td>
      <a href="https://pypi.org/project/manim-extensions/"><img src="https://img.shields.io/pypi/v/manim-extensions?style=flat&logo=python&logoColor=white" /></a>
      <a href="https://pypi.org/project/manim-extensions/"><img src="https://img.shields.io/pypi/status/manim-extensions?style=flat&logo=python&logoColor=white" alt="PyPI Status"></a>
      <a href="https://pypi.org/project/manim-extensions/"><img src="https://img.shields.io/pypi/pyversions/manim-extensions?style=social&color=CB4040&logo=python" /></a>
      <a href="https://pypi.org/project/manim-extensions/#files"><img src="https://img.shields.io/pypi/wheel/manim-extensions?style=flat&logo=python&logoColor=white" alt="PyPI Wheel"></a>
      <br>
      <a href="https://pypi.org/project/manim_extensions/"><img src="https://img.shields.io/pypi/dm/manim_extensions?style=social&logo=python" /></a>
      <a href="https://pypi.org/project/manim-extensions/"><img src="https://img.shields.io/pypi/implementation/manim-extensions?style=social&logo=python" alt="Python Implementation"></a>
    </td>
  </tr>

  <tr>
    <td><strong>🚀 Repository</strong></td>
    <td>
      <a href="https://github.com/ExploreMaths/manim_extensions/releases/latest"><img src="https://img.shields.io/github/v/release/ExploreMaths/manim_extensions?style=flat&color=%2333fb950&logo=github&label=stable" /></a>
      <a href="https://github.com/ExploreMaths/manim_extensions/releases/"><img src="https://img.shields.io/github/v/release/ExploreMaths/manim_extensions?include_prereleases&style=flat&color=%23ea7233&logo=github&label=latest" /></a>
      <a href="https://github.com/ExploreMaths/manim_extensions"><img src="https://img.shields.io/github/repo-size/ExploreMaths/manim_extensions?style=social&logo=github" /></a>
      <br>
      <a href="https://github.com/ExploreMaths/manim_extensions/commits/main"><img src="https://img.shields.io/github/last-commit/ExploreMaths/manim_extensions?style=flat&logo=git&logoColor=white" alt="Last Commit"></a>
      <a href="https://github.com/ExploreMaths/manim_extensions/graphs/commit-activity"><img src="https://img.shields.io/github/commit-activity/m/ExploreMaths/manim_extensions?style=social&logo=git" alt="Monthly Commit Activity"></a>
    </td>
  </tr>

  <tr>
    <td><strong>✅ CI & Docs</strong></td>
    <td>
      <a href="https://github.com/ExploreMaths/manim_extensions/actions/workflows/python-package.yml"><img src="https://github.com/ExploreMaths/manim_extensions/actions/workflows/python-package.yml/badge.svg" /></a>
      <a href="https://github.com/ExploreMaths/manim_extensions/actions/workflows/validate.yml"><img src="https://github.com/ExploreMaths/manim_extensions/actions/workflows/validate.yml/badge.svg" /></a>
      <br>
      <a href="https://manim-extensions.readthedocs.io/en/latest/"><img src="https://img.shields.io/readthedocs/manim-extensions/latest?style=flat&logo=readthedocs&logoColor=white" /></a>
    </td>
  </tr>
</table>

</div>

---

`manim_extensions` extends [Manim](https://www.manim.community/) with:

- **Chinese formula support** — render Chinese characters inside `MathTex` via `xelatex` / `xeCJK`
- **Reusable mobjects** — labelled dots, braces and arrows tied to formulas, file trees, motion trails, shadows, 3D vectors, tree diagrams, and more
- **Geometry helpers** — circle / line / arc intersections and tangent points
- **Common animations** — typewriting, random / reverse writes, highlights, sweep effects, and extra easing functions
- **Bundled toolkits** — involute gears, mind maps / timelines / catalog diagrams, compass-and-straightedge constructions, algorithm visualisation, automata, circuits, data structures, meshes, neural networks, physics, Rubik's cube, sequence diagrams, and TikZ integration

## Modules

| Package | Description |
|---------|-------------|
| `manim_extensions.mobjects`   | Custom mobjects (Basic) |
| `manim_extensions.geometry`   | Geometric calculation functions (Basic) |
| `manim_extensions.animations` | Animations and easing functions (Basic) |
| `manim_extensions.gearbox`    | Involute gears and racks |
| `manim_extensions.mindmap`    | Mind maps, timelines, catalog diagrams |
| `manim_extensions.compass`    | Compass, ruler, pencil, and construction animations |
| `manim_extensions.algorithm`  | Algorithm visualisation helpers |
| `manim_extensions.automata`   | Automata visualisation helpers |
| `manim_extensions.circuit`    | Circuit diagram animations |
| `manim_extensions.data_structures` | Data structure animations |
| `manim_extensions.meshes`     | Mesh and geometry visualisation |
| `manim_extensions.neural_network` | Neural-network visualisation |
| `manim_extensions.physics`    | Physics simulation helpers |
| `manim_extensions.rubikscube` | Rubik's Cube animation toolkit |
| `manim_extensions.sequence_diagram` | Sequence diagram animations |
| `manim_extensions.tikz`       | TikZ import helpers |

## Bundled plugins

The following third-party Manim plugins are bundled directly as subpackages
inside `manim_extensions`:

- `manim-algorithm` → `manim_extensions.algorithm`
- `manim-automata` → `manim_extensions.automata`
- `manim-circuit` → `manim_extensions.circuit`
- `manim-data-structures` → `manim_extensions.data_structures`
- `manim-meshes` → `manim_extensions.meshes`
- `manim-neural-network` → `manim_extensions.neural_network`
- `manim-physics` → `manim_extensions.physics`
- `manim-rubikscube` → `manim_extensions.rubikscube`
- `manim-sequence-diagram` → `manim_extensions.sequence_diagram`
- `manim-tikz` → `manim_extensions.tikz`

Installing `manim_extensions` lets you import them directly from the package
namespace and guarantees compatible versions. See the
[documentation](https://manim-extensions.readthedocs.io/) for details and
attribution to the original authors.

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
