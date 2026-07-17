# manim_extensions

`manim_extensions` is an extension toolkit for [Manim](https://www.manim.community/), providing Chinese formula rendering, geometric calculations, annotated graphics, and common animation effects to help you create mathematical animations more efficiently.

## Installation

```bash
pip install manim_extensions
```

Dependency: `manim`

## Module Overview

| Module | Description |
|--------|-------------|
| `mobjects` | Mobject class extensions, including Chinese formulas, labeled dots, extendable lines, etc. |
| `geometry` | Pure geometric calculation functions for finding intersections, tangent points, etc. |
| `animations` | Animation effects, such as visualized arc drawing and typewriter effects |
| `gearbox` | Involute gears and racks (from `manim-GearBox`) |
| `mindmap` | Mind maps, timelines, and catalog diagrams (from `manim-mindmap`) |
| `compass` | Compass-and-straightedge construction tools (from `manim-compass`) |

---

## mobjects Module

### `ChineseMathTex(*texts, font="SimSun", tex_to_color_map={}, **kwargs)`

A `MathTex` subclass that supports Chinese characters. You can write Chinese directly in the formula without manually wrapping it in `\text{}`.

```python
from manim_extensions import ChineseMathTex

formula = ChineseMathTex(
    "\\frac{1}{2} + \\text{hello} = x",
    tex_to_color_map={"\\text{hello}": RED},
    font="SimSun"
)
```

**Parameters**
- `*texts` — LaTeX text strings
- `font` — Chinese font name, default `"SimSun"`
- `tex_to_color_map` — Dictionary mapping text to colors, default `{}`
- `**kwargs` — Other arguments passed to `MathTex`

---

### `LabelDot(dot_label, dot_pos, label_pos=DOWN, buff=0.1, **kwargs)`

Creates a dot at the specified position and adds a `MathTex` label next to it.

```python
from manim_extensions import LabelDot

dot = LabelDot("A", [1, 2, 0], label_pos=UP, buff=0.2)
```

**Parameters**
- `dot_label` — Label text
- `dot_pos` — Dot position
- `label_pos` — Direction of the label relative to the dot, default `DOWN`
- `buff` — Spacing between label and dot, default `0.1`
- `**kwargs` — Other arguments passed to `VGroup`

---

### `MathTexLine(formula, direction=UP, buff=0.5, **kwargs)`

Creates a line segment and places a `MathTex` formula next to it in the specified direction.

```python
from manim_extensions import MathTexLine

line = MathTexLine(MathTex("y = x"), direction=UP, color=BLUE)
```

**Parameters**
- `formula` — `MathTex` formula object
- `direction` — Direction of the formula relative to the line, default `UP`
- `buff` — Spacing between formula and line, default `0.5`
- `**kwargs` — Other arguments passed to `Line`

---

### `MathTexBrace(target, formula, direction=UP, buff=0.5, **kwargs)`

Creates a brace for a target object and places a `MathTex` formula next to it.

```python
from manim_extensions import MathTexBrace

line = Line(LEFT, RIGHT)
brace = MathTexBrace(line, MathTex("\\Delta x"), direction=UP)
```

**Parameters**
- `target` — The object to be braced
- `formula` — `MathTex` formula object
- `direction` — Direction of the brace relative to the target, default `UP`
- `buff` — Spacing between formula and brace, default `0.5`
- `**kwargs` — Other arguments passed to `Brace`

---

### `MathTexDoublearrow(formula, direction=UP, buff=0.5, **kwargs)`

Creates a double arrow and places a `MathTex` formula next to it in the specified direction.

```python
from manim_extensions import MathTexDoublearrow

arrow = MathTexDoublearrow(MathTex("\\Leftrightarrow"), direction=DOWN)
```

**Parameters**
- `formula` — `MathTex` formula object
- `direction` — Direction of the formula relative to the arrow, default `UP`
- `buff` — Spacing between formula and arrow, default `0.5`
- `**kwargs` — Other arguments passed to `DoubleArrow`

---

### `ExtendedLine(line, extend_distance, **kwargs)`

Extends an existing `Line` by a specified distance at both ends along its original direction.

```python
from manim_extensions import ExtendedLine

original = Line(LEFT, RIGHT)
extended = ExtendedLine(original, extend_distance=1.0, color=RED)
```

**Parameters**
- `line` — Original line segment
- `extend_distance` — Distance to extend at each end
- `**kwargs` — Other arguments passed to `Line`

---

## geometry Module

### `CircleInt(circle1, circle2)`

Calculates the intersection points of two circles.

```python
from manim_extensions import CircleInt

c1 = Circle(radius=2).shift(LEFT)
c2 = Circle(radius=2).shift(RIGHT)
result = CircleInt(c1, c2)  # ([x1, y1, 0], [x2, y2, 0]) or None
```

**Returns**
- A tuple of two intersection points `([x, y, 0], [x, y, 0])` if they intersect
- `None` if they do not intersect

---

### `LineCircleInt(line, circle)`

Calculates the intersection points of a line segment and a circle, returning only points within the segment parameter range `[0, 1]`.

```python
from manim_extensions import LineCircleInt

line = Line(LEFT * 3, RIGHT * 3)
circle = Circle(radius=1)
result = LineCircleInt(line, circle)
```

**Returns**
- Two intersection points, one intersection point, or `None`

---

### `LineInt(line1, line2)`

Calculates the intersection point of two infinitely extended line segments in 2D (not restricted to the segment endpoints).

```python
from manim_extensions import LineInt

l1 = Line(LEFT, RIGHT)
l2 = Line(DOWN, UP)
result = LineInt(l1, l2)  # [0.0, 0.0, 0] or None
```

**Returns**
- Intersection point `[x, y, 0]`, or `None` if parallel

---

### `LineArcInt(line, arc)`

Calculates the intersection points of a line segment and an arc, checking whether the points truly lie within the arc's angle range.

```python
from manim_extensions import LineArcInt

line = Line(LEFT, RIGHT)
arc = Arc(start_angle=0, angle=PI, radius=1)
result = LineArcInt(line, arc)
```

**Returns**
- Two intersection points, one intersection point, or `None`

---

### `TangentPoint(p1, p2, line_start, line_end)`

Calculates the tangent point of a circle (passing through `p1` and `p2`) and a line segment.

```python
from manim_extensions import TangentPoint

p = TangentPoint(
    [1, 0, 0], [-1, 0, 0],
    line_start=[0, -2, 0], line_end=[0, 2, 0]
)
```

**Parameters**
- `p1`, `p2` — Two points on the circle, in the format `(x, y)` or `(x, y, z)`
- `line_start`, `line_end` — Start and end points of the line segment

**Returns**
- Tangent point coordinates as `np.ndarray`, or `None` if calculation fails

---

## animations Module

### `VisDrawArc(scene, arc, axis=OUT, run_time=1)`

Visualized arc drawing animation, showing a moving dot and a dashed radius line. **Call it directly; no need to wrap it in `self.play()`.**

```python
from manim_extensions import VisDrawArc

class MyScene(Scene):
    def construct(self):
        arc = Arc(start_angle=0, angle=PI, radius=2)
        VisDrawArc(self, arc, axis=OUT, run_time=2)
```

**Parameters**
- `scene` — Manim scene object
- `arc` — The `Arc` to draw
- `axis` — Rotation direction, `OUT` for counterclockwise and `IN` for clockwise, default `OUT`
- `run_time` — Animation duration in seconds, default `1`

---

### `TypeWriter(mobject, interval=2, **kwargs)`

Typewriter effect animation that displays `Text` content character by character. Automatically calculates the total animation duration based on character count and interval.

```python
from manim_extensions import TypeWriter

class MyScene(Scene):
    def construct(self):
        text = Text("Hello World")
        self.play(TypeWriter(text, interval=0.1))
```

**Parameters**
- `mobject` — `Text` object
- `interval` — Display interval between characters in seconds, default `2`
- `**kwargs` — Other arguments passed to `Animation`

---

## Third-party modules

The following modules are bundled as subpackages of `manim_extensions`. Their original authors and licenses are noted in the reference manual.

- `manim_extensions.gearbox` — involute gears and racks
- `manim_extensions.mindmap` — mind maps, timelines, catalog diagrams
- `manim_extensions.compass` — compass, ruler, pencil, and construction animations

---

## License

MIT License
