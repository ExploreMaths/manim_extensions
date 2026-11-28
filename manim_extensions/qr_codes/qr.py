# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: use vendored manim_extensions.nerdfont instead of the manim-nerdfont-icons package; lazy-import segno (qr extra)

"""QR code generation for Manim.

This module provides QR code generation functionality with customization options.
"""

from typing import Any, Literal

from types import ModuleType

from manim import Circle, DOWN, ManimColor, ORIGIN, RIGHT, Rectangle, VGroup, WHITE

from ..utils.deps import require


class QRCode(VGroup):
    """A QR code rendered as a Manim group.

    The payload is encoded with segno and converted into one Manim mobject per
    dark module. The three finder patterns use ``corner_color`` and can be
    sized independently of the data modules. An optional Nerd Font icon is
    placed in the centre, and the modules underneath it are removed.

    Parameters
    ----------
    payload
        The data to encode in the QR code.
    corner_size
        The size of the corner elements in QR pixels. Might need to be
        adjusted for larger or very small QR codes.
    icon
        A Nerd Font icon to place in the center of the QR code, either an
        icon name or a Unicode code point. See the `Icon Gallery
        <https://manim-extensions.readthedocs.io/en/latest/reference/nerdfont/icon_gallery.html>`_
        for available icons.
    icon_color
        The color of the icon.
    icon_size
        The size of the icon in QR pixels. Pixels in the middle of the QR
        code are removed to make space for the icon.
    icon_margin_size
        A margin around the icon in QR pixels; the space left around the
        icon.
    white_color
        The color of the rectangles or data points, which are typically
        white in a QR code.
    corner_color
        The color for the corner elements of the QR code.
    data_shape
        Shape of the data modules; either ``'rectangles'`` or ``'circles'``.
    rectangles_kwargs
        Additional keyword arguments for the rectangles, which represent
        the QR code data.
    circle_kwargs
        Additional keyword arguments for the circles, which represent the
        QR code data.
    error_correction
        The error correction level for the QR code, as accepted by
        :func:`~segno.make`.
    segno_kwargs
        Additional keyword arguments for the :func:`~segno.make` function.
    **kwargs
        Keyword arguments forwarded to
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Raises
    ------
    ValueError
        Raised when ``data_shape`` is not one of ``'circles'`` or
        ``'rectangles'``.

    Examples
    --------
    .. manim:: QRCodeScene
       :save_last_frame:

       from manim import *
       from manim_extensions.qr_codes import QRCode

       class QRCodeScene(Scene):
           def construct(self):
               plain = QRCode("https://fishshell.com")
               with_icon = QRCode(
                   payload="https://fishshell.com",
                   icon="terminal",
                   icon_size=6,
               )
               group = VGroup(plain, with_icon).arrange(RIGHT, buff=0.75)
               label = Text("https://fishshell.com")
               label.to_edge(UP, buff=0.75)
               self.add(group, label)

    .. manim:: QRCodeShapes
       :save_last_frame:

       from manim import *
       from manim_extensions.qr_codes import QRCode

       class QRCodeShapes(Scene):
           def construct(self):
               rust = QRCode("https://www.rust-lang.org/", icon="language-rust",
                             data_shape="circles")
               python = QRCode("https://www.python.org/", icon="language-python",
                               data_shape="circles", corner_color=BLUE,
                               icon_color=YELLOW, icon_size=4)
               group = VGroup(rust, python).arrange(RIGHT, buff=0.5)
               group.scale(0.8)
               self.add(group)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        payload: str,
        corner_size: int = 7,
        icon: str | int | None = None,
        icon_color: str | ManimColor | None = None,
        icon_size: float = 10,  # in qr pixel
        icon_margin_size: float = 0.1,  # in qr pixel
        white_color: str | ManimColor | None = None,
        corner_color: str | ManimColor | None = None,
        data_shape: Literal["rectangles", "circles"] = "rectangles",
        rectangles_kwargs: dict[str, object] | None = None,
        circle_kwargs: dict[str, object] | None = None,
        error_correction: Literal["L", "M", "Q", "H"] = "H",
        segno_kwargs: dict[str, object] | None = None,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        super().__init__(**kwargs)
        if icon_color is None:
            icon_color = WHITE
        if white_color is None:
            white_color = WHITE
        if corner_color is None:
            corner_color = white_color
        if data_shape not in ["circles", "rectangles"]:
            raise ValueError(
                f"Invalid data_shape: {data_shape}. valid values are 'circles' and 'rectangles'"
            )
        segno: ModuleType = require("qr", "segno")  # segno ships no type stubs
        if rectangles_kwargs is None:
            rectangles_kwargs = {}
        if circle_kwargs is None:
            circle_kwargs = {}
        if segno_kwargs is None:
            segno_kwargs = {}

        # Create a QR code with the given data
        qr = segno.make(payload, error=error_correction, **segno_kwargs)

        # Get the dimensions of the QR code
        matrix = qr.matrix
        size = len(matrix)

        # Define the positions of the corner elements
        corner_positions = set()
        for i in range(corner_size):
            for j in range(corner_size):
                corner_positions.add((i, j))
                corner_positions.add((i, size - 1 - j))
                corner_positions.add((size - 1 - i, j))

        # Create groups for the data modules and the corner elements
        qr_data_group = VGroup()
        qr_corner_group = VGroup()

        # Draw a rectangle or circle for each module of the QR code, except for the corner elements
        for y, row in enumerate(matrix):
            for x, is_white_qr_pixel in enumerate(row):
                current_elem: Rectangle | Circle | None = None

                if data_shape == "rectangles" and is_white_qr_pixel:
                    default_rect_kwargs: dict[str, Any] = (
                        {  # explicit-any-ok: heterogeneous Manim style keyword arguments
                            "width": 1,
                            "height": 1,
                            "fill_opacity": 1,
                            "color": white_color,
                            "stroke_width": 0.5,
                        }
                    )
                    rect_kwargs: dict[str, Any] = (
                        {  # explicit-any-ok: heterogeneous Manim style keyword arguments
                            **default_rect_kwargs,
                            **rectangles_kwargs,
                        }
                    )

                    rect = Rectangle(**rect_kwargs)
                    rect.move_to(DOWN * y + RIGHT * x)
                    current_elem = rect

                elif data_shape == "circles" and is_white_qr_pixel:
                    default_circle_kwargs: dict[str, Any] = (
                        {  # explicit-any-ok: heterogeneous Manim style keyword arguments
                            "radius": 0.5,
                            "fill_opacity": 1,
                            "color": white_color,
                            "stroke_width": 0.5,
                        }
                    )
                    circle_style: dict[str, Any] = (
                        {  # explicit-any-ok: heterogeneous Manim style keyword arguments
                            **default_circle_kwargs,
                            **circle_kwargs,
                        }
                    )
                    circle = Circle(**circle_style)
                    circle.move_to(DOWN * y + RIGHT * x)
                    current_elem = circle

                # override current_elem if it is a corner element
                if is_white_qr_pixel and (x, y) in corner_positions:
                    default_corner_kwargs: dict[str, Any] = (
                        {  # explicit-any-ok: heterogeneous Manim style keyword arguments
                            "width": 1,
                            "height": 1,
                            "fill_opacity": 1,
                            "color": corner_color,
                            "stroke_width": 0.5,
                        }
                    )
                    corner_kwargs: dict[str, Any] = (
                        {  # explicit-any-ok: heterogeneous Manim style keyword arguments
                            **default_corner_kwargs,
                            **rectangles_kwargs,
                        }
                    )
                    rect = Rectangle(**corner_kwargs)
                    rect.move_to(DOWN * y + RIGHT * x)
                    current_elem = rect

                    qr_corner_group.add(current_elem)
                    continue

                if current_elem is not None:
                    qr_data_group.add(current_elem)

        self.add(qr_corner_group, qr_data_group)
        self.move_to(ORIGIN)

        if icon is not None:
            # add icon to the center
            from ..nerdfont import NerdFontIcon

            center_icon = NerdFontIcon(icon)
            center_icon.set_color(icon_color)
            # scale icon to fit the qr center mask

            # if width is larger than height, then scale by using scale_to_fit_width
            # else scale by using scale_to_fit_height
            if center_icon.width > center_icon.height:
                center_icon.scale_to_fit_width(icon_size - 2 * icon_margin_size)
            else:
                center_icon.scale_to_fit_height(icon_size - 2 * icon_margin_size)

            center_icon_bounding_box = Rectangle(
                width=icon_size, height=icon_size, fill_opacity=0, stroke_width=0
            )
            # filter out all the qr pixels that are inside the icon bounding box
            for qr_pixel in list(qr_data_group):
                pixel_x, pixel_y, _ = qr_pixel.get_center()

                box_min_x = center_icon_bounding_box.get_left()[0]
                box_max_x = center_icon_bounding_box.get_right()[0]

                box_min_y = center_icon_bounding_box.get_bottom()[1]
                box_max_y = center_icon_bounding_box.get_top()[1]

                if (
                    box_min_x <= pixel_x <= box_max_x
                    and box_min_y <= pixel_y <= box_max_y
                ):
                    qr_data_group.remove(qr_pixel)

            self.add(center_icon)

        self.scale_to_fit_width(2)
