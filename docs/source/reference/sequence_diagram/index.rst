.. SPDX-FileCopyrightText: 2023 Thomas Chen
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Sequence diagram
================

.. vendored-status:: foxnewsnetwork/manim-sequence-diagram

**Original author:** `Thomas Chen <https://github.com/foxnewsnetwork>`_

**Source repository:** `GitHub <https://github.com/foxnewsnetwork/manim-sequence-diagram>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-sequence-diagram`` adds UML-like sequence-diagram primitives to Manim.
It is meant for software architecture explanations, API flow demos, and
message-order visualisations.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.sequence_diagram`` subpackage.

Features
--------

- :class:`~manim_extensions.sequence_diagram.seq_actor.SeqActor` – participant or lifeline object.
- :class:`~manim_extensions.sequence_diagram.seq_object.SeqObject` – object or system boundary in the sequence.
- :class:`~manim_extensions.sequence_diagram.seq_action.SeqAction` – action or message entry in the timeline.
- simple composition for actor-to-actor communication flows.
- diagrams for software engineering and protocol explanations.

Usage
-----

Upstream shipped ``manim-sequence-diagram`` as a Manim plugin (enabled in
``manim.cfg`` under ``[CLI]`` with ``plugins = manim_sequence_diagram``); here
it is bundled directly inside ``manim_extensions.sequence_diagram``. The API is
entirely Python-based — upstream notes that a dedicated sequence-diagram
syntax may be added later.

Create :class:`~manim_extensions.sequence_diagram.seq_actor.SeqActor`
participants, introduce them onto the timeline, and then move a
:class:`~manim_extensions.sequence_diagram.seq_object.SeqObject` from one actor
to another. The methods on
:class:`~manim_extensions.sequence_diagram.seq_action.SeqAction` are
generators that yield the animations to play:

.. manim:: ClientRaceDatabaseNetwork
   :ref_classes: SeqActor SeqAction SeqObject

   from manim import *
   from manim_extensions.sequence_diagram import (
       SeqActor,
       SeqAction,
       SeqObject,
   )

   class ClientRaceDatabaseNetwork(MovingCameraScene):
       def construct(self):
           actor_client = SeqActor(name="client")
           actor_delivery = SeqActor(name="delivery")
           actor_server = SeqActor(name="server")
           actor_db = SeqActor(name="database")

           # introduce_actors yields a single Fade-in of the grouped actors
           for anim in SeqAction.introduce_actors(
               actor_client, actor_server, actor_delivery, actor_db
           ):
               self.play(anim)

           # move the camera yourself as the diagram grows downward
           self.play(self.camera.frame.animate.move_to(DOWN * 3))

           # subject_gives_gift_to_target yields the lifeline and message
           # animations that move a SeqObject from subject to target
           for anim in SeqAction.subject_gives_gift_to_target(
               subject=actor_client,
               gift=SeqObject(name="async getData"),
               target=actor_delivery,
           ):
               self.play(anim)

.. toctree::
   :hidden:
   :maxdepth: 1

   classes
   constants
