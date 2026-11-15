<!-- SPDX-FileCopyrightText: 2026 ExploreMaths
SPDX-License-Identifier: MIT

Vendored packages

manim_extensions aggregates a number of small upstream Manim extension
projects. This file records, for each vendored package, where it came
from, which upstream version it was synced at, and which local patches
deviate from upstream. Patches are also marked in the patched files
themselves with a `# patched: <reason>` line in the file header.

Version history note: sync points marked with a commit hash were
derived heuristically on 2026-09-25 by comparing the local code
against the upstream GitHub history (AST-normalized content match;
where several upstream commits share identical content, the oldest
one is recorded). On 2026-10-25 all vendored packages that were behind
upstream were re-synced to the latest upstream commit, so the recorded
sync points for those packages now exactly match their upstream HEAD. -->


## `manim_extensions/algorithm`
  - **Upstream:** [sinianluoye/manim-algorithm](https://github.com/sinianluoye/manim-algorithm)
  - **Synced:** [`5d69236739e80facf3a98540a58785e901784a77`](https://github.com/sinianluoye/manim-algorithm/commit/5d69236739e80facf3a98540a58785e901784a77)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/animations.py`, `manim_extensions/mobjects.py`
  - **Upstream:** [manim-kindergarten](https://github.com/manim-kindergarten) (manim_sandbox helpers)
  - **Synced:** not recorded
  - **Status:** not recorded
  - **Local patches:**
    - `mobjects.py` lazy-imports cv2 (`video` extra)
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/arabic`
  - **Upstream:** [razekmh/manim-arabic](https://github.com/razekmh/manim-arabic)
  - **Synced:** [`b30eb9cc44cfe1fe4771421c96a71033d712e416`](https://github.com/razekmh/manim-arabic/commit/b30eb9cc44cfe1fe4771421c96a71033d712e416)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - default font auto-resolution (the upstream default "Al Bayan" is macOS-only, so the module failed everywhere else; `create_arabic_template`/`create_arabic_text` now pick the first installed font from a candidate list via fontconfig when no font is passed)

## `manim_extensions/automata`
  - **Upstream:** [SeanNelsonIO/manim-automata](https://github.com/SeanNelsonIO/manim-automata)
  - **Synced:** [`0e572726311e4adeb5323deecc7cfcdb401cc1a6`](https://github.com/SeanNelsonIO/manim-automata/commit/0e572726311e4adeb5323deecc7cfcdb401cc1a6)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - `mobjects/automata_dependencies/xml_parser.py` lazy-imports xmltodict (`automata` extra)
    - `manim_automaton.py` undefined-name fix in the nda_builder branch (was masked by a star import)
    - removed the unused `ManimAutomataCLI.non_deterministic_finite_automata_path_builder_callback` stub, which only raised `NotImplementedError`
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/cad_drawing_utils`
  - **Upstream:** [GarryBGoode/Manim_CAD_Drawing_utils](https://github.com/GarryBGoode/Manim_CAD_Drawing_utils)
  - **Synced:** [`8c665e1b5dd8123dc7c0d44bcc57f7ce39984714`](https://github.com/GarryBGoode/Manim_CAD_Drawing_utils/commit/8c665e1b5dd8123dc7c0d44bcc57f7ce39984714)
  - **Status:** vendored from PyPI 0.0.5 (upstream HEAD, 2026-02-03)
  - **Local patches:**
    - SPDX header; explicit public exports; rebinding of the `utils` submodule
    - package version corrected to 0.0.5
    - Black formatting applied to the vendored sources

## `manim_extensions/chemistry`
  - **Upstream:** [UnMolDeQuimica/manim-Chemistry](https://github.com/UnMolDeQuimica/manim-Chemistry)
  - **Synced:** [`c03147d4f9374cd75b58257962210e9020895d15`](https://github.com/UnMolDeQuimica/manim-Chemistry/commit/c03147d4f9374cd75b58257962210e9020895d15)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - element/periodic-table/parsers lazy-import pandas, requests, xmltodict (`chemistry` extra)
    - `future_classes.py` missing `functools.wraps` import (was masked by a star import)
    - `from_mol_string` accepts the whole MOL block, hydrogen bonds without stereo are drawn as ``SimpleBond``, ``Element`` tolerates disabled electrons, and ``BatterySchema.invert_terminals`` uses the keyword ``rotate`` form
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/circuit`
  - **Upstream:** [Mr-FuzzyPenguin/manim-circuit](https://github.com/Mr-FuzzyPenguin/manim-circuit)
  - **Synced:** [`5d5ab2c81962be835efd1270e1eb463abb7b66b2`](https://github.com/Mr-FuzzyPenguin/manim-circuit/commit/5d5ab2c81962be835efd1270e1eb463abb7b66b2)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)

## `manim_extensions/code_blocks`
  - **Upstream:** [CasualCodersProjects/manim-code-blocks](https://github.com/CasualCodersProjects/manim-code-blocks)
  - **Synced:** [`0eb9e5d6b5ccf12fe480ddcaa8744eab9d912297`](https://github.com/CasualCodersProjects/manim-code-blocks/commit/0eb9e5d6b5ccf12fe480ddcaa8744eab9d912297)
  - **Status:** vendored from PyPI 1.0.14 (upstream HEAD, 2024-02-20)
  - **Local patches:**
    - SPDX header; bundled the GitHub language colour table; removed the import-time `urlopen` request
    - lazy-loads `tokenize-all-code` through the `code_blocks` extra
    - Black formatting applied to the vendored sources

## `manim_extensions/compass`
  - **Upstream:** [jj-math/manim-compass](https://github.com/jj-math/manim-compass)
  - **Synced:** [`4dfe83f176652e7748ca2e5b475da7fff241f5c6`](https://github.com/jj-math/manim-compass/commit/4dfe83f176652e7748ca2e5b475da7fff241f5c6)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)
    - merged upstream `SingleRulerScene` (`scene/ruler_scene.py`, 2026-10-25 re-sync) with imports normalized to explicit form

## `manim_extensions/data_structures`
  - **Upstream:** [drageelr/manim-data-structures](https://github.com/drageelr/manim-data-structures)
  - **Synced:** [`1465eefab154c4016b41e918b585e83132372782`](https://github.com/drageelr/manim-data-structures/commit/1465eefab154c4016b41e918b585e83132372782)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)

## `manim_extensions/economics`
  - **Upstream:** [ddzhang04/manim_ec](https://github.com/ddzhang04/manim_ec)
  - **Synced:** [`8e699d32196a190b8e2cb8b41c727e22050a01c6`](https://github.com/ddzhang04/manim_ec/commit/8e699d32196a190b8e2cb8b41c727e22050a01c6)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)

## `manim_extensions/fontawesome`
  - **Upstream:** [naveen521kk/manim-fontawesome](https://github.com/naveen521kk/manim-fontawesome) (wrapper); [FortAwesome/Font-Awesome](https://github.com/FortAwesome/Font-Awesome) (SVG assets)
  - **Synced:** [`b3144d7abd65843a14d361754b87f7615dc59977`](https://github.com/naveen521kk/manim-fontawesome/commit/b3144d7abd65843a14d361754b87f7615dc59977)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - wrapper import style normalization
    - assets under `font-awesome/` are CC BY 4.0, see REUSE.toml
    - added a public `list_icons()` helper (upstream has no way to enumerate icon names)
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/gearbox`
  - **Upstream:** [GarryBGoode/manim-GearBox](https://github.com/GarryBGoode/manim-GearBox)
  - **Synced:** [`5fe6d6f93c204da1966e855ea5ba3a953449bf7d`](https://github.com/GarryBGoode/manim-GearBox/commit/5fe6d6f93c204da1966e855ea5ba3a953449bf7d)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)

## `manim_extensions/machine_learning`
  - **Upstream:** [helblazer811/ManimML](https://github.com/helblazer811/ManimML)
  - **Synced:** [`5e8f7cb69f23919f9ec7e880fb22c1ca2f841c08`](https://github.com/helblazer811/ManimML/commit/5e8f7cb69f23919f9ec7e880fb22c1ca2f841c08)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - diffusion/decision-tree/plotting lazy-import matplotlib, seaborn, scikit-learn (`ml` extra)
    - several latent undefined-name fixes surfaced by removing star imports (quoted `NeuralNetworkLayer` annotations now import the real base class, `leaf_child_index` typo, dead code after `raise NotImplementedError`, `new_connective` misname, missing `plt`/`wraps`)
    - implemented the remaining upstream stubs (upstream is archived, so they will not be fixed there):
      - `scene.play` forwarding
      - `MaxPooling2DLayer` Create override
      - three-channel image → convolution animation
      - `FeedForwardToFeedForward.modify_edge_colors`
      - activation evaluation point highlight
      - text leaf nodes + BFS/level-order tree expansion + split-to-animation map + best-first traversal, a `DecisionTreeEmbedding` module (upstream only names this class in its docstrings and never shipped it) and the tree/surface unfolding animation built from it, with non-overlapping leaf spacing and no bogus length unit in split labels
      - `NeuralNetwork.replace_layer`
      - `VariationalAutoencoder.make_triplet_forward_pass` and a working `make_image_forward_pass` (upstream nests a `NeuralNetwork` as a layer, which fails because networks have no `construct_layer`)
    - removed stale TODOs and unreachable branches
    - `BlankConnective` now implements the inherited abstract `construct_layer`, so layer pairs without a registered connective fall back to an empty connective instead of raising `TypeError: Can't instantiate abstract class`
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/meshes`
  - **Upstream:** [bmmtstb/manim-meshes](https://github.com/bmmtstb/manim-meshes)
  - **Synced:** [`9d6cb8341a7538ee6a9448d162e3de215211e9ad`](https://github.com/bmmtstb/manim-meshes/commit/9d6cb8341a7538ee6a9448d162e3de215211e9ad)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - `params.py`, `templates.py`, `models/manim_models/opengl_mesh.py` lazy-import moderngl/trimesh (`meshes` extra)
    - implemented 3D and 4-D `templates.create_grid` (a 4-D grid is the tesseract: 16 vertices / 24 faces / 32 edges), `Mesh.apply_flip` / `ManimMesh.flip`, 4-D centre projection (`get_3d_vertices` / `convert_vertices_to_3d`) and 4-D plane rotation (`apply_rotation` / `ManimMesh.rotate`), all of which upstream still raises `NotImplementedError` for
    - `__add__` returns a new mesh instead of mutating `self`, and `__add__` / `__iadd__` / `__eq__` / `__ne__` return `NotImplemented` for non-mesh operands
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/mindmap`
  - **Upstream:** [jj-math/manim-mindmap](https://github.com/jj-math/manim-mindmap)
  - **Synced:** [`7fe1e5adddfd579aa2b27a0eace3a90560344b30`](https://github.com/jj-math/manim-mindmap/commit/7fe1e5adddfd579aa2b27a0eace3a90560344b30)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)
    - renamed the misspelled node-state enum to `NodeState`

## `manim_extensions/mobject_svg`
  - **Upstream:** [naveen521kk/manim-mobject-svg](https://github.com/naveen521kk/manim-mobject-svg)
  - **Synced:** [`2b8c62b8dda30798f16b7420b05349d2983989f8`](https://github.com/naveen521kk/manim-mobject-svg/commit/2b8c62b8dda30798f16b7420b05349d2983989f8)
  - **Status:** synced (v0.5.0)
  - **Local patches:**
    - source identical to v0.5.0 (`f184c3a`)
    - the three newer upstream commits only touch `poetry.lock` and `pyproject.toml`
    - import/doc style normalization
    - added module docstrings and SPDX headers
    - typed and documented the cairo context helpers (`Iterator[cairo.Context]`, `int | None`)
    - documented `CAIRO_LINE_WIDTH_MULTIPLE` with a ``#:`` docstring
    - replaced `tempfile.mktemp` with `NamedTemporaryFile` in the two `create_svg_*` entry points
    - corrected the upstream `_apply_fill` docstring that advertised a `Camera` return value

## `manim_extensions/nerdfont`
  - **Upstream:** [Alexander-Nasuta/manim-nerdfont-icons](https://github.com/Alexander-Nasuta/manim-nerdfont-icons)
  - **Synced:** [`46878cdd68cdda1bbd5c91804ba90a60ebf0a45f`](https://github.com/Alexander-Nasuta/manim-nerdfont-icons/commit/46878cdd68cdda1bbd5c91804ba90a60ebf0a45f)
  - **Status:** pinned; patched (PyPI 1.0.x locks manim<0.20)
  - **Local patches:**
    - `icons.py` loads the bundled font via `importlib.resources.files()` and from this package instead of `manim_nerdfont_icons.resources` (the upstream `pkg_resources.path()` call was removed in Python 3.13)
    - vendored because the 1.0.x PyPI release pins `manim>=0.19,<0.20`
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/physics`
  - **Upstream:** [Matheart/manim-physics](https://github.com/Matheart/manim-physics)
  - **Synced:** [`d37580e07ac67d06c8dfbb78804b8a0256d1502b`](https://github.com/Matheart/manim-physics/commit/d37580e07ac67d06c8dfbb78804b8a0256d1502b)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - rigid mechanics/optics lazy-import pymunk/shapely (`physics` extra)

## `manim_extensions/pymunk`
  - **Upstream:** [HHP999/manim_pymunk](https://github.com/HHP999/manim_pymunk)
  - **Synced:** [`c1122865dc90ed0a71361ef77f73ec72c87e256a`](https://github.com/HHP999/manim_pymunk/commit/c1122865dc90ed0a71361ef77f73ec72c87e256a)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - constraints/space/utils lazy-import pymunk (`physics` extra)
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/qr_codes`
  - **Upstream:** [Alexander-Nasuta/manim-qr-codes](https://github.com/Alexander-Nasuta/manim-qr-codes)
  - **Synced:** [`db49a0002bda401fe8be22fb93420e4273c0da8a`](https://github.com/Alexander-Nasuta/manim-qr-codes/commit/db49a0002bda401fe8be22fb93420e4273c0da8a)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - `qr.py` uses the vendored `nerdfont` instead of the manim-nerdfont-icons package and lazy-imports segno (`qr` extra)

## `manim_extensions/radar`
  - **Upstream:** [FTZ-OPUS/manim-radar](https://github.com/FTZ-OPUS/manim-radar)
  - **Synced:** [`59bc6cf170c590104f5676b2435f2cb1d0c06c7b`](https://github.com/FTZ-OPUS/manim-radar/commit/59bc6cf170c590104f5676b2435f2cb1d0c06c7b)
  - **Status:** vendored from PyPI 0.1.2 (upstream HEAD, 2026-09-21)
  - **Local patches:**
    - SPDX header; CLI import path normalized to `manim_extensions.radar`
    - console script exposed as `manim-radar`
    - Black formatting applied to the vendored sources

## `manim_extensions/rubikscube`
  - **Upstream:** [WampyCakes/manim-rubikscube](https://github.com/WampyCakes/manim-rubikscube)
  - **Synced:** [`e117d42eb4b7484957440a4c9d67ab183bb06e0a`](https://github.com/WampyCakes/manim-rubikscube/commit/e117d42eb4b7484957440a4c9d67ab183bb06e0a)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - `cube.py` lazy-imports kociemba (`rubikscube` extra)
    - `cube_animations.py` applies `rate_func` in `interpolate_mobject` (manim 0.21 requires subclasses to apply it manually, so turns were linear instead of smooth)
    - implemented the local `cube_utils` state helpers `get_cubie_colors_from_state` and `get_all_states` (upstream does not provide them, and the vendored stubs returned ``None``)

## `manim_extensions/sequence_diagram`
  - **Upstream:** [foxnewsnetwork/manim-sequence-diagram](https://github.com/foxnewsnetwork/manim-sequence-diagram)
  - **Synced:** [`8232636ead85af41b720561252d4749926b03ba7`](https://github.com/foxnewsnetwork/manim-sequence-diagram/commit/8232636ead85af41b720561252d4749926b03ba7)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/straightedge_compass`
  - **Upstream:** [manim-straightedge-compass](https://pypi.org/project/manim-straightedge-compass/)
  - **Synced:** PyPI 0.1.1
  - **Status:** vendored from PyPI (no public GitHub repository)
  - **Local patches:**
    - SPDX header; package references normalized to `manim_extensions.straightedge_compass`
    - Black formatting applied to the vendored sources

## `manim_extensions/svg_animations`
  - **Upstream:** [MathItYT/manim-svg-animations](https://github.com/MathItYT/manim-svg-animations)
  - **Synced:** [`da696ce5693d6cb57d97553a8f7534b8dbe5ace5`](https://github.com/MathItYT/manim-svg-animations/commit/da696ce5693d6cb57d97553a8f7534b8dbe5ace5)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization
    - `html_parsed_vmobject.py` lazily imports the vendored `mobject_svg` module and svgpathtools (`svg` extra)
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/table`
  - **Upstream:** [philippe2803/manim-table](https://github.com/philippe2803/manim-table)
  - **Synced:** [`7a882ccd959c8b04637268e8d2a2f4f0d7ea57b5`](https://github.com/philippe2803/manim-table/commit/7a882ccd959c8b04637268e8d2a2f4f0d7ea57b5)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)
    - documented module-level constants with ``#:`` docstrings

## `manim_extensions/three_d`
  - **Upstream:** [FTZ-OPUS/manim-3d](https://github.com/FTZ-OPUS/manim-3d)
  - **Synced:** [`334f65549691c8c90cb0e9c30855b1e2cb4bd896`](https://github.com/FTZ-OPUS/manim-3d/commit/334f65549691c8c90cb0e9c30855b1e2cb4bd896)
  - **Status:** vendored from PyPI 0.1.1 (tag `v0.1.1`)
  - **Local patches:**
    - SPDX header; CJK subtitles resolve through `manim_extensions.mobjects.DEFAULT_CJK_FONT` instead of the macOS-only `PingFang SC`
    - package version corrected to 0.1.1
    - Black formatting applied to the vendored sources

## `manim_extensions/tikz`
  - **Upstream:** [ralphieraccoon/manim-tikz](https://github.com/ralphieraccoon/manim-tikz)
  - **Synced:** [`3a3c5c6115c6412555501ffa4440899164c89385`](https://github.com/ralphieraccoon/manim-tikz/commit/3a3c5c6115c6412555501ffa4440899164c89385)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)

## `manim_extensions/weighted_line`
  - **Upstream:** [mutable-learning/manim-weighted-line](https://github.com/mutable-learning/manim-weighted-line)
  - **Synced:** [`e2f4b42df135942d920c00bc1810688644771d75`](https://github.com/mutable-learning/manim-weighted-line/commit/e2f4b42df135942d920c00bc1810688644771d75)
  - **Status:** synced (upstream HEAD, 2026-10-25 re-sync)
  - **Local patches:**
    - import/doc style normalization (commit `712865f`)
