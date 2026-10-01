"""A grid of generic person silhouettes for the Twenty Questions scenes (2, 4)."""

import numpy as np
from manim import PI, Arc, Circle, VGroup, VMobject

from style import TEXT_MUTED


class PersonIcon(VGroup):
    """Head + shoulders, built from primitives (no SVG assets, no real faces)."""

    def __init__(self, height=0.45, color=TEXT_MUTED, **kwargs):
        super().__init__(**kwargs)
        head = Circle(radius=0.2).set_fill(color, 1).set_stroke(width=0)
        shoulders = VMobject().set_fill(color, 1).set_stroke(width=0)
        arc = Arc(radius=0.36, start_angle=0, angle=PI)
        shoulders.set_points(arc.points)
        shoulders.add_line_to(arc.get_start())
        shoulders.next_to(head, np.array([0, -1, 0]), buff=0.05)
        self.add(head, shoulders)
        self.height = height


class CelebrityGrid(VGroup):
    """rows x cols PersonIcons. ``self.icon(r, c)`` addresses one; index = r * cols + c."""

    def __init__(self, rows=8, cols=8, icon_height=0.45, spacing=0.6, color=TEXT_MUTED, **kwargs):
        super().__init__(**kwargs)
        self.rows, self.cols, self.spacing = rows, cols, spacing
        for r in range(rows):
            for c in range(cols):
                icon = PersonIcon(height=icon_height, color=color)
                icon.move_to([(c - (cols - 1) / 2) * spacing, ((rows - 1) / 2 - r) * spacing, 0])
                self.add(icon)

    def icon(self, r, c):
        return self[r * self.cols + c]

    def cells(self, rows, cols):
        """VGroup of the icons in the given row and column index ranges."""
        return VGroup(*[self.icon(r, c) for r in rows for c in cols])


__all__ = ["CelebrityGrid", "PersonIcon"]
