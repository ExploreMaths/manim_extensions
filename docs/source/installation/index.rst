.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Installation
============

Stable release
--------------

Install the latest stable release from PyPI:

.. code-block:: bash

   pip install manim_extensions

This installs Manim Community Edition (>=0.21) along with all core
runtime dependencies (numpy, scipy, pandas, networkx, etc.).

Optional extras
---------------

Some functionality requires additional packages that are not installed
by default:

.. code-block:: bash

   pip install manim_extensions[dev]     # pytest for running tests
   pip install manim_extensions[docs]    # sphinx + furo for building docs
   pip install manim_extensions[ml]      # matplotlib, scikit-learn, seaborn, tqdm

Two lazily-imported plugins are not declared in ``pyproject.toml`` because
their PyPI metadata pins incompatible Manim or Python versions:

- **manim-mobject-svg** (for :class:`~manim_extensions.svg_animations.HTMLParsedVMobject`) —
  on Python 3.13+ install with
  ``pip install --ignore-requires-python manim-mobject-svg``.
- **manim-nerdfont-icons** (for the optional ``icon`` argument of
  :func:`~manim_extensions.qr_codes.qr_code`) — install with
  ``pip install --no-deps manim-nerdfont-icons``.

Verifying the installation
--------------------------

After installation, import the package in Python:

.. code-block:: python

   import manim_extensions
   print(manim_extensions.__version__)

You can also run the test suite locally:

.. code-block:: bash

   pip install manim_extensions[dev]
   pytest tests/ -q

Development install
-------------------

To work on ``manim_extensions`` itself, clone the repository and install
in editable mode:

.. code-block:: bash

   git clone https://github.com/ExploreMaths/manim_extensions.git
   cd manim_extensions
   pip install -e ".[dev]"

The bundled plugins are included directly as Python subpackages.

LaTeX requirements
------------------

If you want to use :class:`~manim_extensions.mobjects.ChineseMathTex`, make
sure ``xelatex`` and the ``xeCJK`` LaTeX package are available on your system.
For English-only formulas, Manim's default :class:`~manim.MathTex` works
without additional LaTeX packages.

Building the documentation
--------------------------

The documentation uses Sphinx and a custom Manim directive. Build it with:

.. code-block:: bash

   cd docs
   make clean     # Linux/macOS (uses the Makefile)
   make html

.. code-block:: doscon

   make.bat clean   # Windows
   make.bat html

The generated HTML will be in ``docs/build/html/``.