Reference Manual
================

The reference manual contains the complete API for ``manim_extensions``.

Inheritance Graphs
------------------

Basic
*****

.. inheritance-diagram::
   manim_extensions.mobjects
   manim_extensions.animations
   :parts: 1
   :top-classes: manim.mobject.mobject.Mobject, manim.animation.animation.Animation

GearBox
*******

.. inheritance-diagram::
   manim_extensions.gearbox.gear_mobject.Gear_mobject
   :parts: 1
   :top-classes: manim.mobject.types.vectorized_mobject.VMobject

MindMap
*******

.. inheritance-diagram::
   manim_extensions.mindmap.mindmap.mindmap
   manim_extensions.mindmap.nodes.node
   manim_extensions.mindmap.animations.animations
   :parts: 1
   :top-classes: manim.mobject.mobject.Mobject

Compass
*******

.. inheritance-diagram::
   manim_extensions.compass.compass.compass
   manim_extensions.compass.compass.pencil
   manim_extensions.compass.compass.ruler
   manim_extensions.compass.scene.compass_scene
   :parts: 1
   :top-classes: manim.mobject.mobject.Mobject

Module Index
------------

.. toctree::
   :maxdepth: 3

   basic/index
   algorithm/index
   automata/index
   circuit/index
   compass/index
   data_structures/index
   gearbox/index
   meshes/index
   mindmap/index
   neural_network/index
   physics/index
   rubikscube/index
   sequence_diagram/index
   tikz/index
