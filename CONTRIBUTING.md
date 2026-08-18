<!--
SPDX-FileCopyrightText: 2026 ExploreMaths
SPDX-License-Identifier: MIT
-->

# Contributing

Contributions are welcome! Please open issues or pull requests on the
[GitHub repository](https://github.com/ExploreMaths/manim_extensions).

## Getting Started

1. Fork the repository and clone your fork locally.
2. Create a new branch for your changes:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Make your changes and add tests if applicable.
4. Run the test suite to ensure nothing is broken:
   ```bash
   pytest
   ```
5. Submit a pull request to the `main` branch.

## Code Style

- Follow PEP 8 for Python code.
- Use meaningful variable and function names.
- Add docstrings for all public functions and classes.
- Keep lines within 88 characters (Black-compatible).

## Reporting Issues

When reporting a bug, please include:

- A minimal reproducible example.
- The expected behavior vs. actual behavior.
- Your Python version and Manim version.

## Contributing Extensions

If you would like to contribute your own extension (e.g. a new mobject module,
utility, or visualization), please follow these guidelines:

- **Categorize your extension** into an appropriate module (e.g. `mobjects`,
  `geometry`, `meshes`, `automata`, `physics`, etc.). If no existing category
  fits, a new module may be proposed.
- **Create a pull request** with a clear description of what the extension does
  and how it fits into the project.
- **Include documentation** with example usages in the docstrings so that the
  Sphinx docs can render a live preview.
- **Ensure code quality** by running the existing test suite and linters.

## Pull Request Guidelines

- Each PR should focus on a single concern.
- Update documentation if you change public APIs.
- Do not break existing tests.
- Keep the diff as small and focused as possible.