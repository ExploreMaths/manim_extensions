Changelog
=========

v1.0.4 (Unreleased)
--------------------

**Changed**

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
  (converted bare ``LEFT``, ``DOWN``, and ``LayoutDirection.LeftToRight``
  inline code to proper ``:class:``/``:attr:`` cross-references).
* Fixed CI test failures for missing ``xmltodict``, invalid escape sequences
  in TikZ docstrings, and CJK font detection on Linux.
* Fixed ``TypeError`` for ``str | None`` union syntax in Python 3.10–3.13
  environments by adding ``from __future__ import annotations``.

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