# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""QR code generation for Manim.

This module provides QR code generation functionality with customization options.

"""

import manim as m
import segno


def qr_code(payload: str,
            corner_size=7,
            icon: str | int | None = None,
            icon_color: str = None,
            icon_size: float = 10,  # in qr pixel
            icon_margin_size: float = 0.1,  # in qr pixel
            white_color: str = None,
            corner_color: str = None,
            data_shape: str = 'rectangles',
            rectangles_kwargs: dict = None,
            circle_kwargs: dict = None,
            error_correction='H',
            segno_kwargs: dict = None,
            **kwargs, ) -> m.VGroup:
    """
    Create a QR code as a VGroup of Manim objects.
    This function uses the segno library to generate a QR code and then converts it into Manim objects.

    :param payload:             the data to encode in the QR code
    :param corner_size:         the size of the corner elements in QR pixels. might need to be adjusted for larger
                                or very small QR codes.
    :param icon:                a Nerd Font icon to place in the center of the QR code.
                                see https://manim-nerdfont-icons.readthedocs.io/en/latest/icon-gallery.html
                                for available icons.
    :param icon_color:          the color of the icon. defaults to white.
    :param icon_size:           the size of the icon in QR pixels. Pixels in the middle of the QR code will be removed
                                to make space for the icon. Here you can specify the size of the icon in QR pixels.
    :param icon_margin_size:    a margin around the icon in QR pixels. This is the space that will be left around the icon.
    :param white_color:         the color of the rectangles or datapoints that are typically white in a QR code.
    :param corner_color:        set a color for the corner elements of the QR code.
    :param data_shape:          can be either 'rectangles' or 'circles'.
    :param rectangles_kwargs:   additional keyword arguments for the rectangles that represent the QR code data.
    :param circle_kwargs:       additional keyword arguments for the circles that represent the QR code data.
    :param error_correction:    the error correction level for the QR code.
    :param segno_kwargs:        additional keyword arguments for the segno.make() function.
    :param kwargs:              placeholder for additional keyword arguments that are not used in this function.
    :return:                    a VGroup containing the QR code as Manim objects.

    Examples
    --------
    .. manim:: QrCodeDocExample
       :save_last_frame:

       import manim as m
       from manim_extensions.qr_codes.qr import qr_code

       class QrCodeDocExample(m.Scene):
           def construct(self):
               plain = qr_code("https://fishshell.com")
               with_icon = qr_code(
                   payload="https://fishshell.com",
                   icon="terminal",
                   icon_size=6,
               )
               group = m.VGroup(plain, with_icon).arrange(m.RIGHT, buff=0.75)
               label = m.Text("https://fishshell.com")
               label.to_edge(m.UP, buff=0.75)
               self.add(group, label)

    .. manim:: QrCodeShapesExample

       import manim as m
       from manim_extensions.qr_codes.qr import qr_code

       class QrCodeShapesExample(m.Scene):
           def construct(self):
               rust = qr_code("https://www.rust-lang.org/", icon="language-rust",
                              data_shape="circles")
               self.play(m.FadeIn(rust))
               self.wait(1)
               python = qr_code("https://www.python.org/", icon="language-python",
                                data_shape="circles", corner_color=m.BLUE,
                                icon_color=m.YELLOW, icon_size=4)
               self.play(m.ReplacementTransform(rust, python))
               self.wait(1)
    """
    if icon_color is None:
        icon_color = m.WHITE
    if white_color is None:
        white_color = m.WHITE
    if corner_color is None:
        corner_color = white_color
    if data_shape not in ['circles', 'rectangles']:
        raise ValueError(f"Invalid data_shape: {data_shape}. valid values are 'circles' and 'rectangles'")
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

    # Create a VGroup to hold all the elements
    qr_data_group = m.VGroup()
    qr_corner_group = m.VGroup()

    # Draw a rectangle or circle for each module of the QR code, except for the corner elements
    for y, row in enumerate(matrix):
        for x, is_white_qr_pixel in enumerate(row):
            current_elem = None

            if data_shape == 'rectangles' and is_white_qr_pixel:
                default_rect_kwargs = {
                    'width': 1,
                    'height': 1,
                    'fill_opacity': 1,
                    'color': white_color,
                    'stroke_width': 0.5,
                }
                rect_kwargs = {**default_rect_kwargs, **rectangles_kwargs}

                rect = m.Rectangle(
                    **rect_kwargs
                )
                rect.move_to(m.DOWN * y + m.RIGHT * x)
                current_elem = rect

            elif data_shape == 'circles' and is_white_qr_pixel:
                default_circle_kwargs = {
                    'radius': 0.5,
                    'fill_opacity': 1,
                    'color': white_color,
                    'stroke_width': 0.5,
                }
                circle_kwargs = {**default_circle_kwargs, **circle_kwargs}
                circle = m.Circle(
                    **circle_kwargs
                )
                circle.move_to(m.DOWN * y + m.RIGHT * x)
                current_elem = circle

            # override current_elem if it is a corner element
            if is_white_qr_pixel and (x, y) in corner_positions:
                default_corner_kwargs = {
                    'width': 1,
                    'height': 1,
                    'fill_opacity': 1,
                    'color': corner_color,
                    'stroke_width': 0.5,
                }
                corner_kwargs = {**default_corner_kwargs, **rectangles_kwargs}
                rect = m.Rectangle(
                    **corner_kwargs
                )
                rect.move_to(m.DOWN * y + m.RIGHT * x)
                current_elem = rect

                qr_corner_group.add(current_elem)
                continue

            if current_elem is not None:
                qr_data_group.add(current_elem)

    qr_code_group = m.VGroup(qr_corner_group, qr_data_group)
    qr_code_group.move_to(m.ORIGIN)

    if icon is not None:
        # add icon to the center
        try:
            from manim_nerdfont_icons.icons import nerdfont_icon
        except ImportError as exc:
            raise ImportError(
                "The 'icon' argument requires the manim-nerdfont-icons "
                "package. Its PyPI metadata pins manim<0.20, so install "
                "it with: pip install --no-deps manim-nerdfont-icons"
            ) from exc
        center_icon = nerdfont_icon(icon)
        center_icon.set_color(icon_color)
        # scale icon to fit the qr center mask

        # if width is larger than height, then scale by using scale_to_fit_width
        # else scale by using scale_to_fit_height
        if center_icon.width > center_icon.height:
            center_icon.scale_to_fit_width(icon_size - 2 * icon_margin_size)
        else:
            center_icon.scale_to_fit_height(icon_size - 2 * icon_margin_size)

        center_icon_bounding_box = m.Rectangle(width=icon_size, height=icon_size, fill_opacity=0, stroke_width=0)
        # filter out all the qr pixels that are inside the icon bounding box
        for qr_pixel in qr_data_group:
            pixel_x, pixel_y, _ = qr_pixel.get_center()

            box_min_x = center_icon_bounding_box.get_left()[0]
            box_max_x = center_icon_bounding_box.get_right()[0]

            box_min_y = center_icon_bounding_box.get_bottom()[1]
            box_max_y = center_icon_bounding_box.get_top()[1]

            if box_min_x <= pixel_x <= box_max_x and box_min_y <= pixel_y <= box_max_y:
                qr_data_group.remove(qr_pixel)

        qr_code_group.add(center_icon)

    return qr_code_group.scale_to_fit_width(2)