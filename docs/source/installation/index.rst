Installation
============

Stable release
--------------

Install the latest stable release from PyPI:

.. code-block:: bash

   pip install manim_extensions

This pulls in Manim as the only required runtime dependency.

Verifying the installation
--------------------------

After installation, import the package in Python:

.. code-block:: python

   import manim_extensions
   print(manim_extensions.__version__)

You can also run the test suite locally:

.. code-block:: bash

   pip install pytest
   pytest tests/ -q

Development install
-------------------

To work on ``manim_extensions`` itself, clone the repository with its
submodules and install in editable mode:

.. code-block:: bash

   git clone https://github.com/ExploreMaths/manim_extensions.git
   cd manim_extensions
   pip install -e .

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