# SPDX-FileCopyrightText: 2023 Thomas Chen
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *

class SeqObject(VGroup):
    """Named object shown inside a sequence diagram.

    Parameters
    ----------
        name : str
            Object name displayed inside the box.
        font_size : float, optional
            Font size of the label. Defaults to ``18``.

    Examples
    --------
    .. manim:: SeqObjectExample
       :save_last_frame:

       from manim import *
       from manim_extensions.sequence_diagram.seq_object import SeqObject

       class SeqObjectExample(Scene):
           def construct(self):
               obj = SeqObject("MyService")
               self.add(obj)
               """

    def __init__(
        self,
        name: str,
        font_size: float = 18
    ):
        """Initialize SeqObject."""
        self.obj_name = name
        obj_label = self.create_obj_label(font_size)
        obj_ctn = Rectangle(
            color='#00FF00',
            height=obj_label.height + 0.5,
            width=obj_label.width + 0.4
        )
        # TODO: figure out a way to show json data
        # or alternatively code snippets
        obj_label.align_to(obj_ctn, ORIGIN)
        super().__init__(obj_ctn, obj_label)

    def create_obj_label(self, font_size: float = 18):
        """Build the text label shown inside the object box.

        Parameters
        ----------
        font_size : float, optional
            Font size used for the label (default ``18``).

        Returns
        -------
        Text
            A white :class:`~manim.mobject.text.text_mobject.Text` mobject
            displaying the object name.
        """
        return Text(self.obj_name, font_size=font_size).set_color(WHITE)