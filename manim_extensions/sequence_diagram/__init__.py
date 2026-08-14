"""Sequence diagram primitives.

This module exports the actors, actions, and objects used for sequence-diagram
style visualisations in Manim.

    Examples
    --------

.. manim:: SequenceDiagramPackageDocExample
      :save_last_frame:

   from manim import *
   from manim_extensions.sequence_diagram import SeqActor, SeqObject

   class SequenceDiagramPackageDocExample(Scene):
       def construct(self):
"""

__version__ = "0.1.0"

from .seq_action import *
from .seq_actor import *
from .seq_object import *

__all__ = [
  "SeqAction",
  "SeqActor",
  "SeqObject"
]