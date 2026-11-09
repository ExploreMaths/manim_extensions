.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

==========
Code style
==========

The tree is formatted with Black and type-checked convention by convention;
the checks in ``validate.yml`` and the docstring validators reject anything that
departs from the rules below.

Formatting and line length
--------------------------

* Follow **PEP 8**. Code is formatted with **Black** (line length **88**), configured under ``[tool.black]`` in ``pyproject.toml``.
* **The whole tree is Black-clean and CI enforces it.** The vendored modules were reformatted together with everything else, so ``manim_extensions``, ``tests``, ``scripts``, ``workflow`` and ``docs`` are checked as a whole by the ``black`` job in ``validate.yml``. Do not add ``# fmt: off`` to keep an upstream file byte-identical — a vendored module reformatted here is accepted, and a later upstream merge is resolved by re-running Black on the merged file rather than by preserving its original spacing.
* **Enable the pre-commit hook once per clone** so Black runs on staged files and the result lands in the same commit, with no follow-up "style" commit:

  .. code-block:: bash

      git config core.hooksPath .githooks

  The hook needs Black on your interpreter (``python3 -m pip install black``); without it the hook warns and lets the commit through, and CI still catches the file. ``git commit --no-verify`` bypasses the hook for one commit.
* flake8 enforces ``E9,F63,F7,F82`` (syntax / undefined names) as hard failures and runs a non-fatal complexity check at ``--max-line-length=127``.

Type annotations
----------------

* **Every function and method parameter must have a type annotation**, except ``self``, ``cls``, ``*args``, and ``**kwargs``.
* **Never write an annotation as a string literal** (``node: "Node"``, ``-> "Option"``). Import the name instead, or, for a genuine forward reference to a class defined later in the same module, add ``from __future__ import annotations`` at the top of the module. ``scripts/check_type_annotations.py`` rejects quoted annotations; ``Literal["a", "b"]`` payloads are string values, not annotations, and are allowed.
* **A parameter or return value that only accepts a closed set of string values must be annotated with** ``typing.Literal[...]``, not ``str``. A closed set means the implementation branches on the value (``if x == "up"``, a dispatch dict keyed by it) or the docstring enumerates every accepted spelling. Import ``Literal`` from ``typing`` and keep it inline at the signature when it fits within 88 columns; when it does not, or the same set is repeated across several signatures, define one module-level alias and reuse it. A ``Literal`` set must match the runtime validation exactly — adding an accepted value means updating the annotation, the docstring, and the ``Literal`` in the same commit.

  .. code-block:: python

      def get_face(self, face: Literal["U", "D", "F", "B", "L", "R"]) -> np.ndarray: ...
      def create_decision_tree(self, traversal_order: Literal["bfs", "level", "best"] = "bfs") -> None: ...

  Values that are genuinely open-ended stay ``str``: file paths, labels and titles, TeX payloads, colour hex strings, and free-form identifiers. Existing ``str`` annotations for closed sets are technical debt; fix them when you touch that signature rather than rewriting a whole module in one pass.
* Return annotations are strongly encouraged where practical. A CI check (``scripts/check_return_annotations.py``) runs as a signal for functions that return a value without an annotation — add one when it points you there, and the maintainer will help refine imperfect annotations. **A class method that returns an instance of its own class must annotate it with** ``Self`` (``from typing import Self``), not with a quoted forward reference such as ``-> "ClassName"``. ``Self`` is available since Python 3.11 and is the canonical spelling; a string annotation would either require ``from __future__ import annotations`` to drop or break at runtime.
* **Functions with no return value must not write a** ``-> None`` return annotation and must not add a ``Returns`` docstring section. ``sphinx-autodoc-typehints`` renders a redundant ``RETURN TYPE: None`` whenever a signature ends in ``-> None``; omitting the annotation suppresses it.
* A non-``None`` return annotation requires a ``Returns`` (or ``Yields``) docstring section (see the Docstrings section below).
* ``mypy --strict`` is configured in ``pyproject.toml`` for local type checking,
  but it is **not currently enforced in CI**, and the codebase does not pass
  it (mostly ``type-arg`` / ``no-untyped-def`` noise in vendored modules). Run
  it locally as advisory only.

Imports
-------

Two hard rules, both enforced by dedicated checkers:

1. **No star imports from** ``manim`` outside ``__init__.py``. ``from manim import *`` (and ``from manim.<sub> import *``) is only allowed in ``__init__.py`` files that re-export names. Everywhere else use explicit imports:

   .. code-block:: python

       from manim import Circle, FadeIn, VGroup   # ✓
       from manim import *                         # ✗ (only in __init__.py)

Run ``python workflow/check_redundant_imports.py --fix`` to convert existing star imports automatically.

2. **In-package imports must be relative.** Any import that targets a module inside ``manim_extensions`` must use relative import syntax. This includes vendored subpackages that still import under their upstream names (``manim_chemistry``, ``manim_ml``, ``manim_pymunk``, ``manim_arabic``).

   .. code-block:: python

       from ..utils.deprecation import deprecated   # ✓
       from manim_extensions.utils.deprecation import deprecated  # ✗

Run ``python workflow/check_relative_imports.py --fix`` to convert automatically (some plain ``import`` statements need manual review).

* flake8 also checks for **unused imports** (``F401``) in CI.

Naming
------

* Modules: ``snake_case``
* Classes: ``PascalCase``
* Functions, methods, variables: ``snake_case``
* Constants: ``UPPER_SNAKE_CASE``
* Private names start with a single underscore (``_``).

Docstrings
----------

Docstrings use the **numpydoc** style. The project enforces this with several AST-based validators, so the rules below are not optional.

Module docstrings
~~~~~~~~~~~~~~~~~

Every ``.py`` file must have a module docstring immediately after any SPDX license header (and before any import). The docstring must open with ``"""`` or ``r"""``.

Required docstrings
~~~~~~~~~~~~~~~~~~~

Every **public** function, method, and class must have a docstring. This includes ``__init__`` (it is not exempt). The following dunder methods are exempt: ``__repr__``, ``__str__``, ``__len__``, ``__getitem__``, ``__setitem__``, ``__call__``, ``__eq__``, ``__hash__``, ``__enter__``, ``__exit__``, and the rest of the standard dunder set. Inner functions like ``wrapper`` are also exempt.

numpydoc section format
~~~~~~~~~~~~~~~~~~~~~~~

Sections use a bare header line followed by a ``----------`` underline. **Google-style inline headers like** ``Args:`` or ``Returns:`` are rejected — use ``Parameters`` and ``Returns`` instead.

Spacing is enforced too: a section header must be **separated from the preceding paragraph by a blank line**, and the entry list must **directly follow the underline** (a blank line between the underline and the first entry is rejected). A header that is flush against the summary is absorbed into the summary paragraph by napoleon, and sphinx-autodoc-typehints then injects ``:type:`` lines into that paragraph so docutils renders raw reST text in the reference pages. ``validate_doc_sections.py`` rejects both mistakes (``SECTION_MISSING_BLANK_BEFORE``, ``SECTION_BLANK_AFTER_UNDERLINE``).

.. code-block:: python

    def scale(self, factor: float, about_point: np.ndarray | None = None) -> "Mobject":
        """Scale the mobject by *factor*.
    
        Parameters
        ----------
        factor
            The scaling factor.
        about_point
            The point to scale about. If ``None``, the origin is used.
    
        Returns
        -------
            The scaled mobject.
    
        Raises
        ------
        ValueError
            If *factor* is zero.
    
        Examples
        --------
        .. manim:: ScaleExample
    
            class ScaleExample(Scene):
                def construct(self):
                    ...
        """

Required sections
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Condition
     - Required section
   * - Function/method has parameters (except bare ``*args``)
     - ``Parameters``
   * - Return annotation is not ``None``
     - ``Returns`` or ``Yields``
   * - Function is a generator (``yield``)
     - ``Yields``
   * - Function raises an exception directly
     - ``Raises``

Every parameter listed in the signature must have a corresponding entry in the ``Parameters`` section.

``__init__`` parameters go in the **class** docstring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Constructor parameters are documented in the **class** docstring, **not** in ``__init__``. The ``__init__`` docstring should only be a brief description. This is enforced by ``validate_param_docs.py``.

.. code-block:: python

    class Circle(VGroup):
        """A circle mobject.
    
        Parameters
        ----------
        radius
            The radius of the circle.
        color
            The stroke color.
        """
    
        def __init__(self, radius: float = 1.0, color: str = WHITE):
            """Create a circle."""
            ...

Section order
~~~~~~~~~~~~~

When multiple sections are present they must follow numpydoc's canonical order:

``Parameters`` → ``Other Parameters`` → ``Attributes`` / ``Methods`` → ``Returns`` / ``Yields`` / ``Receives`` → ``Raises`` → ``Warns`` → ``References`` → ``Examples``

Advisory blocks use admonitions, not sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Note`` / ``Notes``, ``See Also``, ``Warning`` / ``Warnings``, ``Tip`` / ``Tips``, ``Important``, ``Caution``, and ``Danger`` must **not** be written as numpydoc section headers. Write them as reST admonition blocks — ``.. note::``, ``.. seealso::``, ``.. warning::``, ``.. tip::``, ``.. important::``, ``.. caution::``, ``.. danger::`` — and place them **before** ``Examples``:

.. code-block:: python

    .. note::
    
        The compensation is exact for flat content lying in the plane of the camera.

``Examples`` must be the last section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Examples`` is always the final section of a docstring. No numpydoc section header and no top-level admonition block may follow it; advisory blocks belong before ``Examples``. ``validate_doc_sections.py`` rejects both mistakes (``ADVISORY_SECTION_HEADER``, ``EXAMPLES_NOT_LAST``).

Types come from the signature, not the docstring
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sphinx-autodoc-typehints`` (with ``autodoc_typehints = "description"``) injects every parameter, attribute and return type from the code signature into the rendered reference page. Docstrings must **not** hand-write a type anywhere — neither in ``Parameters`` nor in ``Returns``/``Yields``. A handwritten type would render twice (once handwritten, once injected) and, worse, drift out of sync with the signature (e.g. a stale ``Any`` left behind after an annotation was tightened). Write plain ``name`` entries in ``Parameters`` and a bare description under ``Returns``:

.. code-block:: python

    Parameters
    ----------
    factor
        The scaling factor.

.. code-block:: python

    Returns
    -------
        The scaled mobject.

For ``Returns``, put the description **indented one level deeper** than the ``Returns`` header (the same ``+4``-style indent used for parameter descriptions). The indented description is required so napoleon parses it as the return description rather than absorbing it into the header.

This is enforced by ``validate_doc_sections.py`` (``MANUAL_TYPE_ANNOTATION``).

Docstring closing triple-quote indentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The closing ``"""`` of a docstring must be **indented to the same level as the opening triple-quote** (i.e. the indentation of the docstring body). A closing quote left flush at column 0 — typically the last line of a docstring that ends in a code block — is a defect. This is enforced by ``validate_doc_sections.py``.

Entry description style
~~~~~~~~~~~~~~~~~~~~~~~

* Parameter / return / raises / attribute entry **descriptions must start with a capital letter and end with a period** (or ``?``, ``!``). Descriptions that start with inline literals, cross-reference roles, or type placeholders are exempt from the capital-letter rule.
* Descriptions must be **indented deeper** than their entry line (``name : type``). Flat descriptions at the same indentation break napoleon's parsing.

Terminal punctuation
~~~~~~~~~~~~~~~~~~~~

* The **summary line** (first paragraph) must end with terminal punctuation (``.``, ``?``, ``!``, or equivalent).
* The **last content line** of the docstring must end with terminal punctuation. URLs, formula lines, doctest prompts (``>>>``, ``...``), and ``TODO`` placeholders are exempt.

No default-value descriptions in docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Do not describe parameter/attribute **default values** in the docstring. Default values already appear in the rendered signature (injected by ``sphinx-autodoc-typehints``), so any repetition such as ``Defaults to X``, ``by default X``, ``(default X)``, ``defaults to X``, ``Default is X``, ``By default X``, or ``(the default)`` is redundant and must be omitted. Write plain descriptions that state what the parameter *means*, not what it defaults to. (Ordinary uses of the word "default" that are not default-value descriptions — e.g. "the default colour", "reset to its default appearance", "the default DVI path", ``get_param_or_default`` — are fine to keep.)

Raw docstrings for example code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a docstring embeds example code whose string literals contain ``\n`` escapes (e.g. MOL/SDF file blocks), the docstring **must** use an ``r"""`` raw prefix. Without it, Python interprets the escapes and Sphinx renders mangled, unrunnable code.

Interactive examples use ``.. nbcell::``, not doctest prompts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An interactive example (code the reader is meant to run and see output for) must be written as a ``.. nbcell::`` block — the notebook-style cell directive — **not** as ``>>>`` / ``...`` doctest prompts. ``nbcell`` renders ``In [n]:`` / ``Out[n]:`` prompts with input/output areas styled by ``nbcell.css``, keeps an optional ``:output:`` verbatim, and works both in ``.rst`` files and inside docstrings. ``>>>`` prompts in a docstring render as a plain code block, which the docs treat as a defect (no cell chrome, no output area).

Mobject subclasses need a ``.. manim::`` example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every class that subclasses a Manim mobject (``Mobject``, ``VMobject``, ``VGroup``, ``Line``, ``Circle``, ``Text``, ...) must include a ``.. manim::`` example block in its **class docstring**. Pure ``Enum``/``ABC`` classes and non-mobject helpers are exempt.

``.. manim::`` blocks must live under ``Examples``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any ``.. manim::`` block must appear under a numpydoc ``Examples`` section header. A manim block in the summary or in another section is rejected.
