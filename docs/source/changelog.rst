Changelog
=========

v1.0.4 (Unreleased)
--------------------

**Changed**

* Updated documentation: added per-module index pages with individual ``:doc:``
  links in the main index (matching the ``Compass`` style), added inheritance
  diagrams for all bundled modules, and removed references to the deleted
  ``third_party/`` directory and Git submodules.
* Updated Python version requirement to ``>=3.11`` across ``pyproject.toml``,
  GitHub Actions workflow, and documentation.

**Fixed**

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

* Added bundled subpackages: ``GearBox``, ``MindMap``, ``Compass``, ``Algorithm``,
  ``Automata``, ``Circuit``, ``Data Structures``, ``Meshes``, ``Neural Network``,
  ``Physics``, ``Rubik's Cube``, ``Sequence Diagram`` and ``TikZ`` from third-party
  Manim extensions.

**Changed**

* Documentation rebuilt with Furo theme, inheritance diagrams and interactive Manim examples matching Manim Community's official docs.

**Fixed**

* Fixed CJK font fallback for ``ChineseMathTex`` on Linux/ReadTheDocs.

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

* Fixed ``LabelDot`` center point calculation.

v1.0.0
------

**Full Changelog**: https://github.com/ExploreMaths/manim_extensions/commits/v1.0.0

**View on PyPI**: https://pypi.org/project/manim-extensions/1.0.0/

What's Changed
^^^^^^^^^^^^^^

**Added**

* Initial release with ``mobjects``, ``geometry`` and ``animations`` modules.