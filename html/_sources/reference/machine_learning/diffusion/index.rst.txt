.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

diffusion
=========

.. module:: manim_extensions.machine_learning.diffusion

Usage
-----

The MCMC helpers are building blocks for diffusion and sampling scenes; import the sampler and visualisation helpers from the `mcmc` module.

.. code-block:: python

   from manim_extensions.machine_learning.diffusion.mcmc import (
       MultidimensionalGaussianPosterior,
       metropolis_hastings_sampler,
       make_dist_image_mobject_from_samples,
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
