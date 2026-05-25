# manim_extensions

[English](#english) | [中文](#中文)

<a name="中文"></a>
## 中文

manim_extensions 是一个用于 [Manim](https://www.manim.community/) 的扩展工具包，提供了中文公式渲染、几何计算、带标注的图形以及常用动画效果，帮助你更高效地制作数学动画。

### 安装

```bash
pip install manim_extensions
```

依赖：`manim`

### 模块概览

| 模块 | 说明 |
|------|------|
| `mobjects` | Mobject 类扩展，包含中文公式、带标签圆点、可延长线段等 |
| `geometry` | 纯几何计算函数，用于求交点、切点等 |
| `animations` | 动画效果，如可视化绘弧、打字机效果 |

---

### mobjects 模块

#### `ChineseMathTex(*texts, font="SimSun", tex_to_color_map={}, **kwargs)`

支持中文显示的 `MathTex` 子类。可直接在公式中写入中文，无需手动包裹 `\text{}`。

```python
from manim_extensions import ChineseMathTex

formula = ChineseMathTex(
    "\\frac{1}{2} + 你好 = x",
    tex_to_color_map={"你好": RED},
    font="SimSun"
)
```

**参数**
- `*texts` — LaTeX 文本字符串
- `font` — 中文字体名称，默认 `"SimSun"`
- `tex_to_color_map` — 文本到颜色的映射字典，默认 `{}`
- `**kwargs` — 传递给 `MathTex` 的其他参数

---

#### `LabelDot(dot_label, dot_pos, label_pos=DOWN, buff=0.1, **kwargs)`

在指定位置创建一个圆点，并在其旁边添加 `MathTex` 标签。

```python
from manim_extensions import LabelDot

dot = LabelDot("A", [1, 2, 0], label_pos=UP, buff=0.2)
```

**参数**
- `dot_label` — 标签文本
- `dot_pos` — 圆点位置
- `label_pos` — 标签相对圆点的方向，默认 `DOWN`
- `buff` — 标签与圆点的间距，默认 `0.1`
- `**kwargs` — 传递给 `VGroup` 的其他参数

---

#### `MathTexLine(formula, direction=UP, buff=0.5, **kwargs)`

创建一条线段，并在其指定方向旁放置 `MathTex` 公式。

```python
from manim_extensions import MathTexLine

line = MathTexLine(MathTex("y = x"), direction=UP, color=BLUE)
```

**参数**
- `formula` — `MathTex` 公式对象
- `direction` — 公式相对线段的方向，默认 `UP`
- `buff` — 公式与线段的间距，默认 `0.5`
- `**kwargs` — 传递给 `Line` 的其他参数

---

#### `MathTexBrace(target, formula, direction=UP, buff=0.5, **kwargs)`

为指定对象创建一个花括号，并在其旁边放置 `MathTex` 公式。

```python
from manim_extensions import MathTexBrace

line = Line(LEFT, RIGHT)
brace = MathTexBrace(line, MathTex("\\Delta x"), direction=UP)
```

**参数**
- `target` — 要被花括号标注的目标对象
- `formula` — `MathTex` 公式对象
- `direction` — 公式与花括号相对目标的方向，默认 `UP`
- `buff` — 公式与花括号的间距，默认 `0.5`
- `**kwargs` — 传递给 `Brace` 的其他参数

---

#### `MathTexDoublearrow(formula, direction=UP, buff=0.5, **kwargs)`

创建一个双向箭头，并在其指定方向旁放置 `MathTex` 公式。

```python
from manim_extensions import MathTexDoublearrow

arrow = MathTexDoublearrow(MathTex("\\Leftrightarrow"), direction=DOWN)
```

**参数**
- `formula` — `MathTex` 公式对象
- `direction` — 公式相对箭头的方向，默认 `UP`
- `buff` — 公式与箭头的间距，默认 `0.5`
- `**kwargs` — 传递给 `DoubleArrow` 的其他参数

---

#### `ExtendedLine(line, extend_distance, **kwargs)`

基于一条已有的 `Line`，在其两端按原方向各延长指定距离。

```python
from manim_extensions import ExtendedLine

original = Line(LEFT, RIGHT)
extended = ExtendedLine(original, extend_distance=1.0, color=RED)
```

**参数**
- `line` — 原始线段
- `extend_distance` — 两端各延长的距离
- `**kwargs` — 传递给 `Line` 的其他参数

---

### geometry 模块

#### `CircleInt(circle1, circle2)`

计算两个圆的交点。

```python
from manim_extensions import CircleInt

c1 = Circle(radius=2).shift(LEFT)
c2 = Circle(radius=2).shift(RIGHT)
result = CircleInt(c1, c2)  # ([x1, y1, 0], [x2, y2, 0]) 或 None
```

**返回**
- 若相交，返回两个交点坐标的元组 `([x, y, 0], [x, y, 0])`
- 若不相交，返回 `None`

---

#### `LineCircleInt(line, circle)`

计算线段与圆的交点，仅返回落在线段参数范围 `[0, 1]` 内的交点。

```python
from manim_extensions import LineCircleInt

line = Line(LEFT * 3, RIGHT * 3)
circle = Circle(radius=1)
result = LineCircleInt(line, circle)
```

**返回**
- 两个交点、一个交点，或 `None`

---

#### `LineInt(line1, line2)`

在二维平面上计算两条无限延长线段的交点（不限制在线段端点范围内）。

```python
from manim_extensions import LineInt

l1 = Line(LEFT, RIGHT)
l2 = Line(DOWN, UP)
result = LineInt(l1, l2)  # [0.0, 0.0, 0] 或 None
```

**返回**
- 交点坐标 `[x, y, 0]`，或平行时返回 `None`

---

#### `LineArcInt(line, arc)`

计算线段与圆弧的交点，会检查交点是否真正落在圆弧的角度范围内。

```python
from manim_extensions import LineArcInt

line = Line(LEFT, RIGHT)
arc = Arc(start_angle=0, angle=PI, radius=1)
result = LineArcInt(line, arc)
```

**返回**
- 两个交点、一个交点，或 `None`

---

#### `TangentPoint(p1, p2, line_start, line_end)`

计算以 `p1` 和 `p2` 为圆上点、且与线段相切的切点坐标。

```python
from manim_extensions import TangentPoint

p = TangentPoint(
    [1, 0, 0], [-1, 0, 0],
    line_start=[0, -2, 0], line_end=[0, 2, 0]
)
```

**参数**
- `p1`, `p2` — 圆上的两个点，格式 `(x, y)` 或 `(x, y, z)`
- `line_start`, `line_end` — 线段的起点和终点

**返回**
- 切点坐标 `np.ndarray`，若无法计算则返回 `None`

---

### animations 模块

#### `VisDrawArc(scene, arc, axis=OUT, run_time=1)`

可视化绘制圆弧的动画，会同时显示一个沿圆弧移动的点及半径虚线。**直接调用即可，无需放入 `self.play()` 中。**

```python
from manim_extensions import VisDrawArc

class MyScene(Scene):
    def construct(self):
        arc = Arc(start_angle=0, angle=PI, radius=2)
        VisDrawArc(self, arc, axis=OUT, run_time=2)
```

**参数**
- `scene` — Manim 场景对象
- `arc` — 要绘制的 `Arc`
- `axis` — 旋转方向，`OUT` 为逆时针，`IN` 为顺时针，默认 `OUT`
- `run_time` — 动画时长（秒），默认 `1`

---

#### `TypeWriter(mobject, interval=2, **kwargs)`

打字机效果动画，逐个字符显示 `Text` 对象的内容。自动根据字符数量与间隔计算动画总时长。

```python
from manim_extensions import TypeWriter

class MyScene(Scene):
    def construct(self):
        text = Text("Hello World")
        self.play(TypeWriter(text, interval=0.1))
```

**参数**
- `mobject` — `Text` 对象
- `interval` — 字符间显示间隔（秒），默认 `2`
- `**kwargs` — 传递给 `Animation` 的其他参数

---

<a name="english"></a>
## English

manim_extensions is an extension toolkit for [Manim](https://www.manim.community/), providing Chinese formula rendering, geometric calculations, annotated graphics, and common animation effects to help you create mathematical animations more efficiently.

### Installation

```bash
pip install manim_extensions
```

Dependency: `manim`

### Module Overview

| Module | Description |
|--------|-------------|
| `mobjects` | Mobject class extensions, including Chinese formulas, labeled dots, extendable lines, etc. |
| `geometry` | Pure geometric calculation functions for finding intersections, tangent points, etc. |
| `animations` | Animation effects, such as visualized arc drawing and typewriter effects |

---

### mobjects Module

#### `ChineseMathTex(*texts, font="SimSun", tex_to_color_map={}, **kwargs)`

A `MathTex` subclass that supports Chinese characters. You can write Chinese directly in the formula without manually wrapping it in `\text{}`.

```python
from manim_extensions import ChineseMathTex

formula = ChineseMathTex(
    "\\frac{1}{2} + 你好 = x",
    tex_to_color_map={"你好": RED},
    font="SimSun"
)
```

**Parameters**
- `*texts` — LaTeX text strings
- `font` — Chinese font name, default `"SimSun"`
- `tex_to_color_map` — Dictionary mapping text to colors, default `{}`
- `**kwargs` — Other arguments passed to `MathTex`

---

#### `LabelDot(dot_label, dot_pos, label_pos=DOWN, buff=0.1, **kwargs)`

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

#### `MathTexLine(formula, direction=UP, buff=0.5, **kwargs)`

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

#### `MathTexBrace(target, formula, direction=UP, buff=0.5, **kwargs)`

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

#### `MathTexDoublearrow(formula, direction=UP, buff=0.5, **kwargs)`

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

#### `ExtendedLine(line, extend_distance, **kwargs)`

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

### geometry Module

#### `CircleInt(circle1, circle2)`

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

#### `LineCircleInt(line, circle)`

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

#### `LineInt(line1, line2)`

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

#### `LineArcInt(line, arc)`

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

#### `TangentPoint(p1, p2, line_start, line_end)`

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

### animations Module

#### `VisDrawArc(scene, arc, axis=OUT, run_time=1)`

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

#### `TypeWriter(mobject, interval=2, **kwargs)`

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

## License

MIT License
