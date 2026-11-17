.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

_AnimationBuilder
=================

``mobject.animate`` and ``camera.frame.animate`` return Manim's
``_AnimationBuilder`` instead of an ``Animation``. The object records fluent
method calls on the mobject target and materialises the real animation only
when it is passed to :py:meth:`~manim.scene.scene.Scene.play`. Methods such as
``set_run_time``,
``scale``, ``shift`` or ``move_to`` are forwarded dynamically to the target
mobject through ``__getattr__``; ``build`` is the documented entry point that
turns the recorded calls into an ``Animation``.

.. autoclass:: manim.mobject.mobject._AnimationBuilder
   :members:
