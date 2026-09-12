# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

# Vendored packages
#
# manim_extensions aggregates a number of small upstream Manim extension
# projects. This file records, for each vendored package, where it came
# from, which upstream version it was synced at, and which local patches
# deviate from upstream. Patches are also marked in the patched files
# themselves with a `# patched: <reason>` line in the file header.
#
# Version history note: most packages below were vendored before this
# registry existed, so their exact upstream tag/commit is not recorded;
# only subsequently synced packages carry a precise version.

| Local module | Upstream repository | Synced tag/commit | Local patches |
| --- | --- | --- | --- |
| `manim_extensions/algorithm` | https://github.com/sinianluoye/manim-algorithm | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/arabic` | https://github.com/razekmh/manim-arabic | not recorded | import/doc style normalization; default font auto-resolution (the upstream default "Al Bayan" is macOS-only, so the module failed everywhere else; `create_arabic_template`/`create_arabic_text` now pick the first installed font from a candidate list via fontconfig when no font is passed) |
| `manim_extensions/automata` | https://github.com/SeanNelsonIO/manim-automata | not recorded | import/doc style normalization; `mobjects/automata_dependencies/xml_parser.py` lazy-imports xmltodict (`automata` extra) |
| `manim_extensions/chemistry` | https://github.com/UnMolDeQuimica/manim-Chemistry | not recorded | import/doc style normalization; element/periodic-table/parsers lazy-import pandas, requests, xmltodict (`chemistry` extra) |
| `manim_extensions/circuit` | https://github.com/Mr-FuzzyPenguin/manim-circuit | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/compass` | https://github.com/jj-math/manim-compass | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/data_structures` | https://github.com/drageelr/manim-data-structures | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/economics` | https://github.com/ddzhang04/manim_ec | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/fontawesome` | https://github.com/naveen521kk/manim-fontawesome (wrapper); https://github.com/FortAwesome/Font-Awesome (SVG assets) | not recorded | wrapper import style normalization; assets under `man-awesome/` are CC BY 4.0, see REUSE.toml |
| `manim_extensions/gearbox` | https://github.com/GarryBGoode/manim-GearBox | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/machine_learning` | https://github.com/helblazer811/ManimML | not recorded | import/doc style normalization; diffusion/decision-tree/plotting lazy-import matplotlib, seaborn, scikit-learn (`ml` extra) |
| `manim_extensions/meshes` | https://github.com/bmmtstb/manim-meshes | not recorded | import/doc style normalization; `params.py`, `templates.py`, `models/manim_models/opengl_mesh.py` lazy-import moderngl/trimesh (`meshes` extra) |
| `manim_extensions/mindmap` | https://github.com/jj-math/manim-mindmap | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/physics` | https://github.com/Matheart/manim-physics | not recorded | import/doc style normalization; rigid mechanics/optics lazy-import pymunk/shapely (`physics` extra) |
| `manim_extensions/pymunk` | https://github.com/HHP999/manim_pymunk | not recorded | import/doc style normalization; constraints/space/utils lazy-import pymunk (`physics` extra) |
| `manim_extensions/qr_codes` | https://github.com/Alexander-Nasuta/manim-qr-codes | not recorded | import/doc style normalization; `qr.py` uses the vendored `utils.nerdfont` instead of the manim-nerdfont-icons package and lazy-imports segno (`qr` extra) |
| `manim_extensions/rubikscube` | https://github.com/WampyCakes/manim-rubikscube | not recorded | import/doc style normalization; `cube.py` lazy-imports kociemba (`rubikscube` extra) |
| `manim_extensions/sequence_diagram` | https://github.com/foxnewsnetwork/manim-sequence-diagram | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/svg_animations` | https://github.com/MathItYT/manim-svg-animations | not recorded | import/doc style normalization; `html_parsed_vmobject.py` lazily imports the manim-mobject-svg plugin and svgpathtools (`svg` extra) |
| `manim_extensions/table` | https://github.com/philippe2803/manim-table | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/tikz` | https://github.com/ralphieraccoon/manim-tikz | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/utils/nerdfont` | https://github.com/Alexander-Nasuta/manim-nerdfont-icons | `1.0.2` | `icons.py` loads the bundled font via `importlib.resources.files()` and from this package instead of `manim_nerdfont_icons.resources` (the upstream `pkg_resources.path()` call was removed in Python 3.13); vendored because the 1.0.x PyPI release pins `manim>=0.19,<0.20` |
| `manim_extensions/weighted_line` | https://github.com/mutable-learning/manim-weighted-line | not recorded | import/doc style normalization (commit `712865f`) |
| `manim_extensions/animations.py`, `manim_extensions/mobjects.py` | https://github.com/manim-kindergarten (manim_sandbox helpers) | not recorded | `mobjects.py` lazy-imports cv2 (`video` extra) |
