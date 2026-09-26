.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Installation
============

Stable release
--------------

Install the latest stable release from PyPI:

.. code-block:: bash

   pip install manim_extensions

This installs Manim Community Edition (>=0.21), numpy, and — on
Python < 3.13 — the ``manim-mobject-svg`` plugin. Everything else ships
with manim itself or is split into the per-module extras below and
lazy-imported on use.

Optional extras
---------------

Some functionality requires additional packages that are not installed
by default:

.. code-block:: bash

   pip install manim_extensions[all]         # every module at once
   pip install manim_extensions[automata]    # xmltodict
   pip install manim_extensions[chemistry]   # pandas, xmltodict, requests
   pip install manim_extensions[dev]         # pytest for running tests
   pip install manim_extensions[docs]        # sphinx + furo for building docs
   pip install manim_extensions[meshes]      # trimesh, moderngl
   pip install manim_extensions[ml]          # matplotlib, scikit-learn, seaborn, tqdm
   pip install manim_extensions[physics]     # pymunk, shapely
   pip install manim_extensions[qr]          # segno
   pip install manim_extensions[rubikscube]  # kociemba
   pip install manim_extensions[svg]         # svgpathtools
   pip install manim_extensions[video]       # opencv (VideoMobject)

If a feature is used without its extra installed, the error message
names the exact ``pip install manim_extensions[...]`` command.

Every vendored module also has a same-named extra. The ones below
declare no additional dependencies (they work with the base install)
but exist so installs can uniformly request
``manim_extensions[<module>]``: ``algorithm``, ``arabic``, ``circuit``,
``compass``, ``data_structures``, ``economics``, ``fontawesome``,
``gearbox``, ``mindmap``, ``sequence_diagram``, ``table``, ``tikz``,
``weighted_line``.

One lazily-imported plugin is only partially declared in
``pyproject.toml`` because its PyPI metadata pins an incompatible Python
version:

- **manim-mobject-svg** (for :class:`~manim_extensions.svg_animations.HTMLParsedVMobject`)
  is installed automatically on Python < 3.13; on Python 3.13+ install
  it with ``pip install --ignore-requires-python manim-mobject-svg``.

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