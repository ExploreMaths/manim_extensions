"""Contains classes to construct an array.

Examples
--------

.. manim:: MArrayModuleDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions.data_structures import (
       MArray, MArrayPointer, MArrayDirection
   )

   class MArrayModuleDocExample(Scene):
       def construct(self):
           arr = MArray(self, [10, 20, 30, 40, 50], label="data")
           ptr = MArrayPointer(
               self, arr, index=2, label="i",
               pointer_pos=MArrayDirection.UP
           )
           self.add(arr, ptr)
"""

from copy import deepcopy

import numpy as np
from manim import *
from manim.mobject.mobject import _AnimationBuilder
from typing import Any, Callable, List, Tuple, Union

from .m_enum import MArrayDirection, MArrayElementComp


class MArrayElement(VGroup):
    """A class that represents an array element.

    Parameters
    ----------
    scene
        Specifies the scene where the object is to be rendered.
    mob_square_args
        Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
    mob_value_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
    mob_index_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
    mob_label_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element label.
    index_pos
        Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`
    index_gap
        Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
    label_pos
        Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
    label_gap
        Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
    next_to_mob
        Specifies the placement for :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square` w.r.t another :class:`~manim_extensions.data_structures.m_array.MArrayElement`.
    next_to_dir
        Specifies the direction of placement for :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square` w.r.t another :class:`~manim_extensions.data_structures.m_array.MArrayElement`.

    Examples
    --------
    .. manim:: MArrayElementDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.data_structures import MArrayElement

       class MArrayElementDocExample(Scene):
           def construct(self):
               elem = MArrayElement(
                   self,
                   mob_value_args={"text": "42"},
                   mob_index_args={"text": "i"},
                   mob_label_args={"text": "x"},
               )
               self.add(elem)

    Attributes
    ----------

    __scene : :class:`~manim.scene.scene.Scene`
        The scene where the object is to be rendered.
    __mob_square_props : :class:`dict`
        Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
    __mob_value_props : :class:`dict`
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
    __mob_index_props : :class:`dict`
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
    __mob_label_props : :class:`dict`
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element label.
    __index_pos : :class:`numpy.ndarray`
        The position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`
    __index_gap : :class:`float`
        The distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
    __label_pos : :class:`numpy.ndarray`
        The position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
    __label_gap : :class:`float`
        The distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
    __mob_square : :class:`~manim.mobject.geometry.polygram.Square`
        Represents the body of the element.
    __mob_value : :class:`~manim.mobject.text.text_mobject.Text`
        Represents the value of the element.
    __mob_index : :class:`~manim.mobject.text.text_mobject.Text`
        Represents the index of the element.
    __mob_label : :class:`~manim.mobject.text.text_mobject.Text`
        Represents the label of the element.
    """

    def __init_props(
        self,
        scene: Scene,
        index_pos: np.ndarray,
        index_gap: float,
        label_pos: np.ndarray,
        label_gap: float,
    ) -> None:
        """Initializes the attributes for the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        index_pos
            Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`
        index_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        label_pos
            Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        """

        self.__mob_square_props: dict = {
            "color": BLUE_B,
            "fill_color": BLUE_D,
            "fill_opacity": 1,
            "side_length": 1,
        }
        self.__mob_value_props: dict = {"text": "", "color": WHITE, "weight": BOLD}
        self.__mob_index_props: dict = {"text": "", "color": BLUE_D, "font_size": 32}
        self.__mob_label_props: dict = {"text": "", "color": BLUE_A, "font_size": 38}
        self.__scene: Scene = scene
        self.__index_pos: np.ndarray = index_pos
        self.__index_gap: float = index_gap
        self.__label_pos: np.ndarray = label_pos
        self.__label_gap: float = label_gap

    def __update_props(
        self,
        mob_square_args: dict = {},
        mob_value_args: dict = {},
        mob_index_args: dict = {},
        mob_label_args: dict = {},
    ) -> None:
        """Updates the attributes of the class.

        Parameters
        ----------
        mob_square_args
            Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
        mob_value_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
        mob_index_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element label.
        """

        self.__mob_square_props.update(mob_square_args)
        self.__mob_value_props.update(mob_value_args)
        self.__mob_index_props.update(mob_index_args)
        self.__mob_label_props.update(mob_label_args)

        if type(self.__mob_value_props["text"]) != str:
            self.__mob_value_props["text"] = str(self.__mob_value_props["text"])

        if type(self.__mob_index_props["text"]) != str:
            self.__mob_index_props["text"] = str(self.__mob_index_props["text"])

        if type(self.__mob_label_props["text"]) != str:
            self.__mob_label_props["text"] = str(self.__mob_label_props["text"])

    def __init_mobs(
        self,
        init_square: bool = False,
        init_value: bool = False,
        init_index: bool = False,
        init_label: bool = False,
        next_to_mob: "MArrayElement" = None,
        next_to_dir: np.ndarray = RIGHT,
    ) -> None:
        """Initializes the mobjects for the class.

        Parameters
        ----------
        init_square
            If `True`, instantiates a :class:`~manim.mobject.geometry.polygram.Square` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        init_value
            If `True`, instantiates a :class:`~manim.mobject.text.text_mobject.Text` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_value`.
        init_index
            If `True`, instantiates a :class:`~manim.mobject.text.text_mobject.Text` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index`.
        init_label
            If `True`, instantiates a :class:`~manim.mobject.text.text_mobject.Text` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label`.
        next_to_mob
            Specifies placement for :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square` w.r.t another :class:`~manim_extensions.data_structures.m_array.MArrayElement`.
        next_to_dir
            Specifies direction of placement for :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square` w.r.t another :class:`~manim_extensions.data_structures.m_array.MArrayElement`.
        """

        if init_square:
            self.__mob_square: Square = Square(**self.__mob_square_props)
            if next_to_mob is not None:
                self.__mob_square.next_to(
                    next_to_mob.fetch_mob_square(), next_to_dir, 0
                )
            self.add(self.__mob_square)

        if init_value:
            self.__mob_value: Text = Text(**self.__mob_value_props)
            self.__mob_value.next_to(self.__mob_square, np.array([0, 0, 0]), 0)
            self.add(self.__mob_value)

        if init_index:
            self.__mob_index: Text = Text(**self.__mob_index_props)
            self.__mob_index.next_to(
                self.__mob_square, self.__index_pos, self.__index_gap
            )
            self.add(self.__mob_index)

        if init_label:
            self.__mob_label: Text = Text(**self.__mob_label_props)
            self.__mob_label.next_to(
                self.__mob_square, self.__label_pos, self.__label_gap
            )
            self.add(self.__mob_label)

    def __deepcopy__(self, memo):
        """Deepcopy that excludes attributes specified in `exclude_list`."""

        exclude_list = ["_MArrayElement__scene"]

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in exclude_list:
                setattr(result, k, deepcopy(v, memo))
        return result

    def __init__(
        self,
        scene: Scene,
        mob_square_args: dict = {},
        mob_value_args: dict = {},
        mob_index_args: dict = {},
        mob_label_args: dict = {},
        index_pos: np.ndarray = UP,
        index_gap: float = 0.25,
        label_pos: np.ndarray = LEFT,
        label_gap: float = 0.5,
        next_to_mob: "MArrayElement" = None,
        next_to_dir: np.ndarray = RIGHT,
        **kwargs
    ) -> None:
        """Initializes the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        mob_square_args
            Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
        mob_value_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
        mob_index_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element label.
        index_pos
            Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`
        index_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        label_pos
            Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        next_to_mob
            Specifies the placement for :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square` w.r.t another :class:`~manim_extensions.data_structures.m_array.MArrayElement`.
        next_to_dir
            Specifies the direction of placement for :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square` w.r.t another :class:`~manim_extensions.data_structures.m_array.MArrayElement`.
        """

        super().__init__(**kwargs)

        self.__init_props(scene, index_pos, index_gap, label_pos, label_gap)

        self.__update_props(
            mob_square_args, mob_value_args, mob_index_args, mob_label_args
        )

        self.__init_mobs(True, True, True, True, next_to_mob, next_to_dir)

    def fetch_mob_square(self) -> Square:
        """Fetches the square mobject.

        Returns
        -------
        :class:`~manim.mobject.geometry.polygram.Square`
            :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        """

        return self.__mob_square

    def fetch_mob_value(self) -> Text:
        """Fetches the value mobject.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_value`.
        """

        return self.__mob_value

    def fetch_mob_index(self) -> Text:
        """Fetches the index mobject.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index`.
        """

        return self.__mob_index

    def fetch_mob_label(self) -> Text:
        """Fetches the label mobject.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label`.
        """

        return self.__mob_label

    def fetch_mob(self, mob_target: MArrayElementComp) -> Mobject:
        """Fetches the mobject based on the specified enum.

        Parameters
        ----------
        mob_target
            Specifies the :class:`~manim.mobject.mobject.Mobject` to fetch.

        Returns
        -------
        :class:`~manim.mobject.mobject.Mobject`
            Mobject of the class.
        """

        if mob_target == MArrayElementComp.BODY:
            return self.fetch_mob_square()
        elif mob_target == MArrayElementComp.VALUE:
            return self.fetch_mob_value()
        elif mob_target == MArrayElementComp.INDEX:
            return self.fetch_mob_index()
        elif mob_target == MArrayElementComp.LABEL:
            return self.fetch_mob_label()
        else:
            return self

    def update_mob_value(
        self,
        mob_value_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Re-intializes the value mobject.

        Parameters
        ----------
        mob_value_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
        update_anim
            Animation to be applied to the updated :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_value`.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_value`.
        """

        self.__update_props(mob_value_args=mob_value_args)

        self.remove(self.__mob_value)

        self.__init_mobs(init_value=True)

        self.add(self.__mob_value)

        if play_anim:
            self.__scene.play(
                update_anim(self.__mob_value, **update_anim_args), **play_anim_args
            )

        return self.__mob_value

    def update_mob_index(
        self,
        mob_index_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Re-intializes the index mobject.

        Parameters
        ----------
        mob_index_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
        update_anim
            Animation to be applied to the updated :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index`.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index`.
        """

        self.__update_props(mob_index_args=mob_index_args)

        self.remove(self.__mob_index)

        self.__init_mobs(init_index=True)

        self.add(self.__mob_index)

        if play_anim:
            self.__scene.play(
                update_anim(self.__mob_index, **update_anim_args), **play_anim_args
            )

        return self.__mob_index

    def update_mob_label(
        self,
        mob_label_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Re-intializes the label mobject.

        Parameters
        ----------
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element label.
        update_anim
            Animation to be applied to the updated :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label`.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label`.
        """

        self.__update_props(mob_label_args=mob_label_args)

        self.remove(self.__mob_label)

        self.__init_mobs(init_label=True)

        self.add(self.__mob_label)

        if play_anim:
            self.__scene.play(
                update_anim(self.__mob_label, **update_anim_args), **play_anim_args
            )

        return self.__mob_label

    def animate_mob_square(self) -> "_AnimationBuilder":
        """Invokes the animate property over square mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_square`.
        """

        return self.__mob_square.animate

    def animate_mob_value(self) -> "_AnimationBuilder":
        """Invokes the animate property over value mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_value`.
        """

        return self.__mob_value.animate

    def animate_mob_index(self) -> "_AnimationBuilder":
        """Invokes the animate property over index mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_index`.
        """

        return self.__mob_index.animate

    def animate_mob_label(self) -> "_AnimationBuilder":
        """Invokes the animate property over label mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArrayElement.__mob_label`.
        """

        return self.__mob_label.animate


class MArray(VGroup):
    """A class that represents an array.

    Parameters
    ----------
    scene
        Specifies the scene where the object is to be rendered.
    arr
        Specifies the array to represent.
    label
        Specifies the value of the array label.
    index_offset
        Specifies the difference between successive displayable indices.
    index_start
        Specifies the starting value of displayable index.
    index_hex_display
        If `True`, displays indices in hex.
    hide_index
        If `True`, doesn't display indices.
    arr_dir
        Specifies the growth direction of the array.
    arr_label_pos
        Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
    arr_label_gap
        Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` and :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
    mob_arr_label_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the array label.
    mob_square_args
        Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
    mob_value_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
    mob_index_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
    **kwargs
        Forwarded to constructor of the parent.

    Examples
    --------
    .. manim:: MArrayDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.data_structures import MArray

       class MArrayDocExample(Scene):
           def construct(self):
               arr = MArray(self, [3, 1, 4, 1, 5, 9, 2, 6], label="arr")
               self.add(arr)

    .. manim:: MArrayInsertRemoveDocExample

       from manim import *
       from manim_extensions.data_structures import MArray

       class MArrayInsertRemoveDocExample(Scene):
           def construct(self):
               arr = MArray(self, [1, 3, 5, 7], label="arr")
               self.play(Write(arr))
               self.wait(0.5)
               arr.append_elem(2)
               self.wait(0.5)
               arr.append_elem(4)
               self.wait(0.5)
               arr.remove_elem(index=1)
               self.wait(0.5)

    Attributes
    ----------

    __scene : :class:`~manim.scene.scene.Scene`
        The scene where the object is to be rendered.
    __arr : :class:`list`
        The array to represent.
    __label : :class:`str`
        The value of the array label.
    __index_offset : :class:`int`
        The difference between successive displayable indices.
    __index_start : :class:`int`
        The starting value of displayable index.
    __index_hex_display : :class:`bool`
        If `True`, displays indices in hex.
    __hide_index : :class:`bool`
        If `True`, doesn't display indices.
    __arr_dir : :class:`~.m_enum.MArrayDirection`
        The growth direction of the array.
    __arr_label_pos : :class:`~.m_enum.MArrayDirection`
        The position of :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
    __arr_label_gap : :class:`float`
        The distance between :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` and :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
    __mob_arr_label_props : :class:`dict`
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the array label.
    __mob_arr : :class:`~typing.List` [:class:`~manim_extensions.data_structures.m_array.MArrayElement`]
        Represents the array.
    __mob_arr_label : :class:`~manim.mobject.text.text_mobject.Text`
        Represents the array label.
    """

    __dir_map = [
        {"arr": UP, "index": RIGHT},
        {"arr": DOWN, "index": RIGHT},
        {"arr": RIGHT, "index": UP},
        {"arr": LEFT, "index": UP},
    ]
    """Maps :class:`~.m_enum.MArrayDirection` to :class:`numpy.ndarray`."""

    def __sum_elem_len(self, index_start: int, index_end: int) -> int:
        """Sums the side_length of all elements' square mobject present in the array between the specified range.

        Parameters
        ----------
        index_start
            Starting index of the range (inclusive).
        index_end
            Ending index of the range (inclusive).

        Returns
        -------
        :class:`int`
            Sum of ``side_length`` of all :class:`~manim.mobject.geometry.polygram.Square` present inside :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr` in the specified range.
        """

        if (
            index_start < 0
            or index_end < 0
            or index_start > len(self.__mob_arr)
            or index_end > len(self.__mob_arr)
        ):
            raise Exception("Index out of bounds!")

        total_len = 0
        for i in range(index_start, index_end + 1):
            total_len += self.__mob_arr[i].fetch_mob_square().side_length
        return total_len

    def __calc_label_pos_and_mob(self) -> Tuple[Square, np.ndarray]:
        """Calculates the position of the array label relative to one of the element's square mobjects.

        Returns
        -------
        :class:`~manim.mobject.geometry.polygram.Square`
            Square mobject next to which the array label is positioned.
        :class:`numpy.ndarray`
            The relative position of the array label.
        """

        if np.array_equal(
            self.__dir_map[self.__arr_label_pos.value]["arr"],
            self.__dir_map[self.__arr_dir.value]["arr"],
        ):
            return (
                self.__mob_arr[-1].fetch_mob_square(),
                self.__dir_map[self.__arr_label_pos.value]["arr"],
            )
        elif np.array_equal(
            self.__dir_map[self.__arr_label_pos.value]["arr"],
            -self.__dir_map[self.__arr_dir.value]["arr"],
        ):
            return (
                self.__mob_arr[0].fetch_mob_square(),
                self.__dir_map[self.__arr_label_pos.value]["arr"],
            )

        else:
            middle_index = len_before = len_after = 0
            if len(self.__mob_arr) > 1:
                odd_indices = len(self.__mob_arr) % 2 == 1
                middle_index = int(len(self.__mob_arr) / 2)
                len_before = self.__sum_elem_len(0, middle_index - 1)
                len_after = self.__sum_elem_len(
                    middle_index + 1 if odd_indices else middle_index,
                    len(self.__mob_arr) - 1,
                )
            return (
                self.__mob_arr[middle_index].fetch_mob_square(),
                self.__dir_map[self.__arr_label_pos.value]["arr"]
                + self.__dir_map[self.__arr_dir.value]["arr"]
                * ((len_after - len_before) / 2),
            )

    def __calc_index(self, index: int) -> Union[int, str]:
        """Calculates the displayable index of the specified element based on attributes set at initialization.

        Parameters
        ----------
        index
            Specifies the index of the element for which to compute the displayable index.

        Returns
        -------
        :data:`~typing.Union` [:class:`int`, :class:`str`]
            Displayable index.
        """

        return (
            ""
            if self.__hide_index
            else (
                self.__index_start + self.__index_offset * index
                if self.__index_hex_display is False
                else hex(self.__index_start + self.__index_offset * index)
            )
        )

    def __calc_index_pos(self) -> np.ndarray:
        """Calculates the index position of all elements based on attributes set at initialization.

        Returns
        -------
        :class:`numpy.ndarray`
            Index position.
        """

        return (
            self.__dir_map[self.__arr_dir.value]["index"]
            if not self.__switch_index_pos
            else self.__dir_map[self.__arr_dir.value]["index"] * -1
        )

    def __calc_label_shift_factor(self, mob: MArrayElement) -> float:
        """Calculates how much to shift the array label after insertion/removal of an element.

        Parameters
        ----------
        mob
            Specifies the element that is inserted/removed.

        Returns
        -------
        :class:`float`
            Factor by which to shift the :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label`.
        """

        if np.array_equal(
            self.__dir_map[self.__arr_label_pos.value]["arr"],
            self.__dir_map[self.__arr_dir.value]["arr"],
        ):
            return mob.fetch_mob_square().side_length
        elif not np.array_equal(
            self.__dir_map[self.__arr_label_pos.value]["arr"],
            -self.__dir_map[self.__arr_dir.value]["arr"],
        ):
            return mob.fetch_mob_square().side_length / 2
        return 0

    def __append_elem(
        self,
        value,
        shift_label: bool = True,
        append_anim: Animation = Write,
        append_anim_args: dict = {},
        append_anim_target: MArrayElementComp = None,
        mob_square_args: dict = {},
        mob_value_args: dict = {},
        mob_index_args: dict = {},
    ) -> List[Animation]:
        """Creates and inserts a new element in the array.

        Parameters
        ----------
        value
            Specifies the value of the new element.
        shift_label
            If `True`, shifts the :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` to center of the array.
        append_anim
            Animation to be applied to the new element.
        append_anim_args
            Arguments for append :class:`~manim.animation.animation.Animation`.
        append_anim_target
            Specifies the target :class:`~manim.mobject.mobject.Mobject` of the :class:`~manim_extensions.data_structures.m_array.MArrayElement` on which the append :class:`~manim.animation.animation.Animation` is to be played.
        mob_square_args
            Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
        mob_value_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
        mob_index_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.

        Returns
        -------
        :data:`typing.List` [:class:`~manim.animation.animation.Animation`]
            List of append animations.
        """

        mob_value_args["text"] = value
        mob_index_args["text"] = self.__calc_index(len(self.__mob_arr))
        self.__mob_arr.append(
            MArrayElement(
                scene=self.__scene,
                mob_square_args=mob_square_args,
                mob_value_args=mob_value_args,
                mob_index_args=mob_index_args,
                index_pos=self.__calc_index_pos(),
                next_to_mob=self.__mob_arr[-1] if len(self.__mob_arr) else None,
                next_to_dir=self.__dir_map[self.__arr_dir.value]["arr"],
            )
        )
        self.add(self.__mob_arr[-1])

        anim_list = [
            append_anim(
                self.__mob_arr[-1].fetch_mob(append_anim_target), **append_anim_args
            )
        ]

        if shift_label:
            label_shift_factor = self.__calc_label_shift_factor(self.__mob_arr[-1])
            anim_list.append(
                ApplyMethod(
                    self.__mob_arr_label.shift,
                    self.__dir_map[self.__arr_dir.value]["arr"] * label_shift_factor,
                )
            )

        return anim_list

    def __remove_elem(
        self,
        index: int,
        removal_anim: Animation = FadeOut,
        update_anim: Animation = Indicate,
        removal_anim_args: dict = {},
        update_anim_args: dict = {},
        removal_anim_target: MArrayElementComp = None,
        update_anim_target: MArrayElementComp = MArrayElementComp.INDEX,
    ) -> Tuple[Succession, Callable[[bool], List[Animation]]]:
        """Removes the element from the array at the specified index.

        Parameters
        ----------
        index
            Specifies the index of the element to remove.
        removal_anim
            Animation to be applied to the element being removed.
        update_anim
            Animation to be applied on remaining elements.
        removal_anim_args
            Arguments for removal :class:`~manim.animation.animation.Animation`.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        removal_anim_target
            Specifies the target :class:`~manim.mobject.mobject.Mobject` of the :class:`~manim_extensions.data_structures.m_array.MArrayElement` on which the removal :class:`~manim.animation.animation.Animation` is to be played.
        update_anim_target
            Specifies the target :class:`~manim.mobject.mobject.Mobject` of the :class:`~manim_extensions.data_structures.m_array.MArrayElement` on which the update :class:`~manim.animation.animation.Animation` is to be played.

        Returns
        -------
        :class:`~manim.animation.composition.Succession`
            Contains :class:`~manim.animation.animation.Animation` played for removal and shifting of element(s).
        :data:`~typing.Callable` [[:class:`bool`], :class:`~typing.List` [:class:`~manim.animation.animation.Animation`]]
            Method that updates the indices of element(s) after the removed element and returns a list of update :class:`~manim.animation.animation.Animation` (s).
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        self.remove(self.__mob_arr[index])
        removed_mob = self.__mob_arr[index]
        self.__mob_arr = self.__mob_arr[0:index] + self.__mob_arr[index + 1 :]

        anims_shift = []
        for i in range(index, len(self.__mob_arr)):
            anims_shift.append(
                ApplyMethod(
                    self.__mob_arr[i].shift,
                    -(
                        self.__dir_map[self.__arr_dir.value]["arr"]
                        * removed_mob.fetch_mob_square().side_length
                    ),
                )
            )

        label_shift_factor = self.__calc_label_shift_factor(removed_mob)

        if label_shift_factor != 0:
            anims_shift.append(
                ApplyMethod(
                    self.__mob_arr_label.shift,
                    -self.__dir_map[self.__arr_dir.value]["arr"] * label_shift_factor,
                )
            )

        def update_indices(
            play_anim: bool = True, play_anim_args: dict = {}
        ) -> List[Animation]:
            """Updates the indices of :class:`~manim_extensions.data_structures.m_array.MArrayElement` (s) that occur after the removal.

            Parameters
            ----------

            play_anim : :class:`bool`, default: `True`
                Specifies whether to play the update :class:`manim.Animation`.
            play_anim_args : :class:`dict`, default: `{}`
                Arguments for :meth:`manim.Scene.play`.

            Returns
            -------

            List[:class:`manim.Animation`]
                Represents :class:`~manim.animation.animation.Animation` for indices update.
            """

            anims_index = []
            for i in range(index, len(self.__mob_arr)):
                self.__mob_arr[i].update_mob_index(
                    mob_index_args={"text": self.__calc_index(i)}, play_anim=False
                )
                anims_index.append(
                    update_anim(
                        (self.__mob_arr[i].fetch_mob(update_anim_target)),
                        **update_anim_args
                    )
                )

            if play_anim:
                self.__scene.play(*anims_index, **play_anim_args)

            return anims_index

        return (
            Succession(
                removal_anim(
                    removed_mob.fetch_mob(removal_anim_target), **removal_anim_args
                ),
                AnimationGroup(*anims_shift),
            ),
            update_indices,
        )

    def __init_props(
        self,
        scene: Scene,
        arr: list,
        label: str,
        index_offset: int,
        index_start: int,
        index_hex_display: bool,
        hide_index: bool,
        arr_dir: MArrayDirection,
        switch_index_pos: bool,
        arr_label_pos: MArrayDirection,
        arr_label_gap: float,
    ) -> None:
        """Initializes the attributes for the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        arr
            Specifies the array to represent.
        label
            Specifies the value of the array label.
        index_offset
            Specifies the difference between successive displayable indices.
        index_start
            Specifies the starting value of displayable index.
        index_hex_display
            If `True`, displays indices in hex.
        hide_index
            If `True`, doesn't display indices.
        arr_dir
            Specifies the growth direction of the array.
        arr_label_pos
            Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
        arr_label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` and :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
        """

        self.__mob_arr_label_props: dict = {
            "text": "",
            "color": BLUE_A,
            "font_size": 38,
        }
        self.__scene: Scene = scene
        self.__arr: List[Any] = arr
        self.__label: str = label
        self.__mob_arr: List[MArrayElement] = []
        self.__index_offset: int = index_offset
        self.__index_start: int = index_start
        self.__index_hex_display: bool = index_hex_display
        self.__hide_index: int = hide_index
        self.__arr_dir: MArrayDirection = arr_dir
        self.__switch_index_pos: bool = switch_index_pos
        self.__arr_label_pos: MArrayDirection = arr_label_pos
        self.__arr_label_gap: float = arr_label_gap

    def __update_props(
        self,
        mob_arr_label_args: dict = {},
    ) -> None:
        """Updates the attributes of the class.

        Parameters
        ----------
        mob_arr_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the array label.
        """

        self.__mob_arr_label_props["text"] = self.__label
        self.__mob_arr_label_props.update(mob_arr_label_args)

        if type(self.__mob_arr_label_props["text"]) != str:
            self.__mob_arr_label_props["text"] = str(self.__mob_arr_label_props["text"])

    def __init_mobs(
        self,
        init_arr_label: bool = False,
    ) -> None:
        """Initializes the mobjects for the class.

        Parameters
        ----------
        init_arr_label
            If `True`, instantiates a :class:`~manim.mobject.text.text_mobject.Text` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label`.
        """

        if init_arr_label:
            self.__mob_arr_label = Text(**self.__mob_arr_label_props)
            if len(self.__mob_arr):
                (next_to_mob, label_pos) = self.__calc_label_pos_and_mob()
                self.__mob_arr_label.next_to(
                    next_to_mob, label_pos, self.__arr_label_gap
                )
                if len(self.__mob_arr) % 2 == 0:
                    self.__mob_arr_label.shift(
                        -self.__dir_map[self.__arr_dir.value]["arr"]
                        * (next_to_mob.side_length / 2)
                    )
            self.add(self.__mob_arr_label)

    def __deepcopy__(self, memo):
        """Deepcopy that excludes attributes specified in `exclude_list`."""

        exclude_list = ["_MArray__scene"]

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in exclude_list:
                setattr(result, k, deepcopy(v, memo))
        return result

    def __init__(
        self,
        scene: Scene,
        arr: list = [],
        label: str = "",
        index_offset: int = 1,
        index_start: int = 0,
        index_hex_display: bool = False,
        hide_index: bool = False,
        arr_dir: MArrayDirection = MArrayDirection.RIGHT,
        switch_index_pos: bool = False,
        arr_label_pos: MArrayDirection = MArrayDirection.LEFT,
        arr_label_gap: float = 0.5,
        mob_arr_label_args: dict = {},
        mob_square_args: dict = {},
        mob_value_args: dict = {},
        mob_index_args: dict = {},
        **kwargs
    ) -> None:
        """Initializes the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        arr
            Specifies the array to represent.
        label
            Specifies the value of the array label.
        index_offset
            Specifies the difference between successive displayable indices.
        index_start
            Specifies the starting value of displayable index.
        index_hex_display
            If `True`, displays indices in hex.
        hide_index
            If `True`, doesn't display indices.
        arr_dir
            Specifies the growth direction of the array.
        arr_label_pos
            Specifies the position of :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` w.r.t :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
        arr_label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label` and :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
        mob_arr_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the array label.
        mob_square_args
            Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
        mob_value_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
        mob_index_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
        **kwargs
            Forwarded to constructor of the parent.
        """

        super().__init__(**kwargs)

        self.__init_props(
            scene,
            arr,
            label,
            index_offset,
            index_start,
            index_hex_display,
            hide_index,
            arr_dir,
            switch_index_pos,
            arr_label_pos,
            arr_label_gap,
        )

        self.__update_props(mob_arr_label_args)

        for v in arr:
            self.__append_elem(
                v,
                False,
                mob_square_args=mob_square_args,
                mob_value_args=mob_value_args,
                mob_index_args=mob_index_args,
            )

        self.__init_mobs(True)

    def fetch_arr(self) -> list:
        """Fetches the original array.

        Returns
        -------
        :class:`list`
            :attr:`~manim_extensions.data_structures.m_array.MArray.__arr`.
        """

        return self.__arr

    def fetch_mob_arr(self) -> List[MArrayElement]:
        """Fetches the mobject array.

        Returns
        -------
        :class:`~typing.List`
            :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr`.
        """

        return self.__mob_arr

    def fetch_mob_arr_label(self) -> Text:
        """Fetches the label mobject of the array.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label`.
        """

        return self.__mob_arr_label

    def fetch_arr_dir(self) -> MArrayDirection:
        """Fetches the growth direction enum of the array.

        Returns
        -------
        :class:`~.m_enum.MArrayDirection`
            :attr:`~manim_extensions.data_structures.m_array.MArray.__arr_dir`.
        """

        return self.__arr_dir

    def update_elem_value(
        self,
        index: int,
        value,
        mob_value_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Updates the elements value.

        Parameters
        ----------
        index
            Specifies the index of element whose value to update.
        value
            New value to be assigned to the element.
        mob_value_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
        update_anim
            Animation to be applied to the updated element.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated element's value mobject.
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        self.__arr[index] = value
        mob_value_args["text"] = value
        return self.__mob_arr[index].update_mob_value(
            mob_value_args, update_anim, update_anim_args, play_anim, play_anim_args
        )

    def update_elem_index(
        self,
        index: int,
        value,
        mob_index_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Updates the elements index.

        Parameters
        ----------
        index
            Specifies the index of element whose index to update.
        value
            New value to be assigned to the index of the element.
        mob_index_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
        update_anim
            Animation to be applied to the updated element.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated element's index mobject.
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        mob_index_args["text"] = value
        return self.__mob_arr[index].update_mob_index(
            mob_index_args, update_anim, update_anim_args, play_anim, play_anim_args
        )

    def update_mob_arr_label(
        self,
        label: str,
        mob_arr_label_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Updates the array label.

        Parameters
        ----------
        label
            New value to be assigned to the array label.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the array label.
        update_anim
            Animation to be applied to the updated array label.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated :attr:`~manim_extensions.data_structures.m_array.MArray.__mob_arr_label`.
        """

        self.__label = label

        self.__update_props(mob_arr_label_args=mob_arr_label_args)

        self.remove(self.__mob_arr_label)

        self.__init_mobs(init_arr_label=True)

        self.add(self.__mob_arr_label)

        if play_anim:
            self.__scene.play(
                update_anim(self.__mob_arr_label, **update_anim_args), **play_anim_args
            )

        return self.__mob_arr_label

    def animate_elem(self, index: int) -> "_AnimationBuilder":
        """Invokes the animate property over element mobject specified.

        Parameters
        ----------
        index
            Specifies the index of the element to animate.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :class:`~manim_extensions.data_structures.m_array.MArrayElement`.
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        return self.__mob_arr[index].animate

    def animate_elem_square(self, index: int) -> "_AnimationBuilder":
        """Invokes the animate property over square mobject of the specified element.

        Parameters
        ----------
        index
            Specifies the index of the element who's square mobject to animate.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :class:`~manim.mobject.geometry.polygram.Square`.
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        return self.__mob_arr[index].animate_mob_square()

    def animate_elem_value(self, index: int) -> "_AnimationBuilder":
        """Invokes the animate property over value mobject of the specified element.

        Parameters
        ----------
        index
            Specifies the index of the element who's value mobject animate.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :class:`~manim.mobject.text.text_mobject.Text`.
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        return self.__mob_arr[index].animate_mob_value()

    def animate_elem_index(self, index: int) -> "_AnimationBuilder":
        """Invokes the animate property over index mobject of the specified element.

        Parameters
        ----------
        index
            Specifies the index of the element who's index mobject animate.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :class:`~manim.mobject.text.text_mobject.Text`.
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        return self.__mob_arr[index].animate_mob_index()

    def append_elem(
        self,
        value: Any,
        append_anim: Animation = Write,
        append_anim_args: dict = {},
        append_anim_target: MArrayElementComp = None,
        mob_square_args: dict = {},
        mob_value_args: dict = {},
        mob_index_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> List[Animation]:
        """Creates and inserts a new element in the array.

        Parameters
        ----------
        value
            Specifies the value of the new element.
        append_anim
            Animation to be applied to the new element.
        append_anim_args
            Arguments for append :class:`~manim.animation.animation.Animation`.
        append_anim_target
            Specifies the target :class:`~manim.mobject.mobject.Mobject` of the :class:`~manim_extensions.data_structures.m_array.MArrayElement` on which the append :class:`~manim.animation.animation.Animation` is to be played.
        mob_square_args
            Arguments for :class:`~manim.mobject.geometry.polygram.Square` that represents the element body.
        mob_value_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element value.
        mob_index_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the element index.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`typing.List` [:class:`~manim.animation.animation.Animation`]
            List of append animations.
        """

        self.__arr.append(value)

        anim_list = self.__append_elem(
            value,
            mob_square_args=mob_square_args,
            mob_value_args=mob_value_args,
            mob_index_args=mob_index_args,
            append_anim=append_anim,
            append_anim_args=append_anim_args,
            append_anim_target=append_anim_target,
        )

        if play_anim:
            self.__scene.play(*anim_list, **play_anim_args)

        return anim_list

    def remove_elem(
        self,
        index: int,
        removal_anim: Animation = FadeOut,
        update_anim: Animation = Indicate,
        removal_anim_args: dict = {},
        update_anim_args: dict = {},
        removal_anim_target: MArrayElementComp = None,
        update_anim_target: MArrayElementComp = MArrayElementComp.INDEX,
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Tuple[Succession, Callable[[bool], List[Animation]]]:
        """Removes the element from the array at the specified index.

        Parameters
        ----------
        index
            Specifies the index of the element to remove.
        removal_anim
            Animation to be applied to the element being removed.
        update_anim
            Animation to be applied on remaining elements.
        removal_anim_args
            Arguments for removal :class:`~manim.animation.animation.Animation`.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        removal_anim_target
            Specifies the target :class:`~manim.mobject.mobject.Mobject` of the :class:`~manim_extensions.data_structures.m_array.MArrayElement` on which the removal :class:`~manim.animation.animation.Animation` is to be played.
        update_anim_target
            Specifies the target :class:`~manim.mobject.mobject.Mobject` of the :class:`~manim_extensions.data_structures.m_array.MArrayElement` on which the update :class:`~manim.animation.animation.Animation` is to be played.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.animation.composition.Succession`
            Contains :class:`~manim.animation.animation.Animation` played for removal and shifting of element(s).
        :data:`~typing.Callable` [[:class:`bool`], :class:`~typing.List` [:class:`~manim.animation.animation.Animation`]]
            Method that updates the indices of element(s) after the removed element and returns a list of update :class:`~manim.animation.animation.Animation` (s).
        """

        if index < 0 or index > len(self.__mob_arr):
            raise Exception("Index out of bounds!")

        self.__arr = self.__arr[0:index] + self.__arr[index + 1 :]

        (remove_anim, update_indices) = self.__remove_elem(
            index,
            removal_anim,
            update_anim,
            removal_anim_args,
            update_anim_args,
            removal_anim_target,
            update_anim_target,
        )

        if play_anim:
            self.__scene.play(remove_anim, **play_anim_args)
            update_indices(play_anim_args=play_anim_args)

        return (remove_anim, update_indices)


class MArrayPointer(VGroup):
    """A class that represents a pointer.

    Parameters
    ----------
    scene
        Specifies the scene where the object is to be rendered.
    arr
        Specifies the array to which the pointer is to be attached.
    index
        Specifies the index of the element to which the pointer is to be attached.
    label
        Specifies the value of the pointer label.
    arrow_len
        Specifies the length of :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
    arrow_gap
        Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
    label_gap
        Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
    pointer_pos
        Specifies the position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
    mob_arrow_args
        Arguments for :class:`~manim.mobject.geometry.line.Arrow` that represents the pointer arrow.
    mob_label_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the pointer label.
    **kwargs
        Forwarded to constructor of the parent.

    Examples
    --------
    .. manim:: MArrayPointerDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.data_structures import (
           MArray, MArrayPointer, MArrayDirection
       )

       class MArrayPointerDocExample(Scene):
           def construct(self):
               arr = MArray(self, [10, 20, 30, 40, 50], label="data")
               ptr = MArrayPointer(
                   self, arr, index=2, label="i",
                   pointer_pos=MArrayDirection.UP
               )
               self.add(arr, ptr)

    Attributes
    ----------
    __scene : :class:`~manim.scene.scene.Scene`
        The scene where the object is to be rendered.
    __arr : :class:`~typing.List` [:class:`~manim_extensions.data_structures.m_array.MArrayElement`]
        The array to which the pointer is attached to.
    __index : :class:`int`
        The index of the element to which the pointer is attached to.
    __label : :class:`str`
        The value of the pointer label.
    __arrow_len : :class:`float`
        The length of :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
    __arrow_gap : :class:`float`
        The distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
    __label_gap : :class:`float`
        The distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
    __pointer_pos : :class:`~manim_extensions.data_structures.m_enum.MArrayDirection`
        The position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
    __mob_arrow_props : :class:`dict`
        Arguments for :class:`~manim.mobject.geometry.line.Arrow` that represents the pointer arrow.
    __mob_label_props : :class:`dict`
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the pointer label.
    __mob_arrow : :class:`~manim.mobject.geometry.line.Arrow`
        Represents the arrow of the element.
    __mob_label : :class:`~manim.mobject.text.text_mobject.Text`
        Represents the label of the element.
    __updater_pos : :data:`~typing.Callable` [[], None]
        The updater function that keeps the pointer intact with the array.
    """

    __dir_map = [
        {"np": UP, "dir": MArrayDirection.UP},
        {"np": DOWN, "dir": MArrayDirection.DOWN},
        {"np": RIGHT, "dir": MArrayDirection.RIGHT},
        {"np": LEFT, "dir": MArrayDirection.LEFT},
    ]
    """Maps :class:`~.m_enum.MArrayDirection` to :class:`numpy.ndarray`."""

    def __calc_arrow_pos(self) -> np.ndarray:
        """Calculates direction vector for the arrow mobject.

        Returns
        -------
        :class:`numpy.ndarray`
            Position vector for :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
        """

        arr_dir_np = self.__dir_map[self.__arr.fetch_arr_dir().value]["np"]
        arrow_pos_np = np.copy(self.__dir_map[self.__pointer_pos.value]["np"])

        if np.dot(arr_dir_np, arrow_pos_np):
            arrow_pos_np[0], arrow_pos_np[1] = arrow_pos_np[1], arrow_pos_np[0]
            self.__pointer_pos = self.__dir_map[
                (self.__pointer_pos.value + 2) % len(self.__dir_map)
            ]["dir"]

        return arrow_pos_np

    def __add_updater(self) -> None:
        """Attaches the position updater function with the pointer."""

        def updater_pos(mob: Mobject) -> None:
            self.__init_pos()

        self.__updater_pos = updater_pos

        self.add_updater(self.__updater_pos)

    def __remove_updater(self) -> None:
        """Removes the attached position updater function from the pointer."""

        self.remove_updater(self.__updater_pos)

    def __calc_shift_np(self, new_index: int) -> np.ndarray:
        """Calculates how much the pointer should shift by to point to the new index.

        Parameters
        ----------
        new_index
            Specifies the prospective index of element to which the pointer is to be attached.

        Returns
        -------
        :class:`numpy.ndarray`
            A vector that represents how much the pointer should shift.
        """

        to_lesser_index = False
        index_start = self.__index
        index_end = new_index
        if index_start > index_end:
            index_start, index_end = index_end, index_start
            to_lesser_index = True

        return (
            (
                self.__arr._MArray__sum_elem_len(index_start, index_end)
                - (
                    self.__arr.fetch_mob_arr()[self.__index]
                    .fetch_mob_square()
                    .side_length
                )
            )
            * self.__dir_map[self.__arr.fetch_arr_dir().value]["np"]
            * (-1 if to_lesser_index else 1)
        )

    def __init_props(
        self,
        scene: Scene,
        arr: MArray,
        index: int,
        label: str,
        arrow_len: float,
        arrow_gap: float,
        label_gap: float,
        pointer_pos: MArrayDirection,
    ) -> None:
        """Initializes the attributes for the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        arr
            Specifies the array to which the pointer is to be attached.
        index
            Specifies the index of the element to which the pointer is to be attached.
        label
            Specifies the value of the pointer label.
        arrow_len
            Specifies the length of :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
        arrow_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
        label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
        pointer_pos
            Specifies the position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
        """

        self.__mob_arrow_props: dict = {"color": GOLD_D}
        self.__mob_label_props: dict = {"text": label, "color": GOLD_A, "font_size": 38}
        self.__scene: Scene = scene
        self.__arr: MArray = arr
        if index >= len(self.__arr.fetch_mob_arr()) or index < 0:
            raise Exception("Index out of bounds!")
        self.__index: int = index
        self.__label: str = label
        self.__arrow_len: float = arrow_len
        self.__arrow_gap: float = arrow_gap
        self.__label_gap: float = label_gap
        self.__pointer_pos: MArrayDirection = pointer_pos

    def __update_props(
        self, mob_arrow_args: dict = {}, mob_label_args: dict = {}
    ) -> None:
        """Updates the attributes of the class.

        Parameters
        ----------
        mob_arrow_args
            Arguments for :class:`~manim.mobject.geometry.line.Arrow` that represents the pointer arrow.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the pointer label.
        """

        self.__mob_arrow_props.update(mob_arrow_args)
        self.__mob_label_props["text"] = self.__label
        self.__mob_label_props.update(mob_label_args)

        if type(self.__mob_label_props["text"]) != str:
            self.__mob_label_props["text"] = str(self.__mob_label_props["text"])

    def __init_mobs(self, init_arrow: bool = False, init_label: bool = False) -> None:
        """Initializes the mobjects for the class.

        Parameters
        ----------
        init_arrow
            If `True`, instantiates a :class:`~manim.mobject.geometry.line.Arrow` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
        init_label
            If `True`, instantiates a :class:`~manim.mobject.text.text_mobject.Text` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
        """

        if init_arrow:
            arrow_pos_np = self.__calc_arrow_pos()
            self.__mob_arrow = Arrow(
                start=(-arrow_pos_np + (arrow_pos_np * self.__arrow_len)),
                end=-arrow_pos_np,
                **self.__mob_arrow_props
            )
            self.__mob_arrow.next_to(
                self.__arr.fetch_mob_arr()[self.__index].fetch_mob_square(),
                arrow_pos_np,
                self.__arrow_gap,
            )
            self.add(self.__mob_arrow)

        if init_label:
            self.__mob_label = Text(**self.__mob_label_props)
            self.__mob_label.next_to(
                self.__mob_arrow,
                self.__dir_map[self.__pointer_pos.value]["np"],
                self.__label_gap,
            )
            self.add(self.__mob_label)

    def __init_pos(self) -> None:
        """Initializes the position of the object"""

        arrow_pos_np = self.__calc_arrow_pos()
        self.next_to(
            self.__arr.fetch_mob_arr()[self.__index].fetch_mob_square(),
            arrow_pos_np,
            self.__arrow_gap,
        )

    def __deepcopy__(self, memo):
        """Deepcopy that excludes attributes specified in `exclude_list`."""

        exclude_list = ["_MArrayPointer__scene", "_MArrayPointer__arr"]

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in exclude_list:
                setattr(result, k, deepcopy(v, memo))
        return result

    def __init__(
        self,
        scene: Scene,
        arr: MArray,
        index: int = 0,
        label: str = "",
        arrow_len: float = 1,
        arrow_gap: float = 0.25,
        label_gap: float = 0.25,
        pointer_pos: MArrayDirection = MArrayDirection.DOWN,
        mob_arrow_args: dict = {},
        mob_label_args: dict = {},
        **kwargs
    ) -> None:
        """Initializes the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        arr
            Specifies the array to which the pointer is to be attached.
        index
            Specifies the index of the element to which the pointer is to be attached.
        label
            Specifies the value of the pointer label.
        arrow_len
            Specifies the length of :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
        arrow_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
        label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow` and :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
        pointer_pos
            Specifies the position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__arr`.
        mob_arrow_args
            Arguments for :class:`~manim.mobject.geometry.line.Arrow` that represents the pointer arrow.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the pointer label.
        **kwargs
            Forwarded to constructor of the parent.
        """

        super().__init__(**kwargs)

        self.__init_props(
            scene, arr, index, label, arrow_len, arrow_gap, label_gap, pointer_pos
        )

        self.__update_props(mob_arrow_args, mob_label_args)

        self.__init_mobs(True, True)

        self.__add_updater()

    def fetch_mob_arrow(self) -> Arrow:
        """Fetches the arrow mobject of the pointer.

        Returns
        -------
        :class:`~manim.mobject.geometry.line.Arrow`
            :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
        """

        return self.__mob_arrow

    def fetch_mob_label(self) -> Text:
        """Fetches the label mobject of the pointer.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
        """

        return self.__mob_label

    def fetch_index(self) -> int:
        """Fetches the index that the pointer is attached to.

        Returns
        -------
        :class:`int`
            :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__index`.
        """

        return self.__index

    def update_mob_label(
        self,
        label: str,
        mob_label_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Updates the pointer label.

        Parameters
        ----------
        label
            New value to be assigned to the pointer label.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the pointer label.
        update_anim
            Animation to be applied to the updated pointer label.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
        """

        self.__label = label

        self.__update_props(mob_label_args=mob_label_args)

        self.remove(self.__mob_label)

        self.__init_mobs(init_label=True)

        self.add(self.__mob_label)

        if play_anim:
            self.__scene.play(
                update_anim(self.__mob_label, **update_anim_args), **play_anim_args
            )

        return self.__mob_label

    def animate_mob_arrow(self) -> "_AnimationBuilder":
        """Invokes the animate property over arrow mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_arrow`.
        """

        return self.__mob_arrow.animate

    def animate_mob_label(self) -> "_AnimationBuilder":
        """Invokes the animate property over label mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArrayPointer.__mob_label`.
        """

        return self.__mob_label.animate

    def shift_to_elem(
        self, index: int, play_anim: bool = True, play_anim_args: dict = {}
    ) -> ApplyMethod:
        """Shifts pointer to the specified element.

        Parameters
        ----------
        index
            Specifies the index of the element to which the pointer is to be shifted.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.animation.transform.ApplyMethod`
            Shift animation.
        """

        if index < 0 or index > len(self.__arr.fetch_mob_arr()):
            raise Exception("Index out of bounds!")

        shift_anim = ApplyMethod(
            self.shift, self.__calc_shift_np(index), suspend_mobject_updating=True
        )
        self.__index = index

        if play_anim:
            self.__scene.play(shift_anim, **play_anim_args)

        return shift_anim

    def attach_to_elem(self, index: int) -> None:
        """Attaches pointer to the specified element.

        Parameters
        ----------
        index
            Specifies the index of the element to which the pointer is to be attached.
        """

        if index < 0 or index > len(self.__arr.fetch_mob_arr()):
            raise Exception("Index out of bounds!")

        self.__index = index
        self.__init_pos()


class MArraySlidingWindow(VGroup):
    """A class that represents a sliding window.

    Parameters
    ----------
    scene
        Specifies the scene where the object is to be rendered.
    arr
        Specifies the array to which the sliding window is to be attached.
    index
        Specifies the index of the element to which the sliding window is to be attached.
    size
        Specifies the number of elements the sliding window should enclose.
    label
        Specifies the value of the sliding window label.
    label_gap
        Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
    label_pos
        Specifies the position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
    mob_window_args
        Arguments for :class:`~manim.mobject.geometry.polygram.Rectangle` that represents the window.
    mob_label_args
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the window label.
    **kwargs
        Forwarded to constructor of the parent.

    Examples
    --------
    .. manim:: MArraySlidingWindowDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.data_structures import (
           MArray, MArraySlidingWindow, MArrayDirection
       )

       class MArraySlidingWindowDocExample(Scene):
           def construct(self):
               arr = MArray(self, [7, 2, 5, 1, 8, 3, 6, 4], label="nums")
               window = MArraySlidingWindow(
                   self, arr, index=1, size=3, label="window",
                   label_pos=MArrayDirection.UP
               )
               self.add(arr, window)

    Attributes
    ----------
    __scene : :class:`~manim.scene.scene.Scene`
        The scene where the object is to be rendered.
    __arr : :class:`~typing.List` [:class:`~manim_extensions.data_structures.m_array.MArrayElement`]
        The array to which the sliding window is to be attached.
    __index : :class:`int`
        The index of the element to which the sliding window is to be attached.
    __size : :class:`int`
        The number of elements the sliding window should enclose.
    __label : :class:`str`
        The value of the sliding window label.
    __label_gap : :class:`float`
        The distance between :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
    __label_pos : :class:`~.m_enum.MArrayDirection`
        The position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
    __mob_window_props : :class:`dict`
        Arguments for :class:`~manim.mobject.geometry.polygram.Rectangle` that represents the window.
    __mob_label_props : :class:`dict`
        Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the window label.
    __mob_window : :class:`~manim.mobject.geometry.polygram.Rectangle`
        Represents the window of the sliding window.
    __mob_label : :class:`~manim.mobject.text.text_mobject.Text`
        Represents the label of the sliding window.
    __updater_pos : :data:`typing.Callable` [[], None]
        The updater function that keeps the sliding window intact with the array.
    """

    __dir_map = [
        {"np": UP, "dir": MArrayDirection.UP},
        {"np": DOWN, "dir": MArrayDirection.DOWN},
        {"np": RIGHT, "dir": MArrayDirection.RIGHT},
        {"np": LEFT, "dir": MArrayDirection.LEFT},
    ]
    """Maps :class:`~.m_enum.MArrayDirection` to :class:`numpy.ndarray`."""

    def __calc_window_dim(self) -> Tuple[float, float]:
        """Calculates dimensions of window mobject.

        Returns
        -------
        :class:`float`
            Height of :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        :class:`float`
            Width of :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        """

        height = self.__arr.fetch_mob_arr()[self.__index].fetch_mob_square().side_length
        width = self.__arr._MArray__sum_elem_len(
            self.__index, self.__index + self.__size - 1
        )

        if self.__arr.fetch_arr_dir() in (MArrayDirection.UP, MArrayDirection.DOWN):
            height, width = width, height

        return (height, width)

    def __calc_window_pos_np(self) -> Tuple[np.ndarray, np.ndarray]:
        """Calculates position vector and align vector for the window mobject.

        Returns
        -------
        :class:`numpy.ndarray`
            Position vector for :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`
        :class:`numpy.ndarray`
            Align vector for :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`
        """

        point_np = (
            self.__arr.fetch_mob_arr()[self.__index].fetch_mob_square().get_left()
        )
        align_np = LEFT

        arr_dir = self.__arr.fetch_arr_dir()
        if arr_dir == MArrayDirection.LEFT:
            point_np = (
                self.__arr.fetch_mob_arr()[self.__index].fetch_mob_square().get_right()
            )
            align_np = RIGHT
        elif arr_dir == MArrayDirection.UP:
            point_np = (
                self.__arr.fetch_mob_arr()[self.__index].fetch_mob_square().get_bottom()
            )
            align_np = DOWN
        elif arr_dir == MArrayDirection.DOWN:
            point_np = (
                self.__arr.fetch_mob_arr()[self.__index].fetch_mob_square().get_top()
            )
            align_np = UP

        return (point_np, align_np)

    def __calc_label_pos_np(self) -> np.ndarray:
        """Calculates position vector for the label mobject.

        Returns
        -------
        :class:`numpy.ndarray`
            Position vector for :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label`
        """

        arr_dir = self.__arr.fetch_arr_dir()
        if np.array_equal(
            self.__dir_map[self.__label_pos.value]["np"],
            self.__dir_map[arr_dir.value]["np"],
        ) or np.array_equal(
            self.__dir_map[self.__label_pos.value]["np"],
            -self.__dir_map[arr_dir.value]["np"],
        ):
            return self.__dir_map[(self.__label_pos.value + 2) % len(self.__dir_map)][
                "np"
            ]

        else:
            return self.__dir_map[self.__label_pos.value]["np"]

    def __pos_mobs(self, pos_window: bool = False, pos_label: bool = False) -> None:
        """Positions mobjects of the class.

        Parameters
        ----------
        pos_window
            If `True`, correctly positions :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        pos_label
            If `True`, correctly positions :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label`.
        """

        if pos_window:
            point_np, align_np = self.__calc_window_pos_np()
            self.__mob_window.move_to(point_np, align_np)

        if pos_label:
            self.__mob_label.next_to(
                self.__mob_window,
                self.__calc_label_pos_np(),
                self.__label_gap,
            )

    def __add_updater(self) -> None:
        """Attaches the position updater function with the pointer."""

        def updater_pos(mob: Mobject) -> None:
            self.__init_pos()

        self.__updater_pos = updater_pos

        self.add_updater(self.__updater_pos)

    def __remove_updater(self) -> None:
        """Removes the attached position updater function from the pointer."""

        self.remove_updater(self.__updater_pos)

    def __init_props(
        self,
        scene: Scene,
        arr: MArray,
        index: int,
        size: int,
        label: str,
        label_gap: float,
        label_pos: MArrayDirection,
    ) -> None:
        """Initializes the attributes for the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        arr
            Specifies the array to which the sliding window is to be attached.
        index
            Specifies the index of the element to which the sliding window is to be attached.
        size
            Specifies the number of elements the sliding window should enclose.
        label
            Specifies the value of the sliding window label.
        label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        label_pos
            Specifies the position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        """

        self.__mob_window_props: dict = {"color": RED_D, "stroke_width": 10}
        self.__mob_label_props: dict = {"text": label, "color": RED_A, "font_size": 38}
        self.__scene: Scene = scene
        self.__arr: MArray = arr
        if index >= len(self.__arr.fetch_mob_arr()) or index < 0:
            raise Exception("Index out of bounds!")
        self.__index: int = index
        if size < 1 or index + size > len(self.__arr.fetch_mob_arr()):
            raise Exception("Invalid window size!")
        self.__size: int = size
        self.__label: str = label
        self.__label_gap: float = label_gap
        self.__label_pos: MArrayDirection = label_pos

    def __update_props(
        self, mob_window_args: dict = {}, mob_label_args: dict = {}
    ) -> None:
        """Updates the attributes of the class.

        Parameters
        ----------
        mob_window_args
            Arguments for :class:`~manim.mobject.geometry.polygram.Rectangle` that represents the window.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the window label.
        """

        self.__mob_window_props.update(mob_window_args)
        self.__mob_label_props["text"] = self.__label
        self.__mob_label_props.update(mob_label_args)

        if type(self.__mob_label_props["text"]) != str:
            self.__mob_label_props["text"] = str(self.__mob_label_props["text"])

    def __init_mobs(self, init_window: bool = False, init_label: bool = False) -> None:
        """Initializes the mobjects for the class.

        Parameters
        ----------
        init_arrow
            If `True`, instantiates a :class:`~manim.mobject.geometry.polygram.Rectangle` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        init_label
            If `True`, instantiates a :class:`~manim.mobject.text.text_mobject.Text` and assigns it to :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label`.
        """

        if init_window:
            height, width = self.__calc_window_dim()
            self.__mob_window = Rectangle(
                height=height, width=width, **self.__mob_window_props
            )
            self.__pos_mobs(pos_window=True)
            self.add(self.__mob_window)

        if init_label:
            self.__mob_label = Text(**self.__mob_label_props)
            self.__pos_mobs(pos_label=True)
            self.add(self.__mob_label)

    def __init_pos(self) -> None:
        """Initializes the position of the object"""

        self.__pos_mobs(True, True)

    def __deepcopy__(self, memo):
        """Deepcopy that excludes attributes specified in `exclude_list`."""

        exclude_list = ["_MArraySlidingWindow__scene", "_MArraySlidingWindow__arr"]

        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k not in exclude_list:
                setattr(result, k, deepcopy(v, memo))
        return result

    def __init__(
        self,
        scene: Scene,
        arr: MArray,
        index: int = 0,
        size: int = 1,
        label: str = "",
        label_gap: float = 0.5,
        label_pos: MArrayDirection = MArrayDirection.DOWN,
        mob_window_args: dict = {},
        mob_label_args: dict = {},
        **kwargs
    ) -> None:
        """Initializes the class.

        Parameters
        ----------
        scene
            Specifies the scene where the object is to be rendered.
        arr
            Specifies the array to which the sliding window is to be attached.
        index
            Specifies the index of the element to which the sliding window is to be attached.
        size
            Specifies the number of elements the sliding window should enclose.
        label
            Specifies the value of the sliding window label.
        label_gap
            Specifies the distance between :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label` and :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        label_pos
            Specifies the position of the pointer w.r.t to :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        mob_window_args
            Arguments for :class:`~manim.mobject.geometry.polygram.Rectangle` that represents the window.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the window label.
        **kwargs
            Forwarded to constructor of the parent.
        """

        super().__init__(**kwargs)

        self.__init_props(scene, arr, index, size, label, label_gap, label_pos)

        self.__update_props(mob_window_args, mob_label_args)

        self.__init_mobs(True, True)

        self.__add_updater()

    def fetch_mob_window(self) -> Rectangle:
        """Fetches the window mobject of the sliding window.

        Returns
        -------
        :class:`~manim.mobject.geometry.polygram.Rectangle`
            :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        """

        return self.__mob_window

    def fetch_mob_label(self) -> Text:
        """Fetches the label mobject of the sliding window.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label`.
        """

        return self.__mob_label

    def update_mob_label(
        self,
        label: str,
        mob_label_args: dict = {},
        update_anim: Animation = Write,
        update_anim_args: dict = {},
        play_anim: bool = True,
        play_anim_args: dict = {},
    ) -> Text:
        """Updates the window label.

        Parameters
        ----------
        label
            New value to be assigned to the window label.
        mob_label_args
            Arguments for :class:`~manim.mobject.text.text_mobject.Text` that represents the window label.
        update_anim
            Animation to be applied to the updated window label.
        update_anim_args
            Arguments for update :class:`~manim.animation.animation.Animation`.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.mobject.text.text_mobject.Text`
            Updated :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label`.
        """

        self.__label = label

        self.__update_props(mob_label_args=mob_label_args)

        self.remove(self.__mob_label)

        self.__init_mobs(init_label=True)

        self.add(self.__mob_label)

        if play_anim:
            self.__scene.play(
                update_anim(self.__mob_label, **update_anim_args), **play_anim_args
            )

        return self.__mob_label

    def animate_mob_window(self) -> "_AnimationBuilder":
        """Invokes the animate property over window mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_window`.
        """

        return self.__mob_window.animate

    def animate_mob_label(self) -> "_AnimationBuilder":
        """Invokes the animate property over label mobject.

        Returns
        -------
        :class:`~manim.mobject.mobject._AnimationBuilder`
            Animate property of :attr:`~manim_extensions.data_structures.m_array.MArraySlidingWindow.__mob_label`.
        """

        return self.__mob_label.animate

    def shift_to_elem(
        self, index: int, play_anim: bool = True, play_anim_args: dict = {}
    ) -> ApplyFunction:
        """Shifts sliding window to the specified element.

        Parameters
        ----------
        index
            Specifies the index of the element to which the sliding window is to be shifted.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.animation.transform.ApplyFunction`
            Shift animation.
        """

        if index >= len(self.__arr.fetch_mob_arr()) or index < 0:
            raise Exception("Index out of bounds!")

        if self.__size < 1 or index + self.__size > len(self.__arr.fetch_mob_arr()):
            raise Exception("Invalid window size!")

        self.__index = index
        return self.resize_window(self.__size, play_anim, play_anim_args)

    def attach_to_elem(self, index: int) -> None:
        """Attaches pointer to the specified element.

        Parameters
        ----------
        index
            Specifies the index of the element to which the sliding window is to be attached.
        """

        if index >= len(self.__arr.fetch_mob_arr()) or index < 0:
            raise Exception("Index out of bounds!")

        if self.__size < 1 or index + self.__size > len(self.__arr.fetch_mob_arr()):
            raise Exception("Invalid window size!")

        self.__index = index
        self.__init_pos()

    def resize_window(
        self, size: int, play_anim: bool = True, play_anim_args: dict = {}
    ) -> ApplyFunction:
        """Expands or shrinks the window according to the specified size.

        Parameters
        ----------
        size
            Specifies the number of elements the sliding window should enclose.
        play_anim
            If `True`, plays the animation(s).
        play_anim_args
            Arguments for :meth:`~manim.scene.scene.Scene.play() <manim.scene.scene.Scene.play>`.

        Returns
        -------
        :class:`~manim.animation.transform.ApplyFunction`
            Resize animation.
        """

        if size < 1 or self.__index + size > len(self.__arr.fetch_mob_arr()):
            raise Exception("Invalid window size!")

        self.__size = size

        arr_dir = self.__arr.fetch_arr_dir()
        height, width = self.__calc_window_dim()
        window_pos_np, window_align_np = self.__calc_window_pos_np()
        label_pos_np = self.__calc_label_pos_np()

        def resize_and_shift(mob: MArraySlidingWindow) -> MArraySlidingWindow:
            """Resizes and shifts the sliding window

            Returns
            -------

            :class:`~manim_extensions.data_structures.m_array.MArraySlidingWindow`
                Represents the modified mobject.
            """

            if arr_dir in (MArrayDirection.UP, MArrayDirection.DOWN):
                mob.__mob_window.stretch_to_fit_height(height)
            else:
                mob.__mob_window.stretch_to_fit_width(width)
            mob.__mob_window.move_to(window_pos_np, window_align_np)
            mob.__mob_label.next_to(mob.__mob_window, label_pos_np, mob.__label_gap)
            return mob

        resize_anim = ApplyFunction(
            resize_and_shift, self, suspend_mobject_updating=True
        )

        if play_anim:
            self.__scene.play(resize_anim, **play_anim_args)

        return resize_anim