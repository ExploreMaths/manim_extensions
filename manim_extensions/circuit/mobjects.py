from manim import *
from .utils import *


class VoltageSource(Source):
    """Voltage source symbol for circuit diagrams.

    Examples
    --------

    .. manim:: VoltageSourceExample
      :save_last_frame:

        from manim import *
        from manim_extensions.circuit.mobjects import VoltageSource

        class VoltageSourceExample(Scene):
            def construct(self):
                vs = VoltageSource(value=5, direction=LEFT)
                self.add(vs)
"""

    def __init__(self, value=1, label=True, direction=LEFT, dependent=True, **kwargs):
        # + and -
        """Initialize the VoltageSource instance."""
        markings = VGroup()
        markings.add(Line(DOWN * 0.3, UP * 0.3).shift(UP * 0.5))
        markings.add(Line(LEFT * 0.3, RIGHT * 0.3).shift(UP * 0.5))
        markings.add(Line(LEFT * 0.3, RIGHT * 0.3).shift(DOWN * 0.5))

        super().__init__(
            markings,
            letter="V",
            value=value,
            direction=direction,
            dependent=dependent,
            **kwargs,
        )


class CurrentSource(Source):
    """Current source symbol for circuit diagrams.

    Examples
    --------

    .. manim:: CurrentSourceExample
      :save_last_frame:

        from manim import *
        from manim_extensions.circuit.mobjects import CurrentSource

        class CurrentSourceExample(Scene):
            def construct(self):
                cs = CurrentSource(value=2, direction=RIGHT)
                self.add(cs)
"""

    def __init__(self, value=1, label=True, direction=LEFT, dependent=True, **kwargs):
        # Arrow
        """Initialize the CurrentSource instance."""
        markings = Line(DOWN * 0.75, UP * 0.75).add_tip(tip_shape=StealthTip)
        super().__init__(
            markings,
            letter="A",
            value=value,
            direction=direction,
            dependent=dependent,
            **kwargs,
        )


class Inductor(VMobject):
    """Inductor component used in circuit visualisations.

    Examples
    --------

    .. manim:: InductorExample
      :save_last_frame:

        from manim import *
        from manim_extensions.circuit.mobjects import Inductor

        class InductorExample(Scene):
            def construct(self):
                inductor = Inductor(label="10mH")
                self.add(inductor)
"""

    def __init__(self, label=None, direction=DOWN, **kwargs):
        # initialize the vmobject
        """Initialize the Inductor instance."""
        super().__init__(**kwargs)
        self._direction = direction

        self.main_body = (
            ParametricFunction(
                (lambda t: ((np.cos(t) / 1.94) + (t / (2.21 * PI)), -np.sin(t), 0)),
                t_range=(-PI, 8 * PI),
            )
            .scale(0.25)
            .center()
        )

        self.add(self.main_body)

        # check if lebel is present.
        if not label is None:
            self.label = (
                Tex(str(label) + " H")
                .scale(0.5)
                .next_to(self.main_body, self._direction, buff=0.1)
            )
            self.add(self.label)
        else:
            self.label = None

    def get_anchors(self):
        """Return the start and end anchor points of the inductor.

        Returns
        -------
        list of numpy.ndarray
            ``[start, end]`` of the main body.
        """
        return [self.main_body.get_start(), self.main_body.get_end()]

    def get_terminals(self, val):
        """Return the position of the left or right terminal.

        Parameters
        ----------
        val : str
            ``"left"`` or ``"right"``.

        Returns
        -------
        numpy.ndarray
            The terminal point.
        """
        if val == "left":
            return self.main_body.get_start()
        elif val == "right":
            return self.main_body.get_end()

    def center(self):
        """Shift the inductor so that its main body is centred at the origin.

        Returns
        -------
        Inductor
            The modified self.
        """
        self.shift(
            DOWN * self.main_body.get_center()[1] + LEFT * self.main_body.get_center()
        )

        return self

    def rotate(self, angle, *args, **kwargs):
        """Rotate the inductor about the centre of its main body.

        The label is rotated by the opposite angle to keep it upright.

        Parameters
        ----------
        angle : float
            Rotation angle in radians.
        *args, **kwargs
            Additional arguments forwarded to :meth:`VMobject.rotate`.

        Returns
        -------
        Inductor
            The modified self.
        """
        super().rotate(angle, about_point=self.main_body.get_center(), *args, **kwargs)
        if not self.label == None:
            self.label.rotate(-angle).next_to(self.main_body, self._direction, buff=0.1)

        return self


class Resistor(VMobject):
    """Resistor component shown as a zig-zag path.

    Examples
    --------

    .. manim:: ResistorExample
      :save_last_frame:

        from manim import *
        from manim_extensions.circuit.mobjects import Resistor

        class ResistorExample(Scene):
            def construct(self):
                resistor = Resistor(label="4.7k")
                self.add(resistor)
"""

    def __init__(self, label=None, direction=DOWN, **kwargs):
        # initialize the vmobject
        """Initialize the Resistor instance."""
        super().__init__(**kwargs)
        self._direction = direction

        # Less points, more cleaner!
        self.main_body = VMobject()
        points = [
            [-0.96795, 0, 0],
            [-0.54268, 1, 0],
            [0.30788, -1, 0],
            [1.15843, 1, 0],
            [2.00899, -1, 0],
            [2.85954, 1, 0],
            [3.7101, -1, 0],
            [4.13537, 0, 0],
        ]
        self.main_body.start_new_path(points[0])
        for i in points[1:]:
            self.main_body.add_line_to(np.array(i))
        self.main_body.scale(0.25).center()

        self.add(self.main_body)

        # check if lebel is present.
        if not label is None:
            self.label = (
                Tex(str(label) + r" $\Omega $")
                .scale(0.5)
                .next_to(self.main_body, self._direction, buff=0.1)
            )
            self.add(self.label)
        else:
            self.label = None

    def get_anchors(self):
        """Return the start and end anchor points of the resistor.

        Returns
        -------
        list of numpy.ndarray
            ``[start, end]`` of the main body.
        """
        return [self.main_body.get_start(), self.main_body.get_end()]

    def get_terminals(self, val):
        """Return the position of the left or right terminal.

        Parameters
        ----------
        val : str
            ``"left"`` or ``"right"``.

        Returns
        -------
        numpy.ndarray
            The terminal point.
        """
        if val == "left":
            return self.main_body.get_start()
        elif val == "right":
            return self.main_body.get_end()

    def center(self):
        """Shift the resistor so that its main body is centred at the origin.

        Returns
        -------
        Resistor
            The modified self.
        """
        self.shift(
            DOWN * self.main_body.get_center()[1] + LEFT * self.main_body.get_center()
        )

        return self

    def rotate(self, angle, *args, **kwargs):
        """Rotate the resistor about the centre of its main body.

        The label is rotated by the opposite angle to keep it upright.

        Parameters
        ----------
        angle : float
            Rotation angle in radians.
        *args, **kwargs
            Additional arguments forwarded to :meth:`VMobject.rotate`.

        Returns
        -------
        Resistor
            The modified self.
        """
        super().rotate(angle, about_point=self.main_body.get_center(), *args, **kwargs)
        if not self.label == None:
            self.label.rotate(-angle).next_to(self.main_body, self._direction, buff=0.1)

        return self


class Capacitor(VMobject):
    """Capacitor component for circuit diagrams.

    Examples
    --------

    .. manim:: CapacitorExample
      :save_last_frame:

        from manim import *
        from manim_extensions.circuit.mobjects import Capacitor

        class CapacitorExample(Scene):
            def construct(self):
                cap = Capacitor(label="100n", polarized=True)
                self.add(cap)
"""

    def __init__(self, label=None, direction=DOWN, polarized=False, **kwargs):
        # initialize the vmobject
        """Initialize the Capacitor instance."""
        super().__init__(**kwargs)
        self._direction = direction

        self.main_body = VGroup(
            Line([(7 / 4.42) - 0.125, 1, 0], [(7 / 4.42) - 0.125, -1, 0]),
        )

        # not polarized:
        if not polarized:
            self.main_body.add(
                Line([(7 / 4.42) + 0.125, 1, 0], [(7 / 4.42) + 0.125, -1, 0])
            )
        else:
            self.main_body.add(
                ArcBetweenPoints(
                    start=[(7 / 4.42) + 0.325, 1, 0],
                    end=[(7 / 4.42) + 0.325, -1, 0],
                    angle=PI / 4,
                )
            )
            pass

        self.main_body.scale(0.25).center()

        self.add(self.main_body)

        # check if lebel is present.
        if not label is None:
            self.label = (
                Tex(str(label) + "F")
                .scale(0.5)
                .next_to(self.main_body, self._direction, buff=0.1)
            )
            self.add(self.label)

    def get_terminals(self, val):
        """Return the position of the left or right terminal plate.

        Parameters
        ----------
        val : str
            ``"left"`` or ``"right"``.

        Returns
        -------
        numpy.ndarray
            The terminal midpoint.
        """
        if val == "left":
            return self.main_body[0].get_midpoint()
        elif val == "right":
            return self.main_body[1].get_midpoint()

    def center(self):
        """Shift the capacitor so that its main body is centred at the origin.

        Returns
        -------
        Capacitor
            The mobject itself (allows method chaining).
        """
        self.shift(
            DOWN * self.main_body.get_center()[1] + LEFT * self.main_body.get_center()
        )

        return self

    def rotate(self, angle, *args, **kwargs):
        """Rotate the capacitor about the centre of its main body.

        The label is rotated by the opposite angle to keep it upright.

        Parameters
        ----------
        angle : float
            Rotation angle in radians.
        *args, **kwargs
            Additional arguments forwarded to :meth:`VMobject.rotate`.

        Returns
        -------
        Capacitor
            The modified self.
        """
        super().rotate(angle, about_point=self.main_body.get_center(), *args, **kwargs)
        if not self.label == None:
            self.label.rotate(-angle).next_to(self.main_body, self._direction, buff=0.1)

        return self


class Ground(VMobject):
    """Ground symbol used in circuit diagrams.

    Examples
    --------

    .. manim:: GroundExample
      :save_last_frame:

        from manim import *
        from manim_extensions.circuit.mobjects import Ground

        class GroundExample(Scene):
            def construct(self):
                gnd = Ground(ground_type="earth")
                self.add(gnd)
"""

    def __init__(self, ground_type="ground", label=None, **kwargs):
        # initialize the vmobject
        """Initialize the Ground instance."""
        super().__init__(**kwargs)

        if ground_type == "ground":
            self.main_body = VGroup(Polygon([0, 0, 0], [2, 0, 0], [1, -1, 0]))
            if not label is None and label == "D" or label == "A":
                self.main_body.add(Text(label).move_to(self.main_body))
                # 'D' or 'A' for digital vs analog ground
                pass

        elif ground_type == "earth":
            self.main_body = VGroup(
                Line([0, 0, 0], [2, 0, 0]),
                Line([(1 / 3), -(1 / 3), 0], [(5 / 3), -(1 / 3), 0]),
                Line([(2 / 3), -(2 / 3), 0], [(4 / 3), -(2 / 3), 0]),
            )

        # tail for ground:
        self.add(self.main_body)

        # Scale down to match the scale of other electrical mobjects
        self.main_body.set_color(WHITE)
        self.main_body.stroke_opacity = 1

        self.main_body.center().scale(0.25).center()

    def get_terminals(self, *args):
        """Return the top connection point of the ground symbol.

        Parameters
        ----------
        *args
            Ignored; present for interface compatibility.

        Returns
        -------
        numpy.ndarray
            The terminal point on the top horizontal line.
        """
        if len(self.main_body) != 3:
            return self.main_body[0].point_from_proportion(1 / (2 + 2 * np.sqrt(2)))
        else:
            return self.main_body[0].point_from_proportion(0.5)


class Opamp(VMobject):
    """Operational amplifier symbol for electrical diagram animations.

    Examples
    --------

    .. manim:: OpampExample
      :save_last_frame:

        from manim import *
        from manim_extensions.circuit.mobjects import Opamp

        class OpampExample(Scene):
            def construct(self):
                opamp = Opamp(bias_supply="both", label=True)
                self.add(opamp)
"""

    def __init__(self, bias_supply=None, label=False, **kwargs):
        # initialize the vmobject
        """Initialize the Opamp instance."""
        super().__init__(**kwargs)

        self._plots = VGroup()
        self._terminals = {
            "positive_input": None,
            "negative_input": None,
            "positive_bias": None,
            "negative_bias": None,
            "output": None,
        }

        # main body structure
        self.main_body = VGroup(
            Triangle().rotate(-90 * DEGREES).set_color(WHITE),
        )

        # Indications for the input terminals
        self.main_body.add(
            VGroup(
                Line(DOWN * 0.15, UP * 0.15), Line(LEFT * 0.15, RIGHT * 0.15)
            ).next_to(
                self.main_body.get_left() + [0, self.main_body.height / 4, 0],
                RIGHT,
                buff=0.05,
            )
        )
        self.main_body.add(
            Line(LEFT * 0.15, RIGHT * 0.15).next_to(
                self.main_body.get_left() - [0, self.main_body.height / 4, 0],
                RIGHT,
                buff=0.05,
            ),
        )
        self.add(self.main_body)

        # Rails
        self._labels = VGroup()
        self._pos_rail = Line(
            (self.main_body.get_left() + [0, self.main_body.height / 4, 0]),
            (self.main_body.get_left() + [-0.25, self.main_body.height / 4, 0]),
        )

        self._plots.add(
            Dot(
                self.main_body.get_left() + [-0.25, self.main_body.height / 4, 0]
            ).set_opacity(0)
        )
        self._terminals["positive_input"] = self._plots[-1].get_center()

        self._neg_rail = Line(
            (self.main_body.get_left() - [0, self.main_body.height / 4, 0]),
            (self.main_body.get_left() - [0.25, self.main_body.height / 4, 0]),
        )
        self._plots.add(
            Dot(
                self.main_body.get_left() - [0.25, self.main_body.height / 4, 0]
            ).set_opacity(0)
        )
        self._terminals["negative_input"] = self._plots[-1].get_center()

        self._output_rail = Line(
            self.main_body.get_right(), (self.main_body.get_right() + [0.25, 0, 0])
        )
        self._plots.add(Dot(self.main_body.get_right() + [0.25, 0, 0]).set_opacity(0))
        self._terminals["output"] = self._plots[-1].get_center()

        self.rails = VGroup(self._pos_rail, self._neg_rail, self._output_rail)

        if "positive" == bias_supply or "both" == bias_supply:
            self._positive_bias = Line(
                (self.main_body.get_corner(UL) + self.main_body.get_right()) / 2,
                (self.main_body.get_corner(UL) + self.main_body.get_right()) / 2
                + [0, 0.25, 0],
            )
            self.rails.add(self._positive_bias)
            if label is True:
                self._labels.add(
                    MathTex(r"V_{CC}").scale(0.5).next_to(self._positive_bias, RIGHT)
                )

            self._plots.add(
                Dot(
                    (self.main_body.get_corner(UL) + self.main_body.get_right()) / 2
                    + [0, 0.25, 0]
                ).set_opacity(0)
            )
            self._terminals["positive_bias"] = self._plots[-1].get_center()

        if "negative" == bias_supply or "both" == bias_supply:
            self._negative_bias = Line(
                (self.main_body.get_corner(DL) + self.main_body.get_right()) / 2,
                (self.main_body.get_corner(DL) + self.main_body.get_right()) / 2
                + [0, -0.25, 0],
            )
            self.rails.add(self._negative_bias)
            if label is True:
                self._labels.add(
                    MathTex(r"-V_{CC}").scale(0.5).next_to(self._negative_bias, RIGHT)
                )

            self._plots.add(
                Dot(
                    (self.main_body.get_corner(DL) + self.main_body.get_right()) / 2
                    + [0, -0.25, 0]
                ).set_opacity(0)
            )

            self._terminals["negative_bias"] = self._plots[-1].get_center()
        self.add(self.rails, self._labels, self._plots)

    def get_terminals(self, val):
        """Return the position of a named terminal.

        Parameters
        ----------
        val : str
            One of ``"positive_input"``, ``"negative_input"``,
            ``"positive_bias"``, ``"negative_bias"``, or ``"output"``.

        Returns
        -------
        numpy.ndarray
            The terminal point.
        """
        return self._terminals[val]