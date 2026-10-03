<div align="center">

# <img src="https://raw.githubusercontent.com/ExploreMaths/manim_extensions/main/docs/source/_static/favicon.svg" align="top" width=45> Manim Extensions


**An extension toolkit for [Manim](https://www.manim.community/)** — reusable mobjects, geometric computations, and animations to help you build mathematical videos faster.

<p align="center">
  <img src="https://raw.githubusercontent.com/ExploreMaths/manim_extensions/main/docs/source/_static/cover/magnetic_field.png" width="30%" alt="Magnetic field of a current loop" />
  <img src="https://raw.githubusercontent.com/ExploreMaths/manim_extensions/main/docs/source/_static/cover/multi_pendulum.png" width="30%" alt="Chaotic double pendulum" />
  <img src="https://raw.githubusercontent.com/ExploreMaths/manim_extensions/main/docs/source/_static/cover/rubiks_cube.png" width="30%" alt="Rubik's cube" />
</p>

<p align="center">
  <a href="https://pypi.org/project/manim-extensions/"><img src="https://img.shields.io/pypi/v/manim-extensions?style=flat&logo=python&logoColor=white" alt="PyPI version" /></a>
  <a href="https://pypi.org/project/manim-extensions/"><img src="https://img.shields.io/pypi/pyversions/manim-extensions?style=flat&logo=python&logoColor=white" alt="Python versions" /></a>
  <a href="https://github.com/ExploreMaths/manim_extensions/actions/workflows/python-package.yml"><img src="https://github.com/ExploreMaths/manim_extensions/actions/workflows/python-package.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/ExploreMaths/manim_extensions/actions/workflows/validate.yml"><img src="https://github.com/ExploreMaths/manim_extensions/actions/workflows/validate.yml/badge.svg" alt="Validate" /></a>
  <a href="https://manim-extensions.readthedocs.io/en/latest/"><img src="https://img.shields.io/readthedocs/manim-extensions/latest?style=flat&logo=readthedocs&logoColor=white" alt="Documentation" /></a>
  <a href="https://github.com/ExploreMaths/manim_extensions/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat" alt="MIT License" /></a>
</p>

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
| `manim_extensions.algorithm`  | Algorithm visualisation helpers |
| `manim_extensions.animations` | Animations and easing functions (Basic) |
| `manim_extensions.arabic`     | Arabic text support |
| `manim_extensions.automata`   | Automata visualisation helpers |
| `manim_extensions.chemistry`  | Chemistry visualisation (periodic table, molecules) |
| `manim_extensions.circuit`    | Circuit diagram animations |
| `manim_extensions.compass`    | Compass, ruler, pencil, and construction animations |
| `manim_extensions.data_structures` | Data structure animations |
| `manim_extensions.economics`  | Economics diagrams |
| `manim_extensions.fontawesome`| Font Awesome icon mobjects |
| `manim_extensions.gearbox`    | Involute gears and racks |
| `manim_extensions.geometry`   | Geometric calculation functions (Basic) |
| `manim_extensions.machine_learning` | Machine-learning visualisation |
| `manim_extensions.meshes`     | Mesh and geometry visualisation |
| `manim_extensions.mindmap`    | Mind maps, timelines, catalog diagrams |
| `manim_extensions.mobjects`   | Custom mobjects (Basic) |
| `manim_extensions.physics`    | Physics simulation helpers |
| `manim_extensions.pymunk`     | Pymunk physics engine integration |
| `manim_extensions.qr_codes`   | QR code generation |
| `manim_extensions.rubikscube` | Rubik's Cube animation toolkit |
| `manim_extensions.sequence_diagram` | Sequence diagram animations |
| `manim_extensions.svg_animations` | HTML/SVG animation export |
| `manim_extensions.table`      | Animated tables |
| `manim_extensions.tikz`       | TikZ import helpers |
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
patches are tracked in [VENDORED.md](https://github.com/ExploreMaths/manim_extensions/blob/main/VENDORED.md); patched files carry a
`# patched: <reason>` marker in their header. Licensing and attribution
are kept per-package in [REUSE.toml](https://github.com/ExploreMaths/manim_extensions/blob/main/REUSE.toml).

## License

[MIT](https://github.com/ExploreMaths/manim_extensions/blob/main/LICENSE)
