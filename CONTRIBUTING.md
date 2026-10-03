<!--
SPDX-FileCopyrightText: 2026 ExploreMaths
SPDX-License-Identifier: MIT
-->

# Contributing

Contributions are welcome! Please open issues or pull requests on the [GitHub repository](https://github.com/ExploreMaths/manim_extensions).

This document describes the conventions enforced by the project. Every rule listed here is checked by an automated script in CI (see the [Validation Checklist](#validation-checklist) at the bottom), so make sure to run the relevant checks locally before opening a pull request.

## Table of Contents

- [Getting Started](#getting-started)
- [Code Style](#code-style)
- [Docstrings](#docstrings)
- [RST Formatting](#rst-formatting)
- [Manim Examples (`.. manim::`)](#manim-examples--manim)
- [Cross-References](#cross-references)
- [API Documentation Coverage](#api-documentation-coverage)
- [Licensing & REUSE](#licensing--reuse)
- [Testing](#testing)
- [Validation Checklist](#validation-checklist)
- [Pull Request Guidelines](#pull-request-guidelines)

---

## Getting Started

### 1. Fork and clone

```bash
git clone https://github.com/<your-username>/manim_extensions.git
cd manim_extensions
git checkout -b feature/my-feature
```

### 2. Install system dependencies

Manim (and therefore this package) needs Pango and Cairo:

```bash
# Debian / Ubuntu
sudo apt-get install -y libpango1.0-dev libcairo2-dev libgirepository1.0-dev pkg-config
```

For running examples and tests you also need LaTeX, ffmpeg, and an X display:

```bash
sudo apt-get install -y texlive-latex-base texlive-latex-extra \
  texlive-fonts-recommended dvisvgm texlive-xetex \
  ffmpeg xvfb
```

### 3. Install the package in editable mode

```bash
pip install --upgrade pip
pip install -e ".[dev,all]"        # dev tools + every optional extra
# or, for a lighter install:
pip install -e ".[dev]"             # only the tools + core deps
```

The package requires **Python >= 3.11** and **manim >= 0.21.0**.

### 4. Run the tests

```bash
pytest tests/ -v
```

---

## Code Style

### Formatting and line length

- Follow **PEP 8**. Code is formatted with **Black** (line length **88**).
- flake8 enforces `E9,F63,F7,F82` (syntax / undefined names) as hard failures and runs a non-fatal complexity check at `--max-line-length=127`.

### Type annotations

- **Every function and method parameter must have a type annotation**, except `self`, `cls`, `*args`, and `**kwargs`.
- Return annotations are strongly encouraged; a non-`None` return annotation requires a `Returns` (or `Yields`) docstring section (see [Docstrings](#docstrings)).
- `mypy --strict` is configured in `pyproject.toml` for local type checking,
  but it is **not currently enforced in CI**, and the codebase does not pass
  it (mostly `type-arg` / `no-untyped-def` noise in vendored modules). Run
  it locally as advisory only.

### Imports

Two hard rules, both enforced by dedicated checkers:

1. **No star imports from `manim` outside `__init__.py`.** `from manim import *` (and `from manim.<sub> import *`) is only allowed in `__init__.py` files that re-export names. Everywhere else use explicit imports:

   ```python
   from manim import Circle, FadeIn, VGroup   # ✓
   from manim import *                         # ✗ (only in __init__.py)
   ```

Run `python workflow/check_redundant_imports.py --fix` to convert existing star imports automatically.

2. **In-package imports must be relative.** Any import that targets a module inside `manim_extensions` must use relative import syntax. This includes vendored subpackages that still import under their upstream names (`manim_chemistry`, `manim_ml`, `manim_pymunk`, `manim_arabic`).

   ```python
   from ..utils.deprecation import deprecated   # ✓
   from manim_extensions.utils.deprecation import deprecated  # ✗
   ```

Run `python workflow/check_relative_imports.py --fix` to convert automatically (some plain `import` statements need manual review).

- flake8 also checks for **unused imports** (`F401`) in CI.

### Naming

- Modules: `snake_case`
- Classes: `PascalCase`
- Functions, methods, variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private names start with a single underscore (`_`).

---

## Docstrings

Docstrings use the **numpydoc** style. The project enforces this with several AST-based validators, so the rules below are not optional.

### Module docstrings

Every `.py` file must have a module docstring immediately after any SPDX license header (and before any import). The docstring must open with `"""` or `r"""`.

### Required docstrings

Every **public** function, method, and class must have a docstring. This includes `__init__` (it is not exempt). The following dunder methods are exempt: `__repr__`, `__str__`, `__len__`, `__getitem__`, `__setitem__`, `__call__`, `__eq__`, `__hash__`, `__enter__`, `__exit__`, and the rest of the standard dunder set. Inner functions like `wrapper` are also exempt.

### numpydoc section format

Sections use a bare header line followed by a `----------` underline. **Google-style inline headers like `Args:` or `Returns:` are rejected** — use `Parameters` and `Returns` instead.

```python
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
    Mobject
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
```

### Required sections

| Condition | Required section |
|-----------|------------------|
| Function/method has parameters (except bare `*args`) | `Parameters` |
| Return annotation is not `None` | `Returns` or `Yields` |
| Function is a generator (`yield`) | `Yields` |
| Function raises an exception directly | `Raises` |

Every parameter listed in the signature must have a corresponding entry in the `Parameters` section.

### `__init__` parameters go in the **class** docstring

Constructor parameters are documented in the **class** docstring, **not** in `__init__`. The `__init__` docstring should only be a brief description. This is enforced by `validate_param_docs.py`.

```python
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
```

### Section order

When multiple sections are present they must follow numpydoc's canonical order:

`Parameters` → `Other Parameters` → `Attributes` / `Methods` → `Returns` / `Yields` / `Receives` → `Raises` → `Warns` → `See Also` / `Notes` / `References` → `Examples`

### Entry description style

- Parameter / return / raises / attribute entry **descriptions must start with a capital letter and end with a period** (or `?`, `!`). Descriptions that start with inline literals (`` `` `` ``), cross-reference roles (`:class:`, `:func:`, ...), or type placeholders are exempt from the capital-letter rule.
- Descriptions must be **indented deeper** than their entry line (`name : type`). Flat descriptions at the same indentation break napoleon's parsing.

### Terminal punctuation

- The **summary line** (first paragraph) must end with terminal punctuation (`.`, `?`, `!`, or equivalent).
- The **last content line** of the docstring must end with terminal punctuation. URLs, formula lines, doctest prompts (`>>>`, `...`), and `TODO` placeholders are exempt.

### Raw docstrings for example code

If a docstring embeds example code whose string literals contain `\n` escapes (e.g. MOL/SDF file blocks), the docstring **must** use an `r"""` raw prefix. Without it, Python interprets the escapes and Sphinx renders mangled, unrunnable code.

### Mobject subclasses need a `.. manim::` example

Every class that subclasses a Manim mobject (`Mobject`, `VMobject`, `VGroup`, `Line`, `Circle`, `Text`, ...) must include a `.. manim::` example block in its **class docstring**. Pure `Enum`/`ABC` classes and non-mobject helpers are exempt.

### `.. manim::` blocks must live under `Examples`

Any `.. manim::` block must appear under a numpydoc `Examples` section header. A manim block in the summary or in another section is rejected.

---

## RST Formatting

RST is used both in `.rst` files under `docs/source/` and inside Python docstrings. The `validate_rst.py` checker enforces two things:

### Blank lines before block elements

Every block-level element (bullet list, enumeration, directive, line block, field list, transition, table) must be separated from the preceding paragraph by a **blank line**. Without it, docutils silently renders the list as prose.

### Indentation

- Normal directive body (`note`, `warning`, `admonition`, ...): **+3** spaces relative to the directive.
- Code-producing directives (`code-block`, `raw`, `math`): first body line **+4**; subsequent lines are code and not checked.
- Manim-like directives (`manim`, `nbcell`): first body line **+3**.
- Literal block after `::`: first line **+4**.
- List-item continuation: aligned with the text after the marker.
- Definition-list descriptions (numpydoc `name : type` descriptions): **+4**.

For intentional non-standard layouts (ASCII art, etc.) use either `:skip-indent:` as a directive option or a `.. rst-check: skip-indent` comment directive immediately before the block.

---

## Manim Examples (`.. manim::`)

The `.. manim::` directive renders a live example in the docs. The `validate_manim_directives.py` checker enforces the `:save_last_frame:` usage rules:

| Scene type | Rule |
|------------|------|
| **Static** (no `self.play`, `self.animate`, etc.) | **MUST** have `:save_last_frame:` |
| **Animated** (has `self.play` / `self.animate`) | **MUST NOT** have `:save_last_frame:` |
| Static with `:save_last_frame:` | Must **not** use `self.wait()` (redundant) |

### Example layout

`check_example_layout.py` runs every example with `skip_animations=True` and checks:

- **OUT_OF_FRAME**: content must not extend beyond the frame by more than 5% of the frame size on any side.
- **TOO_SMALL**: content must cover at least 25% of the frame in both dimensions.

Exceptions for intentional cases can be added to `workflow/example_layout_exemptions.json`.

---

## Cross-References

Docstrings and `.rst` files use Sphinx cross-reference roles to link to other APIs. The `validate_refs.py` checker enforces:

- **Use fully-qualified targets.** Roles like `:class:`, `:meth:`, `:func:`, `:attr:`, `:mod:` must point to fully-qualified names, usually with a leading `~` to display only the last component:

  ```rst
  :meth:`~manim.mobject.mobject.Mobject.scale`
  :class:`~manim_extensions.table.table.Table`
  ```

Short targets like `:attr:`__mob_index`` or `:meth:`Mobject.scale`` are rejected.

- **API names must be cross-references, not inline code.** Back-ticked names that look like APIs (e.g. `` `Mobject.scale` ``) should be proper roles. Built-in types (`int`, `str`, `list`, ...) and common exceptions are exempt.

- **Broken references are rejected.** A `~package.module.Class.attr` target whose module cannot be imported or whose class does not exist fails the check.

Run `python workflow/fix_refs.py` to auto-fix fixable issues.

---

## API Documentation Coverage

Every **public** name (class, function, constant) exported by the package must appear in the documentation under `docs/source/reference/`. This is enforced by `validate_api_coverage.py`.

The docs use a custom `.. autoall::` directive that automatically expands into autodoc directives for all public names of a module. When adding a new public module or name, make sure it is reachable from an `autoall` block (or an explicit `autoclass` / `autofunction` / `autodata`).

After adding new public names, refresh the coverage snapshot:

```bash
python workflow/validate_api_coverage.py --write-snapshot
```

The public-name rules:
- A module defines `__all__` → those are the public names.
- No `__all__` → names defined at module level (not imported) that do not start with `_`.

---

## Licensing & REUSE

The project uses the [REUSE](https://reuse.software/) specification for licensing. Every file must have a clear license and copyright declaration.

### New original files

Add an SPDX header at the very top:

```python
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
```

### Vendored / third-party code

When vendoring an external package, record its copyright, license, and upstream source in `REUSE.toml` under a `[[annotations]]` block for the relevant path. See the existing entries (e.g. `algorithm`, `chemistry`, `physics`) for the format.

CI runs `reuse lint` — a missing or incorrect license declaration will fail the build.

---

## Testing

- Tests live in `tests/` and use **pytest**.
- CI requires **>= 35% coverage** (`--cov-fail-under=35`).
- Tests run under `xvfb-run` because Manim needs a display.
- The test matrix covers Python 3.11–3.14.

```bash
xvfb-run -a pytest tests/ -v
```

---

## Validation Checklist

Run these locally before opening a PR. Each corresponds to a CI job in `.github/workflows/validate.yml`.

| Check | Command |
|-------|---------|
| Docstrings (module + function, numpydoc `Parameters`) | `python workflow/validate_docstrings.py` |
| `__init__` params in class docstring | `python workflow/validate_param_docs.py` |
| numpydoc sections, order, example blocks | `python workflow/validate_doc_sections.py` |
| RST formatting (blank lines, indentation) | `python workflow/validate_rst.py` |
| `.. manim::` `:save_last_frame:` rules | `python workflow/validate_manim_directives.py` |
| Example layout (in frame, not too small) | `python workflow/check_example_layout.py` |
| Cross-references (FQNs, no broken refs) | `python workflow/validate_refs.py` |
| No `from manim import *` outside `__init__` | `python workflow/check_redundant_imports.py` |
| Relative in-package imports | `python workflow/check_relative_imports.py` |
| API coverage | `python workflow/validate_api_coverage.py` |
| Unused imports (F401) | `flake8 manim_extensions --select F401 --exclude "*__init__.py*,test,examples"` |
| License headers | `reuse lint` |
| Type annotations on all params | *(CI; `scripts/check_type_annotations.py`)* |
| Dependencies audit | `pip-audit --desc on` |

Several checkers have a `--fix` mode for auto-repairable issues:

```bash
python workflow/validate_docstrings.py --fix        # Args: -> Parameters
python workflow/check_redundant_imports.py --fix   # star -> explicit imports
python workflow/check_relative_imports.py --fix     # absolute -> relative imports
python workflow/fix_refs.py                         # cross-reference fixes
```

Vendored subpackages that intentionally deviate from a rule can be exempted via the corresponding `*_exemptions.json` file (`doc_section_exemptions.json`, `param_docs_exemptions.json`, `example_layout_exemptions.json`).

---

## Pull Request Guidelines

- **One concern per PR.** Keep the diff focused and small.
- **Document public API changes.** New public names need docs; changed signatures need updated docstrings and changelog entries.
- **Do not break existing tests.** Run `pytest tests/` locally.
- **Run the validation checklist** above and fix any failures.
- **Add a `.. manim::` example** to any new mobject subclass.
- **Ensure `reuse lint` passes** for any new files.
- Write clear, conventional commit messages.

---

## Reporting Issues

When reporting a bug, please include:

- A minimal reproducible example.
- The expected behavior vs. actual behavior.
- Your Python version and Manim version.

## Translating the documentation

The documentation is localised with Sphinx's gettext support. English is the
source language; the Chinese (Simplified) catalog lives at
`docs/source/locale/zh_CN/LC_MESSAGES/docs.po`.

After editing any English `.rst` source or public docstring, refresh the
catalogs and merge them into the `.po` file:

```bash
cd docs
make gettext        # or: make.bat gettext on Windows
```

Then translate the new/changed `msgid` entries in `docs.po` (empty `msgstr`
falls back to English, so partial translations are fine). Preview the Chinese
build locally with:

```bash
make html-zh        # or: make.bat html-zh on Windows
```

On Read the Docs, the Chinese version is a separate project set to language
"Chinese (Simplified)" and linked to the English project as a translation;
RTD passes the language to Sphinx automatically, so no extra config is needed.
