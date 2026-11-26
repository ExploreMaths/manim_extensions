.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

diffusion
=========

.. automodule:: manim_extensions.machine_learning.diffusion

Usage
-----

The MCMC helpers are building blocks for diffusion and sampling scenes; import the sampler and visualisation helpers from the `mcmc` module.

.. code-block:: python

   from manim_extensions.machine_learning.diffusion.mcmc import (
       MultidimensionalGaussianPosterior,
       SampleDistributionImage,
       metropolis_hastings_sampler,
   )

Modules
-------

.. autosummary::
   :nosignatures:

   ~mcmc

.. toctree::
   :hidden:
   :maxdepth: 1

   mcmc
