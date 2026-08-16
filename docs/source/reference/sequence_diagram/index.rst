Sequence diagram
================

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

Quick start
-----------

.. manim:: SequenceDiagramLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.sequence_diagram import SeqActor, SeqObject

   class SequenceDiagramLibraryExample(Scene):
       def construct(self):
           actor = SeqActor("User")
           obj = SeqObject("Service")
           self.add(actor, obj)

This library is especially useful when explaining:

* API request / response flows,
* lifecycle and event sequences,
* software interaction diagrams and protocol walkthroughs.

See the `original project <https://github.com/foxnewsnetwork/manim-sequence-diagram>`_
for more complete sequence examples and output samples.

.. toctree::
   :hidden:

   classes