.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Changelog
=========

v1.0.4 (Unreleased)
--------------------

**Added**

* Added :func:`~manim_extensions.geometry.ArcInt` to the Basic geometry module
  and its documentation in ``geometry.rst`` for computing arc-arc intersections.
* Added ``reuse-lint`` and ``flake8-unused-imports`` jobs to the GitHub Actions
  workflow for license compliance and unused import detection.

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

v1.0.3
------

**Full Changelog**: https://github.com/ExploreMaths/manim_extensions/compare/v1.0.2...v1.0.3

**View on PyPI**: https://pypi.org/project/manim-extensions/1.0.3/

What's Changed
^^^^^^^^^^^^^^

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

**Full Changelog**: https://github.com/ExploreMaths/manim_extensions/compare/v1.0.1...v1.0.2

**View on PyPI**: https://pypi.org/project/manim-extensions/1.0.2/

What's Changed
^^^^^^^^^^^^^^

**Changed**

* Documentation theme switched to Furo, matching Manim Community's official documentation style.

v1.0.1
------

**Full Changelog**: https://github.com/ExploreMaths/manim_extensions/compare/v1.0.0...v1.0.1

**View on PyPI**: https://pypi.org/project/manim-extensions/1.0.1/

What's Changed
^^^^^^^^^^^^^^

**Fixed**

* Fixed :class:`~manim_extensions.mobjects.LabelDot` center point calculation.

v1.0.0
------

**Full Changelog**: https://github.com/ExploreMaths/manim_extensions/commits/v1.0.0

**View on PyPI**: https://pypi.org/project/manim-extensions/1.0.0/

What's Changed
^^^^^^^^^^^^^^

**Added**

* Initial release with ``mobjects``, ``geometry`` and ``animations`` modules.