"""A 2D feature plane partitioned by a decision tree (scenes 7, 8).

Everything comes from ``data/toy2d.json`` (points, bounds, per-tree leaf boxes and
cut segments) and ``data/tree2d_extra.json`` (internal-node boxes, class
boundaries). This class only maps data coordinates to the screen: it never
computes a threshold or a box.

The plane is drawn as a framed box (the data bounds) with ticks along the bottom
and left edges, not as axes through the origin, so the only lines inside the box
are the tree's cuts.
"""

import math

import numpy as np
from manim import (
    Axes,
    Dot,
    Line,
    MathTex,
    Rectangle,
    Text,
    VGroup,
)

from style import (
    CAPTION_SIZE,
    CLASS_0,
    CLASS_1,
    DOWN,
    FONT,
    GRID,
    LEFT,
    TEXT,
    TEXT_MUTED,
    UP,
)

CLASS_COLORS = [CLASS_0, CLASS_1]

# z-order inside the plane: fills < cuts < dots < markers
Z_FILL, Z_CUT, Z_DOT, Z_TOP = 0, 1, 2, 3


class PartitionedPlane(VGroup):
    def __init__(
        self,
        toy: dict,
        x_length: float = 5.6,
        y_length: float = 5.9,
        dot_radius: float = 0.05,
        tick_size: float = 0.08,
        label_size: float = CAPTION_SIZE * 0.75,
        **kwargs,
    ):
        super().__init__(**kwargs)
        (x0, x1), (y0, y1) = toy["bounds"]
        self.bounds = toy["bounds"]
        # Axes are only used as a coordinate system; they are never added.
        self.axes = Axes(x_range=[x0, x1, 1], y_range=[y0, y1, 1], x_length=x_length, y_length=y_length, tips=False)

        self._axes_center = self.axes.get_center()
        self.frame = Rectangle(width=x_length, height=y_length).move_to(self._axes_center)
        self.frame.set_fill(opacity=0).set_stroke(GRID, 2)

        ticks, tick_labels = VGroup(), VGroup()
        for v in range(math.ceil(x0), math.floor(x1) + 1):
            p = self.c2p(v, y0)
            ticks.add(Line(p, p + DOWN * tick_size, color=GRID, stroke_width=2))
            tick_labels.add(Text(str(v), font=FONT, font_size=label_size, color=TEXT_MUTED).next_to(p, DOWN, buff=0.14))
        for v in range(math.ceil(y0), math.floor(y1) + 1):
            p = self.c2p(x0, v)
            ticks.add(Line(p, p + LEFT * tick_size, color=GRID, stroke_width=2))
            tick_labels.add(Text(str(v), font=FONT, font_size=label_size, color=TEXT_MUTED).next_to(p, LEFT, buff=0.14))
        self.ticks, self.tick_labels = ticks, tick_labels

        self.x_label = MathTex("x_1", color=TEXT).scale(0.8)
        self.x_label.next_to(self.c2p(x1, y0), DOWN, buff=0.14).shift(LEFT * 0.05)
        self.x_label.align_to(tick_labels[0], UP)
        self.y_label = MathTex("x_2", color=TEXT).scale(0.8)
        self.y_label.next_to(self.c2p(x0, y1), LEFT, buff=0.14)
        self.y_label.align_to(tick_labels[-1], DOWN).shift(UP * 0.35)

        self.dots = VGroup()
        self.labels = []
        for pt in toy["points"]:
            d = Dot(self.c2p(*pt["x"]), radius=dot_radius, color=CLASS_COLORS[pt["label"]])
            d.set_z_index(Z_DOT)
            self.dots.add(d)
            self.labels.append(pt["label"])
        self.class_dots = [VGroup(*[d for d, lab in zip(self.dots, self.labels) if lab == c]) for c in (0, 1)]

        self.axes_group = VGroup(self.frame, ticks, tick_labels, self.x_label, self.y_label)
        self.add(self.axes_group, self.dots)

    # --- coordinates ---------------------------------------------------------

    def c2p(self, x, y) -> np.ndarray:
        """Data -> screen. Follows the plane's frame, so the plane may be moved (not scaled) after creation."""
        return self.axes.c2p(x, y) - self._axes_center + self.frame.get_center()

    def box_rect(self, box, color=None, opacity: float = 0.18, stroke_width: float = 0) -> Rectangle:
        """A Rectangle covering ``box`` = [[x_min, x_max], [y_min, y_max]] in data coords."""
        (bx0, bx1), (by0, by1) = box
        a, b = self.c2p(bx0, by0), self.c2p(bx1, by1)
        rect = Rectangle(width=b[0] - a[0], height=b[1] - a[1]).move_to((a + b) / 2)
        rect.set_fill(color if color is not None else GRID, opacity)
        rect.set_stroke(color if color is not None else GRID, stroke_width)
        rect.set_z_index(Z_FILL)
        return rect

    def region(self, box, prediction: int, opacity: float = 0.18) -> Rectangle:
        return self.box_rect(box, CLASS_COLORS[prediction], opacity)

    def segment(self, start, end, color=GRID, stroke_width: float = 3) -> Line:
        line = Line(self.c2p(*start), self.c2p(*end), color=color, stroke_width=stroke_width)
        line.set_z_index(Z_CUT)
        return line

    def h_line(self, y, **kwargs) -> Line:
        (x0, x1), _ = self.bounds
        return self.segment([x0, y], [x1, y], **kwargs)

    def v_line(self, x, **kwargs) -> Line:
        _, (y0, y1) = self.bounds
        return self.segment([x, y0], [x, y1], **kwargs)

    # --- tree-driven groups ------------------------------------------------

    def leaf_regions(self, tree: dict, opacity: float = 0.18) -> VGroup:
        """One filled Rectangle per leaf of an exported tree, in ``tree['leaves']`` order."""
        return VGroup(*[self.region(lf["box"], lf["prediction"], opacity) for lf in tree["leaves"]])

    def cut_segments(self, tree: dict, **kwargs) -> VGroup:
        return VGroup(*[self.segment(s["start"], s["end"], **kwargs) for s in tree["segments"]])

    def boundary(self, segments: list, color=TEXT, stroke_width: float = 4) -> VGroup:
        """The class boundary (staircase) as a group of Lines, from precomputed segments."""
        return VGroup(*[self.segment(s["start"], s["end"], color=color, stroke_width=stroke_width) for s in segments])

