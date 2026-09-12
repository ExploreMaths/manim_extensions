<div align="center">

# <img src="docs/source/_static/favicon.svg" align="top" width=45> Manim Extensions


**An extension toolkit for [Manim](https://www.manim.community/)** — reusable mobjects, geometric computations, and animations to help you build mathematical videos faster.

<p align="center">
  <img src="docs/source/_static/gifs/sequence_diagram.gif" width="30%" alt="Sequence diagram animation" />
  <img src="docs/source/_static/gifs/compass.gif" width="30%" alt="Compass construction animation" />
  <img src="docs/source/_static/gifs/more_animations.gif" width="30%" alt="Animation helpers demo" />
</p>

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
      <a href="https://github.com/ExploreMaths/manim_extensions/actions/workflows/docs-media.yml"><img src="https://github.com/ExploreMaths/manim_extensions/actions/workflows/docs-media.yml/badge.svg"></a>
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
| `manim_extensions.physics`    | Physics simulation helpers |
| `manim_extensions.rubikscube` | Rubik's Cube animation toolkit |
| `manim_extensions.sequence_diagram` | Sequence diagram animations |
| `manim_extensions.tikz`       | TikZ import helpers |
| `manim_extensions.arabic`     | Arabic text support |
| `manim_extensions.chemistry`  | Chemistry visualisation (periodic table, molecules) |
| `manim_extensions.economics`  | Economics diagrams |
| `manim_extensions.fontawesome`| Font Awesome icon mobjects |
| `manim_extensions.machine_learning` | Machine-learning visualisation |
| `manim_extensions.pymunk`     | Pymunk physics engine integration |
| `manim_extensions.qr_codes`   | QR code generation |
| `manim_extensions.svg_animations` | HTML/SVG animation export |
| `manim_extensions.table`      | Animated tables |
| `manim_extensions.weighted_line` | Weighted line graphs |

## Bundled plugins

The following third-party Manim plugins are bundled directly as subpackages
inside `manim_extensions`:

- `manim-algorithm` → `manim_extensions.algorithm`
- `manim-arabic` → `manim_extensions.arabic`
- `manim-automata` → `manim_extensions.automata`
- `manim-Chemistry` → `manim_extensions.chemistry`
- `manim-circuit` → `manim_extensions.circuit`
- `manim-data-structures` → `manim_extensions.data_structures`
- `manim_ec` → `manim_extensions.economics`
- `manim-fontawesome` → `manim_extensions.fontawesome`
- `manim-gearbox` → `manim_extensions.gearbox`
- `manim-meshes` → `manim_extensions.meshes`
- `manim-ml` (ManimML) → `manim_extensions.machine_learning`
- `manim-mindmap` → `manim_extensions.mindmap`
- `manim-physics` → `manim_extensions.physics`
- `manim-pymunk` → `manim_extensions.pymunk`
- `manim-qr-codes` → `manim_extensions.qr_codes`
- `manim-rubikscube` → `manim_extensions.rubikscube`
- `manim-sequence-diagram` → `manim_extensions.sequence_diagram`
- `manim-svg-animations` → `manim_extensions.svg_animations`
- `manim-table` → `manim_extensions.table`
- `manim-tikz` → `manim_extensions.tikz`
- `manim-weighted-line` → `manim_extensions.weighted_line`

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

Requires [Manim](https://github.com/ManimCommunity/manim) Community Edition
(>=0.21). For the Chinese-formula features you also need `xelatex` with the
`xeCJK` package installed.

### Optional extras

Each bundled module only pulls in what it needs. The base install is
just `manim` + `numpy`; heavy or niche dependencies are lazy-imported
and belong to the matching extra:

```bash
pip install manim_extensions[all]         # every module at once
pip install manim_extensions[automata]    # xmltodict
pip install manim_extensions[chemistry]   # pandas, xmltodict, requests
pip install manim_extensions[dev]         # pytest for running tests
pip install manim_extensions[docs]        # sphinx + furo for building docs
pip install manim_extensions[meshes]      # trimesh, moderngl
pip install manim_extensions[ml]          # matplotlib, scikit-learn, seaborn, tqdm
pip install manim_extensions[physics]     # pymunk, shapely
pip install manim_extensions[qr]          # segno
pip install manim_extensions[rubikscube]  # kociemba
pip install manim_extensions[svg]         # svgpathtools
pip install manim_extensions[video]       # opencv (VideoMobject)
```

If a feature is used without its extra installed, the error message names
the exact `pip install manim_extensions[...]` command.

Every vendored module has a same-named extra. The ones below declare no
additional dependencies (they work with the base install) but exist so
that installs can uniformly request `manim_extensions[<module>]`:
`algorithm`, `arabic`, `circuit`, `compass`, `data_structures`,
`economics`, `fontawesome`, `gearbox`, `mindmap`, `sequence_diagram`,
`table`, `tikz`, `weighted_line`.

### Why we bundle upstream packages

Most of `manim_extensions` is **vendored**: source copied from small,
independent upstream Manim extension projects and maintained here as one
coherent, tested whole. The motivations:

- **Upstream metadata locks.** Some upstream packages declare dependency
  ranges that conflict with reality. For example
  `manim-nerdfont-icons` 1.0.x pins `manim>=0.19,<0.20` on PyPI even
  though it works with current manim — it is bundled as
  `manim_extensions.utils.nerdfont` instead of being a dependency.
  `manim-mobject-svg` similarly declares `python<3.13`; it stays a
  lazily-imported plugin for that reason.
- **Integration.** Vendoring lets us normalise import style, docstring
  conventions and CI checks across all modules, fix cross-module bugs in
  one place, and keep every public name importable from a single package.
- **Longevity.** Several upstream projects are inactive; vendoring
  decouples this package from their release cadence.
- **Lean installs.** Because each module's extra dependencies are
  lazy-imported, the base install stays at two packages while every
  feature remains a `pip install manim_extensions[...]` away.

Every vendored package's upstream repository, sync version and local
patches are tracked in [VENDORED.md](VENDORED.md); patched files carry a
`# patched: <reason>` marker in their header. Licensing and attribution
are kept per-package in [REUSE.toml](REUSE.toml).

## License

[MIT](LICENSE)
