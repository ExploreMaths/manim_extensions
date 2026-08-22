.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Changelog
=========

v1.0.4
------

**Added**

* Added :func:`~manim_extensions.geometry.ArcInt` to the Basic geometry module
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
  all public classes across ``algorithm``, ``circuit``, ``compass``, ``meshes``,
  ``mindmap``, ``physics``, and ``rubikscube`` modules, documenting every
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
* Fixed Sphinx cross-references in ``circuit`` and ``mindmap`` modules
  (:attr:`~manim.constants.LEFT`, :attr:`~manim.constants.DOWN`, and :attr:`~manim_extensions.mindmap.algorithms.layout_config.LayoutDirection.LeftToRight`
  inline code to proper ``:class:``/``:attr:`` cross-references).
* Fixed CI test failures for missing ``xmltodict``, invalid escape sequences
  in TikZ docstrings, and CJK font detection on Linux.
* Fixed ``TypeError`` for ``str | None`` union syntax in Python 3.10–3.13
  environments by adding ``from __future__ import annotations``.
* Fixed :func:`~manim_extensions.geometry.ArcInt` division-by-zero error for
  concentric circles by adding a ``d <= 1e-9`` guard.
* Fixed :class:`~manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh`
  ``AttributeError`` by initialising ``triangle_indices`` before ``super().__init__()``.
* Fixed Example Gallery frame overflow and centering for multiple examples
  (``CircuitExample``, ``GearboxExample``, ``NeuralNetworkExample``, etc.)
  by adjusting scales, shifts, and using ``scale_to_fit_width()``.
* Removed gray text / titles from :class:`~manim_extensions.compass.scene.compass_scene.CompassExample`
  and ensured all geometry elements are centered.
* Fixed ``check_redundant_imports.py`` false positives: no longer flags
  explicitly-imported names (e.g. ``ConvertToOpenGL``) when ``from manim import *``
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
  :class:`~manim_extensions.automata.mobjects.token.Token`, and
  :class:`~manim_extensions.automata.mobjects.pushdown_automaton_rule.PushDownAutomatonRule`
  to ``__all__`` so they are importable via ``from manim_extensions.automata import ...``.
* Fixed Sphinx "Title underline too short" warnings in
  ``docs/source/reference/automata/mobjects.rst`` by extending underlines
  for :class:`~manim_extensions.automata.mobjects.manim_transition.ManimTransition`,
  :class:`~manim_extensions.automata.mobjects.manim_deterministic_finite_automaton.ManimdeterministicFiniteAutomaton`,
  and :class:`~manim_extensions.automata.mobjects.manim_nondeterministic_finite_automaton.ManimNondeterministicFiniteAutomaton`
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

* Initial release with ``mobjects``, ``geometry`` and ``animations`` modules.