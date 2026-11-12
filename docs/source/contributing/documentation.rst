.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

=============
Documentation
=============

Reference pages under ``docs/source/reference/`` are generated from docstrings,
so most of the writing happens in Python rather than in ``.rst`` files. The
conventions below apply to both places.

Building the documentation
--------------------------

Install the documentation extra and build with the bundled Makefile:

.. code-block:: bash

    pip install -e ".[docs]"
    cd docs
    make html          # macOS / Linux; use make.bat html on Windows

The generated site lands in ``docs/build/html``. A first build imports every
module through autodoc and renders the examples that are not present in the
CI media cache, so expect it to take a while; later builds only redo what
changed.

RST Formatting
--------------

RST is used both in ``.rst`` files under ``docs/source/`` and inside Python docstrings. The ``validate_rst.py`` checker enforces two things:

Blank lines before block elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every block-level element (bullet list, enumeration, directive, line block, field list, transition, table) must be separated from the preceding paragraph by a **blank line**. Without it, docutils silently renders the list as prose.

Indentation
~~~~~~~~~~~

* Normal directive body (``note``, ``warning``, ``admonition``, ...): **+3** spaces relative to the directive.
* Code-producing directives (``code-block``, ``raw``, ``math``): first body line **+4**; subsequent lines are code and not checked.
* Manim-like directives (``manim``, ``nbcell``): first body line **+3**.
* Literal block after ``::``: first line **+4**.
* List-item continuation: aligned with the text after the marker.
* Definition-list descriptions (numpydoc ``name : type`` descriptions): **+4**.

For intentional non-standard layouts (ASCII art, etc.) use either ``:skip-indent:`` as a directive option or a ``.. rst-check: skip-indent`` comment directive immediately before the block.

Manim Examples (``.. manim::``)
-------------------------------

The ``.. manim::`` directive renders a live example in the docs. The ``validate_manim_directives.py`` checker enforces the ``:save_last_frame:`` usage rules:

.. list-table::
   :header-rows: 1

   * - Scene type
     - Rule
   * - **Static** (no ``self.play``, ``self.animate``, etc.)
     - **MUST** have ``:save_last_frame:``
   * - **Animated** (has ``self.play`` / ``self.animate``)
     - **MUST NOT** have ``:save_last_frame:``
   * - Static with ``:save_last_frame:``
     - Must **not** use ``self.wait()`` (redundant)

Sample files read by an example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every executable example that reads a file — both ``.. manim::`` and ``.. nbcell::`` — **MUST** declare it with the ``:files:`` option and use the bare file name in the code:

.. code-block:: rst

   .. manim:: MoleculeScene
      :files: morphine_2d.mol

      molecule = MMoleculeObject.molecule_from_file("morphine_2d.mol")

.. code-block:: rst

   .. nbcell::
      :files: acetone_2d.mol

      molecule = GraphMolecule.molecule_from_file("acetone_2d.mol")

Rules:

* File names are resolved inside the repository's ``examples/`` tree and copied into the example's working directory, so the code only needs the bare name. Each file is listed as a card under the block, and its contents take part in the media cache hash — editing a sample file re-renders the example.
* Never build a path in example code: no ``"examples/..."``, ``"../examples/..."``, ``"_static/..."`` and no ``Path(__file__)``. Those break as soon as the working directory changes.
* Files the example writes itself (``to_csv``, ``imsave``, ``savefig``, ``open(..., "w")``) are generated at run time, need no ``:files:`` entry and are not sample files.
* Keep new samples inside ``examples/``; the download card links to the file on the ``main`` branch.
* ``workflow/validate_example_files.py`` enforces all of the above in CI and reports ``missing-files``, ``path-instead-of-files``, ``undeclared-file`` and ``unknown-asset``.

Example layout
~~~~~~~~~~~~~~

``check_example_layout.py`` runs every example with ``skip_animations=True`` and checks:

* **OUT_OF_FRAME**: content must not extend beyond the frame by more than 5% of the frame size on any side.
* **TOO_SMALL**: content must cover at least 25% of the frame in both dimensions.

Exceptions for intentional cases can be added to ``workflow/example_layout_exemptions.json``.

Cross-References
----------------

Docstrings and ``.rst`` files use Sphinx cross-reference roles to link to other APIs. The conventions below are advisory except where they name a checker: the tilde rules and intersphinx mappings are enforced by ``validate_intersphinx.py``, and short, ambiguous or unlinked names by ``validate_refs.py``. The rest are cleaned up by the maintainers on merge.

* **Module-prefixed targets use a leading** ``~``. Every cross-reference to a fully-qualified object — whether in this project (``manim``, ``manim_extensions``) or a third-party API (``scipy``, ``numpy``, ``pymunk``, ``sklearn``, ...) — is written with a leading ``~`` so Sphinx shows only the last component while the link stays fully qualified:

  .. code-block:: rst

      :meth:`~manim.mobject.mobject.Mobject.scale`
      :class:`~manim_extensions.table.table.Table`

Short targets such as ``__mob_index`` or the short name ``scale`` are best
avoided (``validate_refs.py`` flags them).

* **Python builtins are written bare.** A single-identifier target with no module prefix (e.g. the builtin exception ``NotImplementedError``) gets no ``~``: it has no prefix to abbreviate, and the python intersphinx inventory registers builtins by their bare name, so a ``~`` in front of the target resolves to nothing. Write the role without the tilde instead. The ``validate_intersphinx.py`` checker enforces both tilde rules in CI (``validate-intersphinx``).

* **API names should be cross-references, not inline code.** Back-ticked names that look like APIs (e.g. ``add_row``) are better written as proper roles. Built-in types (``int``, ``str``, ``list``, ...) and common exceptions are exempt.

* **Broken references should be avoided.** A ``~package.module.Class.attr`` target whose module cannot be imported or whose class does not exist fails the check — prefer double-checking the target resolves.

* **External-library references need an intersphinx mapping.** A ``scipy.spatial.Voronoi``-style reference to a third-party package only becomes a link when that package is registered in ``intersphinx_mapping`` in ``docs/source/conf.py``. A reference to an unmapped external package renders as plain text with no link — a silent defect. When you reference an API from an external library that is not yet mapped, add it to ``intersphinx_mapping`` (base URL of the library's docs; ``None`` lets Sphinx auto-detect ``objects.inv``). The ``validate_intersphinx.py`` checker (enforced in CI as ``validate-intersphinx``) reports any explicit reference whose top-level package is neither part of this project, a mapped intersphinx library, nor a Python standard-library module.

  Currently mapped external libraries: ``python``, ``numpy``, ``manim``, ``pillow``, ``pymunk``, ``scikit-learn``, ``scipy``, ``segno``, ``typing_extensions``. Note the ``scikit-learn`` mapping key corresponds to the ``sklearn`` import name.

* **Ambiguous names shouldn't appear bare.** If a back-ticked name matches several project classes (e.g. the class *Gear* exists both as ``manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear`` and ``manim_extensions.pymunk.custom_mobjects.gear.Gear``), the docs extension cannot auto-link it — it stays a plain code span and the reader cannot tell which object is meant. Where convenient, disambiguate by writing an explicit role with the full module path:

  .. code-block:: rst

      :class:`~manim_extensions.gearbox.gear_mobjects.gear_mobject.Gear`

  ``validate_refs.py`` reports bare back-ticked ambiguous class names, and the Sphinx build emits an ``ambiguous inline-code class name`` warning for ambiguous data/function names. Same-name classes *are* allowed in the codebase; references to them just need to be explicit, and the maintainers will fix any that slip through.

* **Classes mentioned in prose are cross-references.** A class name written as a plain word (including its plural, e.g. ``MCAtoms``) leaves the reader with no link. Write it as a ``:class:`` role instead:

  .. code-block:: rst

      :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom`

  ``validate_refs.py`` reports these as ``unlinked-class``. Every spelling counts, including names that are also ordinary English words. Code samples, directives, section titles, doctests and back-ticked inline code are skipped, since those are code or already handled by the inline-code check. A plural noun puts an escaped space between the role and the ``s``, since a closing backtick may not be followed directly by a letter:

  .. code-block:: rst

      :class:`~manim_extensions.rubikscube.cubie.Cubie`\ s

  The escaped space disappears when rendered, so the page reads *Cubies* with the link on *Cubie*. In a docstring the containing literal must be raw (``r"""``) so Python keeps the backslash, and converting one means collapsing any doubled backslash to a single one.

  When the word really is an ordinary English word and not the class (``Array of shape (4, 3)``, a ``Source:`` citation, ``Ground-truth``), say so with a comment instead of forcing a link. The comment accepts a comma-separated list, and it covers **only the paragraph that follows it** — every other paragraph in the same file still needs a real cross-reference:

  .. code-block:: rst

      .. unlinked-class-ok Array, Arrays

      Arrays of shape (4, 3) hold the control points.

  A page where every mention of a word is the plain noun can opt out of the whole file by adding the ``-file`` suffix to the marker (same comma-separated list, see the code block above). The same two lines work inside a docstring; in a ``.py`` file the ``#`` comment form with the same list is the equivalent file-wide marker.

You can run ``python workflow/fix_refs.py`` to auto-fix fixable issues if you like.

API Documentation Coverage
--------------------------

Every **public** name (class, function, constant) exported by the package must appear in the documentation under ``docs/source/reference/``. This is enforced by ``validate_api_coverage.py``.

The docs use a custom ``.. autoall::`` directive that automatically expands into autodoc directives for all public names of a module. When adding a new public module or name, make sure it is reachable from an ``autoall`` block (or an explicit ``autoclass`` / ``autofunction`` / ``autodata``).

After adding new public names, refresh the coverage snapshot:

.. code-block:: bash

    python workflow/validate_api_coverage.py --write-snapshot

The public-name rules:

* A module defines ``__all__`` → those are the public names.
* No ``__all__`` → names defined at module level (not imported) that do not start with ``_``.
