.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

decision_tree
=============

.. module:: manim_extensions.machine_learning.decision_tree

Classes
-------

.. autosummary::
   :nosignatures:

   ~decision_tree.DecisionTreeContainer
   ~decision_tree.DecisionTreeDiagram
   ~decision_tree.LeafNode
   ~decision_tree.SplitNode

Usage
-----

Pass a fitted scikit-learn tree to the diagram; feature names and class names are optional labels.

.. manim:: IrisDecisionTree
   :save_last_frame:
   :ref_classes: DecisionTreeDiagram

   from manim import *
   from sklearn.datasets import load_iris
   from sklearn.tree import DecisionTreeClassifier
   from manim_extensions.machine_learning.decision_tree.decision_tree import (
       DecisionTreeDiagram,
   )

   class IrisDecisionTree(Scene):
       def construct(self):
           iris = load_iris()
           clf = DecisionTreeClassifier(max_depth=2, random_state=0).fit(
               iris.data[:, :2], iris.target
           )
           diagram = DecisionTreeDiagram(
               clf.tree_,
               feature_names=["sepal length", "sepal width"],
               class_names=[str(name) for name in iris.target_names],
           )
           diagram.scale_to_fit_width(10)
           if diagram.height > 6:
               diagram.scale_to_fit_height(6)
           diagram.move_to(ORIGIN)
           self.add(diagram)

Modules
-------

.. autosummary::
   :nosignatures:

   ~decision_tree
   ~decision_tree_embedding
   ~decision_tree_surface
   ~helpers

.. toctree::
   :hidden:
   :maxdepth: 1

   decision_tree
   decision_tree_embedding
   decision_tree_surface
   helpers
