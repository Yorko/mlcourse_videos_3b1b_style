"""Shared visual style for every scene: palette, typography, timing.

Import this at the top of each scene file (``from style import *``) so that
config tweaks (background colour, etc.) are applied before anything renders.
"""

from manim import (
    BLUE_C,
    DOWN,
    GREEN_C,
    GREY_B,
    GREY_D,
    LEFT,
    RED_C,
    RIGHT,
    TEAL_C,
    UP,
    WHITE,
    YELLOW_C,
    ManimColor,
    config,
)

# --- Palette -----------------------------------------------------------------
# 3b1b-ish: dark background, bright accents. Use the semantic names in scenes
# rather than raw colours so the whole course can be re-themed here.
BACKGROUND = ManimColor("#1C1C1C")
TEXT = WHITE
TEXT_MUTED = GREY_B
GRID = GREY_D

PRIMARY = BLUE_C  # main object / model
SECONDARY = YELLOW_C  # second object / series
POSITIVE = GREEN_C  # correct, gain
NEGATIVE = RED_C  # error, loss
ACCENT = TEAL_C

# Decision-trees video semantics. Yellow is a class here, so never use it to
# highlight: use HIGHLIGHT, and pass color=HIGHLIGHT to Indicate / Flash /
# Circumscribe (their default is yellow).
CLASS_0 = PRIMARY  # blue ball, "repaid"
CLASS_1 = SECONDARY  # yellow ball, "defaulted"
GAIN = POSITIVE  # information gain, the winning cut
IMPURITY = NEGATIVE  # entropy / error, a bad cut, "deny"
HIGHLIGHT = ACCENT  # cut lines, sliders, the active path
DIM_OPACITY = 0.25  # dim with set_opacity, so restoring is exact

# Ordered palette for categorical data (classes, clusters, series).
CATEGORICAL = [PRIMARY, SECONDARY, POSITIVE, NEGATIVE, ACCENT]

# --- Typography --------------------------------------------------------------
FONT = "Helvetica Neue"
TITLE_SIZE = 56
BODY_SIZE = 36
CAPTION_SIZE = 24

# --- Layout & timing ---------------------------------------------------------
EDGE_BUFF = 0.5
TITLE_POSITION = UP * 3.2
CAPTION_POSITION = DOWN * 3.3

FAST = 0.5
NORMAL = 1.0
SLOW = 2.0

# --- Global config -----------------------------------------------------------
config.background_color = BACKGROUND

__all__ = [
    "ACCENT",
    "BACKGROUND",
    "BODY_SIZE",
    "CAPTION_POSITION",
    "CAPTION_SIZE",
    "CATEGORICAL",
    "CLASS_0",
    "CLASS_1",
    "DIM_OPACITY",
    "DOWN",
    "EDGE_BUFF",
    "FAST",
    "FONT",
    "GAIN",
    "GRID",
    "HIGHLIGHT",
    "IMPURITY",
    "LEFT",
    "NEGATIVE",
    "NORMAL",
    "POSITIVE",
    "PRIMARY",
    "RIGHT",
    "SECONDARY",
    "SLOW",
    "TEXT",
    "TEXT_MUTED",
    "TITLE_POSITION",
    "TITLE_SIZE",
    "UP",
]
