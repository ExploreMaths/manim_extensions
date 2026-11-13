.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

=======
Testing
=======

Running the tests
-----------------

* Tests live in ``tests/`` and use **pytest**.
* CI requires **>= 90% coverage** (``--cov-fail-under=90``).
* Tests run under ``xvfb-run`` because Manim needs a display.
* The test matrix covers Python 3.11–3.15.

.. code-block:: bash

    xvfb-run -a pytest tests/ -v

Writing a test
--------------

* Name the file after the module it covers (``tests/test_<module>.py``) and keep
  each test focused on one behaviour.
* ``tests/conftest.py`` provides a fresh Manim Scene plus ready-made triangle,
  square and cube fixtures (vertices, faces and :class:`~manim_extensions.meshes.models.data_models.mesh.Mesh` objects) — reuse them
  instead of rebuilding geometry in every test.
* When fixing a bug, add a test that fails on the old code and passes on the
  new one.
* Anything that renders needs the ``xvfb-run`` prefix locally; CI already runs
  inside a virtual display.

.. _validation-checklist:

Validation Checklist
--------------------

Run these locally before opening a PR. The checker scripts are grouped into
five CI jobs in ``.github/workflows/validate.yml`` by what they need installed;
each row below belongs to one of those groups. Run a whole group with
``python workflow/run_checks.py --group <static|package|layout|lint|audit>``.

.. list-table::
   :header-rows: 1

   * - Check
     - Command
   * - Optional extras are non-empty and listed in ``all``
     - ``python workflow/validate_extras.py``
   * - Docstrings (module + function, raw prefix, numpydoc ``Parameters``)
     - ``python workflow/validate_docstrings.py``
   * - ``__init__`` params in class docstring
     - ``python workflow/validate_param_docs.py``
   * - numpydoc sections, order, admonitions, ``Examples`` last, example blocks
     - ``python workflow/validate_doc_sections.py``
   * - RST formatting (blank lines, indentation)
     - ``python workflow/validate_rst.py``
   * - ``.. manim::`` ``:save_last_frame:`` rules
     - ``python workflow/validate_manim_directives.py``
   * - Example sample files declared with ``:files:``
     - ``python workflow/validate_example_files.py``
   * - Blank-line layout in ``.. manim::`` examples
     - ``python workflow/validate_example_spacing.py``
   * - Descriptive example class names without ``Example``
     - ``python workflow/validate_example_names.py``
   * - Example layout (in frame, not too small)
     - ``python workflow/check_example_layout.py``
   * - Cross-references (FQNs, short/ambiguous/unlinked names)
     - ``python workflow/validate_refs.py``
   * - Intersphinx mappings and tilde rules
     - ``python workflow/validate_intersphinx.py``
   * - No ``from manim import *`` outside ``__init__``
     - ``python workflow/check_redundant_imports.py``
   * - Relative in-package imports
     - ``python workflow/check_relative_imports.py``
   * - API coverage
     - ``python workflow/validate_api_coverage.py``
   * - Black formatting
     - ``black --check manim_extensions tests scripts workflow docs``
   * - Unused imports (F401)
     - ``flake8 manim_extensions --select F401 --exclude "*__init__.py*,test,examples"``
   * - Syntax / undefined names (E9, F63, F7, F82)
     - ``flake8 manim_extensions --select E9,F63,F7,F82 --max-line-length=127``
   * - License headers
     - ``python workflow/validate_headers.py``
   * - License declarations (REUSE)
     - ``reuse lint``
   * - Type annotations on all params / no quoted annotations
     - ``python scripts/check_type_annotations.py``
   * - Return annotations on documented public functions with return values
     - ``python scripts/check_return_annotations.py``
   * - Dependencies audit
     - ``pip-audit --desc on``

Several checkers have a ``--fix`` mode for auto-repairable issues:

.. code-block:: bash

    python workflow/validate_docstrings.py --fix        # Args: -> Parameters
    python workflow/check_redundant_imports.py --fix   # star -> explicit imports
    python workflow/check_relative_imports.py --fix     # absolute -> relative imports
    python workflow/validate_headers.py --fix           # merge/normalize SPDX headers
    python workflow/fix_refs.py                         # cross-reference fixes

Vendored subpackages that intentionally deviate from a rule can be exempted via the corresponding ``*_exemptions.json`` file (``doc_section_exemptions.json``, ``param_docs_exemptions.json``, ``example_layout_exemptions.json``).

Continuous integration
----------------------

Four workflows live in ``.github/workflows/``:

.. list-table::
   :header-rows: 1

   * - Workflow
     - Trigger
     - What it does
   * - ``Validate``
     - push to ``main``, pull request
     - Black, flake8, REUSE and every checker in the table above
   * - ``Python package``
     - push to ``main``, pull request
     - builds and tests the package on Python 3.11–3.14
   * - ``Docs cache``
     - push to ``main``, release tag
     - renders the ``.. manim::`` examples and executes the ``.. nbcell::`` cells, then publishes the cache to the ``rtd-cache`` branch
   * - ``Publish``
     - manual dispatch
     - updates the version and changelog badge, builds the sdist and wheel, uploads to PyPI, tags the release
