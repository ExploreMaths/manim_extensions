<!--
SPDX-FileCopyrightText: 2026 ExploreMaths
SPDX-License-Identifier: MIT
-->

# Development workflow

Set up a local checkout, keep the diff focused, and run the automated checks
before opening a pull request. Every convention linked from this page is
enforced by a script in CI, so a local run of the same commands is the fastest
way to a green build.

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

### 5. Keep your branch up to date

```bash
git fetch upstream
git rebase upstream/main
```

Rebase rather than merge so the history stays linear; resolve conflicts in
the file that changed and re-run the checks before pushing again.


## Pull Request Guidelines

- **One concern per PR.** Keep the diff focused and small.
- **Document public API changes.** New public names need docs; changed signatures need updated docstrings and changelog entries.
- **Do not break existing tests.** Run `pytest tests/` locally.
- **Run the validation checklist** in {doc}`testing` and fix any failures.
- **Add a `.. manim::` example** to any new mobject subclass.
- **Put `Examples` last** in a docstring; use `.. note::` / `.. seealso::` blocks (before `Examples`) instead of `Notes` / `See Also` headers.
- **Ensure `reuse lint` passes** for any new files.
- Write clear, conventional commit messages.


## Reporting Issues

When reporting a bug, please include:

- A minimal reproducible example.
- The expected behavior vs. actual behavior.
- Your Python version and Manim version.
