.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Changelog
=========
v1.0.6 :bdg-primary-line:`In development`
-----------------------------------------

**Added**

* Added :class:`~manim_extensions.nerdfont.icons.NerdFontIcon` (a class
  replacing the earlier ``nerdfont_icon`` function) for rendering Nerd
  Font glyphs as ``ImageMobject`` instances.
* Added a searchable Icon Gallery page listing every Nerd Font symbol, with
  a live filter that hides the empty state until the first search.
* Added :class:`~manim_extensions.arabic.text.ArabicTemplate` and
  :class:`~manim_extensions.arabic.text.ArabicText` classes, replacing the
  ``create_arabic_*`` helper functions, for shaping and rendering Arabic
  text.
* Added :class:`~manim_extensions.compass.scene.ruler_scene.SingleRulerScene`
  to :mod:`~manim_extensions.compass` for single-ruler constructions (one ruler, one pencil, with
  a ``draw_line_with_pencil`` method).
* Added :class:`~manim_extensions.scenes.ConstantStrokeWidthScene`, which
  keeps stroke width constant under camera zoom, and accepted
  ``fixed_stroke_width`` as a mobject constructor keyword so the behaviour
  also applies to nested mobjects.
* Added
  :class:`~manim_extensions.machine_learning.decision_tree.decision_tree_embedding.DecisionTreeEmbedding`,
  a :class:`~manim.mobject.types.vectorized_mobject.VGroup` that pairs a
  fitted scikit-learn tree with its training points: dataset axes, one dot
  per sample, and the decision-region rectangles from
  :class:`~manim_extensions.machine_learning.decision_tree.decision_tree_surface.DecisionTreeSurface`,
  with ``Create`` / ``Uncreate`` overrides and a split-to-animation map.
* Implemented
  :meth:`~manim_extensions.machine_learning.decision_tree.decision_tree.DecisionTreeContainer.make_unfold_tree_animation`,
  which previously halted with ``NotImplementedError``: it unfolds the tree
  in ``bfs``, ``level`` or ``best`` order beside the embedding, accepts a
  fitted classifier or a bare ``tree_`` object, and ships with regression
  tests and a rendered doc example.
* Implemented the remaining ManimML placeholders, since upstream is
  archived: :meth:`~manim_extensions.machine_learning.scene.ManimML3DScene.play` forwards to
  :class:`~manim.scene.three_d_scene.ThreeDScene`,
  :class:`~manim_extensions.machine_learning.neural_network.layers.max_pooling_2d.MaxPooling2DLayer`
  gains a real ``Create`` override, three-channel images animate onto
  convolutional feature maps, :meth:`~manim_extensions.machine_learning.neural_network.layers.feed_forward_to_feed_forward.FeedForwardToFeedForward.modify_edge_colors`
  works, the evaluated point is highlighted in activation animations, leaf
  nodes and tree expansion accept text, :meth:`~manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork.replace_layer` and
  the VAE triplet pass are implemented, and stale TODOs and unreachable
  branches are gone. Every existing public signature keeps its previous
  default behaviour.
* Extended the mesh data model and
  :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh`
  to four dimensions: central projection (``scale = d / (d - w)``), rotations
  in the ``(2, 4)`` plane, flips with 4D semantics, and
  :func:`~manim_extensions.meshes.templates.create_grid` building a tesseract
  (16 vertices, 24 square faces, 32 edges).
* Completed the 3D grid templates and mesh flipping for the vendored mesh
  package, so ``create_grid`` covers the cube and tetrahedral layouts and
  ``apply_flip`` works on the 3D meshes it produces.
* Implemented the Rubik's Cube facelet state helpers
  (``get_cubie_colors_from_state`` and ``get_all_states``), which previously
  returned ``None``: states now round-trip through
  :meth:`~manim_extensions.rubikscube.cube.RubiksCube.set_state` and malformed input raises ``ValueError``.
* Added the ``manim-chemistry`` and ``manim-rubikscube`` console commands.
* Added a ``module-index`` directive that renders the Reference Manual
  Module Index with per-package titles and marks vendored packages that
  are behind their upstream commit with a warning badge.
* Added per-page inheritance diagrams to every reference class page, with
  a single consolidated graph and dark-theme support.
* Added a ``validate-api-coverage`` check (and refreshed the API snapshot)
  so every public name is documented.
* Added a Constants overview page documenting directions, colours, and
  values that the official Manim documentation does not list.
* Added a ``Vendor status`` column to ``VENDORED.md`` and sorted its table
  alphabetically by local module.
* Added a ``setup-manim-env@v1`` shared action to the CI workflows.

**Changed**

* Re-synced 17 vendored packages to their latest upstream commits
  (:mod:`~manim_extensions.compass` merged
  :class:`~manim_extensions.compass.scene.ruler_scene.SingleRulerScene`);
  each page records its upstream repository, sync commit, and local patches
  in ``VENDORED.md``, and the old sync script is gone in favour of manual,
  reviewed merges.
* Simplified type annotations across the package with Manim's typing
  aliases (``Point3D``, ``Vector3D``, ...) and ``typing.Self`` for
  self-returning methods, replacing local aliases and open generics.
* Raised the supported versions to ``Pillow >= 12.2`` and
  ``manim >= 0.22.1``.
* Reworked the chemistry CLI documentation around the ``manim-chemistry``
  console command instead of ``python -m`` module invocations.
* Made :meth:`~manim_extensions.chemistry.utils.pubchem_api.PubchemAPIManager.from_inchi` resolve the InChI to an InChIKey
  first, and sanitised path characters in the InChI so the SDF lookup no
  longer writes into a non-existent folder.
* Fixed the VAE image forward pass so the decoder receives the latent
  tensor and the architecture figure renders in the network.
* Fixed the 3D depth-order flicker in :class:`~manim_extensions.rubikscube.cube.RubiksCube` rotation by ordering
  the cubie layers correctly.
* Placed the gear on the rack's toothed side in ``mesh_to``.
* Turned bare class names in docstrings into ``:class:`` cross-references
  across the repository, using each class's real module for the target
  (172 first mentions plus 54 repeated ones).
* Fixed the decision-region rectangle offsets in
  :class:`~manim_extensions.machine_learning.decision_tree.decision_tree_surface.DecisionTreeSurface`
  and dropped a stray ``print`` from its polygon builder.
* Stopped :class:`~manim_extensions.machine_learning.decision_tree.decision_tree.SplitNode`
  from appending a bogus ``cm`` unit to its threshold text, and scaled its
  doc example so the figure fills the frame.
* Refined ``Any`` annotations across the package to concrete types.
* Moved the vendored ``nerdfont`` package from utils to the top level
  and updated the remaining path references.

**Fixed**

* Fixed the dangling :class:`~manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh` cross-reference in the ``create_grid``
  docstring.
* Fixed the type-annotation and doc-example checks that the new ManimML
  surface exposed.
* Fixed the ``m.`` references left behind in the ``qr_codes`` doc examples.
* Fixed bare direction constants in prose: they now either resolve to
  ``manim.constants`` or stay literal, instead of mis-linking the DOWN constant.
* Fixed generic numpydoc words being auto-linked as types (``Parameters``
  no longer resolves to ``meshes.types.Parameters``).
* Fixed ``Point3D`` / ``Vector3D`` aliases so they resolve to Manim's typing
  inventory instead of local copies.
* Fixed the relative import of ``__version__`` and its use in the Rubik's
  Cube entry point.
* Fixed the resistor label to use proper LaTeX math.
* Fixed the machine-learning example rendering: :class:`~manim_extensions.machine_learning.utils.mobjects.image.GrayscaleImageMobject`
  is built with ``RGB`` instead of ``RBG``, matplotlib figures are converted
  to RGB, and the VAE renders as a ``Group`` that actually shows the
  network.
* Fixed incomplete cross-references across the reference manual.
* Fixed the Validate workflow failures around doc sections, unused imports,
  and REUSE lint.

**Documentation and hygiene**

* Reorganised the reference manual package by package: ``chemistry``,
  automata, algorithm, data structures, economics,
  pymunk, mindmap, machine learning, table, and the rest
  now use category pages instead of one flat page per module.
* Folded each vendored package's upstream README and Read the Docs content
  into its Reference Manual page and led with API sections instead of a
  Quick Start.
* Completed every ManimML usage snippet into a standalone ``Scene`` and
  rendered it with the ``manim`` directive (image-input example stays a
  runnable script because the upstream repository ships no ``digit.jpeg``).
* Converted every package's ``Usage`` code block into a ``.. manim::``
  directive so examples render inline, with the remaining renderable blocks
  converted as well.
* Rescaled doc examples to the camera frame (``RackExample``,
  ``BasicCircuitComponents``, ``LensScene``, ``WaveScene``, the physics
  scenes), and exempted seven physics examples whose mobjects physically
  fly out of frame.
* Made 41 single-animation examples seamless loops wherever the motion is
  rotation-symmetric or a round trip.
* Rendered ``Attributes`` sections as Parameters-style bulleted lists,
  moved before ``Examples``.
* Removed default-value descriptions from docstrings and added a
  ``CONTRIBUTING`` rule covering docstring conventions.
* Enforced numpydoc section spacing: no blank line after a section
  underline, and summaries separated from section headers.
* Replaced monotone ``note`` admonitions with a varied set
  (``tip`` / ``important`` / ``warning`` / ``todo`` / ``seealso``), with
  unimplemented methods marked ``todo``.
* Removed ``-> None`` return annotations (Sphinx would otherwise inject a
  redundant ``RETURN TYPE: None`` block) and added the corresponding
  ``CONTRIBUTING`` rule.
* Added ``Returns`` sections across the packages, including the economics
  pages, and strengthened the return-section validation.
* Normalised numpydoc docstrings across the package: parameter names are
  wrapped in double backticks, manual type annotations are gone, and
  summaries that only restated the ``Returns`` section were dropped.
* Pruned inherited attributes from class pages so that only redefined ones
  are listed.
* Required a leading ``~`` on module-prefixed cross-references and a bare
  target for builtins, and documented the rule in ``CONTRIBUTING``.
* Self-hosted MathJax 4 in SVG output to fix intermittent formula
  rendering and remove font dependencies.
* Reworked link colouring: Python builtin type links render in body
  colour without an underline; signature default-value links and Manim
  constant references use the cross-reference palette; dark-mode colours
  were tuned for readability.
* Pinned ``sphinx-autodoc-typehints`` to 3.10.3 and patched it so Manim
  typing aliases (``Point3D``, ``Vector3D``, ...) are kept unexpanded
  instead of being unwrapped into ``tuple[float, ...]``.
* Dropped unused bundled code fonts in favour of the system monospace
  stack, and let code font size be tuned per type.
* Documented private members in the API reference and nested class pages
  under their modules, with a per-source-file page granularity.
* Ordered the Module Index alphabetically, used each package's real page
  title, and kept a hidden sidebar toctree so the navigation tree is
  preserved.
* Rewrote ``CODE_OF_CONDUCT`` as the project's own code and removed
  duplicate chemistry overview pages plus stray rendered images.

**CI**

* Consumed the shared ``ExploreMaths/setup-manim-env@v1`` action across
  workflows.
* Extended the Validate workflow with type-annotation, return-annotation,
  doc-section, cross-reference, API-coverage, docstring, parameter,
  import, relative-import, RST, ``manim``-directive, unused-import,
  REUSE, and dependency-audit jobs, and reached zero Sphinx warnings.
* Added a ``validate-example-layout`` job that renders every doc example and
  fails when the figure overflows the frame or covers less than a quarter of
  it in both dimensions.
* Made the layout probe mirror real rendering: it runs the example's setup
  before ``construct``, patches the manim 0.22 ``ImageMobject`` render
  regression, installs a modern ``dvisvgm``, and bounds the render job time.
* Installed every optional extra in the cross-reference job so external
  inventory targets resolve.
* Added intersphinx mappings for the external libraries and a CI guard that
  keeps them in sync.
* Cached apt archives and pip downloads in the package test jobs.
* Backed out the CI auto-refresh of the API snapshot in favour of manual,
  reviewed snapshot updates.
* Made API coverage ignore type aliases and type variables, and blocked
  ambiguous class names in the cross-reference job.


v1.0.5 :bdg-success-line:`Latest`
---------------------------------

**Added**

* Added ``workflow/sync_vendored.py`` and a manually triggered
  ``sync-vendored`` workflow that pulls upstream updates for vendored
  modules, preserves local patches via a 3-way merge, reports every API
  surface change (added / removed functions, methods, classes, and
  parameters), and opens a pull request for review.
* Bundled 10 additional third-party Manim plugins as subpackages:
  ``arabic``, ``chemistry``, ``economics``, ``fontawesome``,
  ``machine_learning`` (ManimML), ``pymunk``, ``qr_codes``,
  ``svg_animations``, table, and weighted_line — plus
  ``manim-nerdfont-icons`` 1.0.2, vendored as
  ``manim_extensions.nerdfont`` because its PyPI metadata pins
  ``manim>=0.19,<0.20`` (code and font licensed separately, font shipped
  as package data).
* Added API reference documentation for every bundled package, with a
  single consolidated inheritance graph in the Reference Manual.
* Added a same-named optional extra for every module (automata,
  ``chemistry``, ``physics``, ``rubikscube``, ``meshes``, ``video``,
  ``qr``, ``svg``, ``ml``, ...) and an ``all`` extra; the base install
  is now just ``manim`` + ``numpy``, and every heavier dependency is
  lazy-imported via the new ``manim_extensions.utils.deps.require``
  helper whose error names the exact ``pip install manim_extensions[...]``
  command. A subprocess-based test blocks all optional packages via a
  meta-path finder and asserts the base package and all 250+ submodules
  still import.
* Added ``VENDORED.md``: a registry of every vendored package's upstream
  repository, sync version, and local patches (also marked in-file with
  ``# patched:`` header lines).
* Added comprehensive pytest coverage for previously untested modules
  (the suite grows from 331 to 421 tests), including import-resolution
  regressions, optional-dependency guards, and per-module behaviour.
* Added CI: a ``manim-latest`` job that upgrades to the newest manim
  release and runs the full suite (turning ``manim>=0.21.0`` from a
  claim into a tested guarantee); a ``docs-cache`` workflow that
  pre-renders every doc example at high quality into the ``rtd-cache``
  branch (content-hash incremental, pytest-style progress output) so
  Read the Docs reuses the media instead of timing out; and an RTD API
  trigger that also builds tagged versions after syncing them.
* Added ``workflow/check_relative_imports.py`` and
  ``validate-relative-imports`` / ``validate-docstrings`` /
  ``validate-refs`` jobs to the Validate workflow.
* Added full type annotations to every function and method parameter
  across the entire codebase (544+ functions in 128 files, ~1286
  annotations), plus a ``validate-type-annotations`` CI job
  (``scripts/check_type_annotations.py``) to enforce the requirement
  going forward.
* Added rounded-corner static cover images to the README.

**Changed**

* Changed the default character interval of
  :class:`~manim_extensions.animations.TypeWriter` from ``2`` seconds to
  ``0.1`` seconds. The old default stretched a typical line of text over
  tens of seconds; every documentation example already overrode it.
* :class:`~manim_extensions.mobjects.ChineseMathTex` now defaults
  ``tex_to_color_map`` to ``None`` instead of a shared mutable ``{}``,
  so instances no longer risk mutating each other's colour map.
* Raised the minimum Manim version from ``>=0.19.1`` to ``>=0.21.0`` and
  migrated the table module from ``manimlib`` (ManimGL) to Manim
  Community Edition.
* Replaced the type-specific geometry intersection helpers with a single
  generic ``VMobjectInt``.
* Converted all intra-package absolute imports to relative imports, and
  banned ``from manim import *`` outside ``__init__.py`` across the whole
  repository (165 files converted to explicit imports; the import-style
  checker was inverted accordingly). This also surfaced and fixed real
  latent bugs that star imports had masked from pyflakes (see Fixed).
* Converted all Google-style ``Args:`` docstring sections to numpydoc
  ``Parameters`` (64 sections across 16 files) and added a ``--fix`` mode
  to the docstring validator to keep it that way.
* Normalised indexed labels in doc examples to LaTeX subscripts
  (``V0`` → ``V_0``, ``ext{A1}`` → ``ext{A}_1``, ``P{i+1}`` →
  ``P_{i+1}``).
* Reworked the docs build: examples are pre-rendered by CI and reused on
  RTD via a media cache; README cover media switched from GIFs to three
  rounded static images; ``conf.py`` version synced to 1.0.5 and the
  changelog gained a sphinx-design ``Latest`` badge.
* :class:`~manim_extensions.rubikscube.cube.RubiksCube` doc examples now
  use the default realistic colour scheme instead of an ad-hoc palette.

**Removed**

* Removed the ``[tool.flake8]`` section from ``pyproject.toml``. Flake8
  does not read ``pyproject.toml``; the section was dead configuration,
  and CI passes every flake8 option on the command line.

**Fixed**

* Fixed ``qr_codes/__init__.py`` importing a nonexistent ``QRCode``
  class and the root ``__init__.py`` importing a nonexistent ``ml``
  module — both broke ``import manim_extensions``.
* Fixed manim's utils namespace shadowing the package's own utils
  submodules.
* Fixed machine-learning empty-animation groups being unplayable on
  manim >= 0.21, and the pymunk 7 collision-API /
  :class:`~manim_extensions.economics.base.ADASDiagram` ``numbered_eq``
  regressions.
* Fixed :class:`~manim_extensions.rubikscube.cube_animations.CubeMove` face turns being strictly linear: manim 0.21
  expects subclasses to apply ``rate_func`` themselves, so the rotation
  now eases in and out like the original ManimGL version.
* Fixed the Arabic module failing on every non-macOS platform: the
  macOS-only ``Al Bayan`` default is replaced by fontconfig-based
  auto-resolution (Amiri/Scheherazade/Noto Naskh Arabic...).
* Latent undefined-name bugs surfaced by removing star imports:
  :class:`~manim_extensions.machine_learning.neural_network.layers.parent_layers.NeuralNetworkLayer`
  quoted annotations now import the real base
  class; ``leaf_child_index`` typo; dead code after
  ``raise NotImplementedError()``; an undefined ``transition_ids`` in
  the nondeterministic-automata path; missing ``functools.wraps``,
  ``plt``, ``manim_version``, and ``svg2paths`` imports.
* Fixed the wheel silently dropping runtime data files (mesh shaders,
  Font Awesome SVGs, compass assets, the Nerd Font TTF, REUSE sidecars),
  which broke non-editable installs.
* Repaired mojibake characters in ``mesh.py`` and ``manim_directive.py``.
* Fixed CI authentication and incremental seeding for the docs-cache
  workflow, and made tests skip gracefully when optional extras
  (``sklearn``, the ``manim-mobject-svg`` plugin on Python 3.13+) are
  absent.
* Fixed the gearbox module failing to import due to an incorrect
  ``Renderer`` type annotation on the radius parameter of
  :func:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.involute_func`
  and related functions.
* Fixed missing closing parentheses in four docstring manim example
  blocks (MCMCAxes, MultiPendulum, GMAnimationBuilder, VMobjectInt)
  that caused the docs-cache render workflow to fail.
* Fixed misplaced type annotations that caused ``NameError`` in five
  files (algorithm/array.py, chemistry/utils/utils.py,
  chemistry/manim_chemistry_molecule/mc_atom.py,
  chemistry/twoD/molecule.py, circuit/mobjects.py).

v1.0.4
------

**Added**

* Added ``ArcInt`` to the Basic geometry module
  and its documentation in ``geometry.rst`` for computing arc-arc intersections.
* Added ``reuse-lint`` and ``flake8-unused-imports`` jobs to the GitHub Actions
  workflow for license compliance and unused import detection.
* Added custom Sphinx extension ``inheritance_colors`` that color-codes
  inheritance diagram nodes by module origin — Manim nodes in green
  (#87C2A5), Manim Extensions nodes in teal (#4DB8D4), with dark
  foreground (#1E1E2E) for both, and uncolored Python nodes in gray —
  with a dynamic legend auto-generated above each diagram.
* Added legend display above inheritance diagrams with color swatches for
  Manim, Manim Extensions, and Python (auto-detected when third-party
  nodes appear in a diagram).

**Changed**

* Replaced all ``YELLOW`` color references with ``PURE_YELLOW`` (#FFFF00)
  across the entire codebase (58 occurrences, 20 files), matching the original
  bright yellow that Manim's ``YELLOW`` constant used to represent.
* Simplified :class:`~manim_extensions.mobjects.ExtendedLine` by removing the
  ``**kwargs`` parameter — the class now automatically copies the source line's
  style via ``match_style()``; updated the docstring to document this behavior.
* Removed all ``.. inheritance-diagram::`` directives from ``mobjects.py``
  docstrings (previously present for 11 classes).
* Updated documentation logo size to 208px width (matching Manim Community docs).
* Updated documentation: added per-module index pages with individual ``:doc:``
  links in the main index (matching the :class:`~manim_extensions.compass.compass.compass.Compass` style), added inheritance
  diagrams for all bundled modules, and removed references to the deleted
  ``third_party/`` directory and Git submodules.
* Updated Python version requirement to ``>=3.11`` across ``pyproject.toml``,
  GitHub Actions workflow, and documentation.
* Added comprehensive parameter documentation (``Parameters`` sections) to
  all public classes across ``algorithm``, ``circuit``, compass, ``meshes``,
  mindmap, ``physics``, and ``rubikscube`` modules, documenting every
  ``__init__`` parameter in class-level docstrings.
* Added ``validate.yml`` GitHub Actions workflow with three separate jobs
  (``validate-manim-directives``, ``validate-param-docs``, ``validate-refs``)
  and their corresponding Python validation scripts.
* Removed module-level ``.. manim::`` directive examples from 16 Python files
  (the rendering engine does not display module-level manim examples).
* Converted all absolute ``from manim_extensions.xxx`` imports to relative
  imports across 12 files in ``meshes/`` and ``algorithm/`` subpackages
  (``params.py``, ``templates.py``, ``helpers.py``, ``basic_mesh.py``,
  ``opengl_mesh.py``, ``triangle_mesh.py``, ``mesh.py``, ``voronoi.py``,
  ``divide_and_conquer.py``, ``delaunay_criterion.py``, ``array.py``,
  ``test_numpy_helper.py``) to follow PEP 8 and reduce coupling.
* Added ``package_data`` configuration in ``pyproject.toml`` to ensure
  mesh model data files (``*.ply``, ``*.stl``) are included in
  ``sdist`` and ``wheel`` distributions.
* Added minimum version constraints to all third-party dependencies in
  ``pyproject.toml`` — most importantly ``shapely>=2.0`` (required for
  the new ``from shapely import geometry`` API used in optics),
  plus ``Pillow>=9.0``, ``opencv-python>=4.5``, ``pymunk>=6.0``,
  ``kociemba>=1.2``, ``trimesh>=4.0``, ``scipy>=1.9``,
  and ``moderngl>=5.0``.

**Removed**

* Deleted ``Code``, ``JavaCode``, ``PythonCode``, and ``CppCode`` classes
  from the ``algorithm`` module (unused code block classes).
* Removed the ``index_code_labels`` helper from ``algorithm/utils/debug.py``
  (was only used by the deleted ``Code`` class).

**Fixed**

* Fixed :class:`~manim_extensions.automata.mobjects.manim_transition.ManimTransitionDocExample` displaying a full DFA
  instead of demonstrating a single transition.
* Fixed ``KeyError: 'pop'`` and ``KeyError: 'push'`` in
  :class:`~manim_extensions.automata.mobjects.manim_pushdown_automaton.ManimPushDownAutomaton`
  and :class:`~manim_extensions.automata.mobjects.manim_pushdown_automaton.ManimPushDownAutomatonTransition`
  by adding PDA-specific default templates and defensive ``.get()`` lookups.
* Fixed GitHub Actions workflow paths for ``validate_param_docs.py``
  and ``validate_directives.py`` (added ``workflow/`` prefix).
* Fixed Sphinx cross-references in ``circuit`` and mindmap modules
  (LEFT, DOWN, and :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutDirection.LeftToRight`
  inline code to proper ``:class:``/``:attr:`` cross-references).
* Fixed CI test failures for missing ``xmltodict``, invalid escape sequences
  in TikZ docstrings, and CJK font detection on Linux.
* Fixed ``TypeError`` for ``str | None`` union syntax in Python 3.10–3.13
  environments by adding ``from __future__ import annotations``.
* Fixed ``ArcInt`` division-by-zero error for
  concentric circles by adding a ``d <= 1e-9`` guard.
* Fixed :class:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh`
  ``AttributeError`` by initialising ``triangle_indices`` before ``super().__init__()``.
* Fixed Example Gallery frame overflow and centering for multiple examples
  (``CircuitExample``, ``GearboxExample``, ``NeuralNetworkExample``, etc.)
  by adjusting scales, shifts, and using ``scale_to_fit_width()``.
* Removed gray text / titles from :class:`~manim_extensions.compass.scene.compass_scene.CompassExample`
  and ensured all geometry elements are centered.
* Fixed ``check_redundant_imports.py`` false positives: no longer flags
  explicitly-imported names (e.g. ConvertToOpenGL) when ``from manim import *``
  is absent and those names are not covered by star exports.
* Fixed ``validate_refs.py`` false positives: separated project class map
  (``manim_extensions``) from installed ``manim`` so that manim-internal names
  like ``Code`` no longer trigger inline-code suggestions in changelog/docs.
* Fixed ``flake8-unused-imports`` CI job by correcting the ``--exclude``
  glob pattern (``*__init__.py*``) so that all ``__init__.py`` files are
  properly excluded from the F401 check.
* Added SPDX license header to ``CONTRIBUTING.md`` to restore REUSE 3.3
  compliance.
* Fixed ``pyproject.toml`` TOML parse error on Python 3.13 / pip by replacing
  an invalid tuple (``(...)``) with an array (``[...]``) in the
  ``[tool.flake8]`` section.
* Added ``myst-parser`` to the ``docs`` optional dependencies so ReadTheDocs
  can build the documentation with the included ``CONTRIBUTING.md``.
* Fixed :class:`~manim_extensions.mobjects.FileTree` box-drawing characters
  not connecting on Linux / ReadTheDocs by switching the Linux fallback font
  from ``DejaVu Sans Mono`` to ``JetBrains Mono``, and installing
  ``fonts-jetbrains-mono`` in the ReadTheDocs build environment.
* Fixed ``validate_refs.py`` false positives for filenames like
  ``CONTRIBUTING.md`` by skipping tokens ending in common file extensions
  (``.md``, ``.rst``, ``.py``, etc.).
* Fixed inheritance diagram node colors being overwritten / flashing on
  page load by updating ``responsiveSvg.js`` to preserve custom fill colors
  injected by the ``inheritance_colors`` extension.
* Fixed missing module exports in ``automata/__init__.py`` and
  ``automata/mobjects/__init__.py`` — added
  :class:`~manim_extensions.automata.mobjects.manim_turing_machine.ManimTuringMachine`,
  :class:`~manim_extensions.automata.mobjects.manim_state.ManimState`,
  :class:`~manim_extensions.automata.mobjects.manim_transition.ManimTransition`,
  :class:`~manim_extensions.automata.mobjects.manim_pushdown_automaton_transition.ManimPushDownAutomatonTransition`,
  :class:`~manim_extensions.automata.mobjects.manim_automaton_input.ManimAutomataInput`,
  :class:`~manim_extensions.automata.mobjects.manim_automaton_input.Token`, and
  :class:`~manim_extensions.automata.mobjects.pushdown_automaton_rule.PushDownAutomatonRule`
  to ``__all__`` so they are importable via ``from manim_extensions.automata import ...``.
* Fixed Sphinx "Title underline too short" warnings in
  ``docs/source/reference/automata/mobjects.rst`` by extending underlines
  for :class:`~manim_extensions.automata.mobjects.manim_transition.ManimTransition`,
  :class:`~manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton.ManimdeterministicFiniteAutomaton`,
  and :class:`~manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton.ManimNondeterministicFiniteAutomaton`
  headings.

v1.0.3
------

**Added**

* Added bundled subpackages: ``GearBox``, :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutType.MindMap`, :class:`~manim_extensions.compass.compass.compass.Compass`, ``Algorithm``,
  ``Automata``, :class:`~manim_extensions.circuit.utils.Circuit`, ``Data Structures``, ``Meshes``, ``Neural Network``,
  ``Physics``, ``Rubik's Cube``, ``Sequence Diagram`` and ``TikZ`` from third-party
  Manim extensions.

**Changed**

* Documentation rebuilt with Furo theme, inheritance diagrams and interactive Manim examples matching Manim Community's official docs.

**Fixed**

* Fixed CJK font fallback for :class:`~manim_extensions.mobjects.ChineseMathTex` on Linux/ReadTheDocs.

v1.0.2
------

**Changed**

* Documentation theme switched to Furo, matching Manim Community's official documentation style.

v1.0.1
------

**Fixed**

* Fixed :class:`~manim_extensions.mobjects.LabelDot` center point calculation.

v1.0.0
------

**Added**

* Initial release with mobjects, ``geometry`` and animations modules.
