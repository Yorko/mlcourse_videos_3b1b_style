"""Scene 9: Regression trees (docs/STORYBOARD.md, rows 9.1-9.10).

The axes are drawn out to x = 8 from the start, but the camera frames only the
data range [-5, 5] until 9.8, where it pans right (implementation flag #14).
"""

import json
from pathlib import Path

import numpy as np
from manim import (
    Arrow,
    Axes,
    Circle,
    Create,
    DashedLine,
    DashedVMobject,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MovingCameraScene,
    NumberLine,
    ORIGIN,
    Rectangle,
    ReplacementTransform,
    Text,
    Transform,
    VGroup,
    VMobject,
    Write,
)
from manim_voiceover import VoiceoverScene

from components.tree_diagram import TreeDiagram
from style import *
from voice import speech_service

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REG = json.loads((DATA_DIR / "regression.json").read_text())
EXTRA = json.loads((DATA_DIR / "regression_extra.json").read_text())
BALLS = json.loads((DATA_DIR / "balls.json").read_text())

FITS = {f["max_depth"]: f for f in REG["fits"]}
X_LO, X_HI = REG["data_range"]
X_MAX = 8  # axes extend this far right; seen only after the 9.8 pan
UNIT_X = 1.1  # 11 units of width for the 10-unit data range
Y_RANGE = (-0.5, 2.0)
PLOT_CENTER = DOWN * 0.3
FORMULA_POS = RIGHT * 3.5 + UP * 2.6
COUNTER_POS = LEFT * 5.0 + UP * 2.6
BALL_COLOR = {"blue": CLASS_0, "yellow": CLASS_1}
BALL_LINE_MAX = 26

# Every break point of every fit we show. Depth-d trees are prefixes of the
# depth-5 tree, so building all step functions on this shared grid gives them
# identical point counts and each step only slides vertically when morphing.
SHOWN_DEPTHS = [1, 2, 3, 5]
BREAKS = sorted({t for d in [0, *SHOWN_DEPTHS] for t in FITS[d]["thresholds"]})


def label(text, size=CAPTION_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def step_value(fit, x, side):
    """Leaf value of a precomputed fit just left/right of x (lookup, no fitting)."""
    i = np.searchsorted(fit["thresholds"], x, side="left" if side == "left" else "right")
    return fit["values"][i]


class RegressionTrees(VoiceoverScene, MovingCameraScene):
    def construct(self):
        self.set_speech_service(speech_service())
        frame = self.camera.frame

        axes = Axes(
            x_range=[X_LO, X_MAX, 1],
            y_range=[*Y_RANGE, 0.5],
            x_length=UNIT_X * (X_MAX - X_LO),
            y_length=4.5,
            axis_config={"color": GRID, "include_ticks": True, "tick_size": 0.05},
            tips=False,
        )
        axes.shift(PLOT_CENTER - axes.c2p((X_LO + X_HI) / 2, sum(Y_RANGE) / 2))
        x_lab = label("x", CAPTION_SIZE, TEXT_MUTED).next_to(axes.c2p(X_HI, 0), DOWN + LEFT * 0.2, buff=0.15)
        y_lab = label("y", CAPTION_SIZE, TEXT_MUTED).next_to(axes.c2p(0, Y_RANGE[1]), LEFT, buff=0.15)

        xs, ys = REG["train"]["x"], REG["train"]["y"]
        dots = VGroup(*[Dot(axes.c2p(x, y), radius=0.04, color=TEXT) for x, y in zip(xs, ys)])
        curve_pts = [(x, y) for x, y in zip(REG["f_curve"]["x"], REG["f_curve"]["y"]) if X_LO <= x <= X_HI]
        curve = VMobject().set_points_smoothly([axes.c2p(x, y) for x, y in curve_pts])
        curve = DashedVMobject(curve.set_stroke(GRID, 2), num_dashes=80)

        def step_fn(fit, x0=X_LO, x1=X_HI):
            corners = [axes.c2p(x0, step_value(fit, x0, "right"))]
            for t in BREAKS:
                corners += [axes.c2p(t, step_value(fit, t, "left")), axes.c2p(t, step_value(fit, t, "right"))]
            corners.append(axes.c2p(x1, step_value(fit, x1, "left")))
            return VMobject().set_points_as_corners(corners).set_stroke(HIGHLIGHT, 4)

        # 9.1
        with self.voiceover(text="What if the answer isn't a color at all, but a number?") as tracker:
            self.play(Create(axes), FadeIn(x_lab, y_lab), run_time=tracker.duration * 0.3)
            self.play(
                LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.01),
                Create(curve),
                run_time=tracker.duration * 0.6,
            )

        # 9.2: the single-leaf "tree" is the depth-0 fit, the mean of all points
        mean = FITS[0]["values"][0]
        fit = step_fn(FITS[0])
        mean_label = label("leaf prediction = average", CAPTION_SIZE, HIGHLIGHT)
        mean_label.next_to(axes.c2p(X_LO, mean), UP + RIGHT * 0.01, buff=0.12).shift(RIGHT * 0.1)
        with self.voiceover(
            text="A leaf can't vote on a color anymore, so it predicts the average of its points."
        ) as tracker:
            self.play(Create(fit), run_time=tracker.duration * 0.4)
            self.play(FadeIn(mean_label, shift=UP * 0.1), run_time=tracker.duration * 0.3)

        # 9.3
        residuals = VGroup(
            *[
                Line(axes.c2p(x, y), axes.c2p(x, mean), stroke_width=2, color=IMPURITY, stroke_opacity=0.5)
                for x, y in zip(xs, ys)
            ]
        )
        with self.voiceover(
            text="And the uncertainty we want to shrink becomes how spread out those values are around that average."
        ) as tracker:
            self.bring_to_back(residuals)
            self.play(LaggedStart(*[Create(r) for r in residuals], lag_ratio=0.01), run_time=tracker.duration * 0.8)

        # 9.4
        formula = MathTex(r"D = \frac{1}{n}\sum_i (y_i - ", r"\bar y", r")^2", color=TEXT, font_size=BODY_SIZE + 4)
        formula[1].set_color(HIGHLIGHT)
        formula.move_to(FORMULA_POS)
        arrow = Arrow(
            formula[1].get_bottom(),
            axes.c2p(X_HI, mean) + UP * 0.05,
            buff=0.1,
            color=HIGHLIGHT,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.08,
        )
        with self.voiceover(text="That's the variance: the average squared distance from the mean.") as tracker:
            self.play(Write(formula), run_time=tracker.duration * 0.5)
            self.play(Create(arrow), FadeOut(residuals), run_time=tracker.duration * 0.4)

        # 9.5: the same greedy algorithm as the ball tree
        icon_spec = {
            "id": "r",
            "no": {"id": "a", "no": {"id": "a0", "leaf": "blue"}, "yes": {"id": "a1", "leaf": "yellow"}},
            "yes": {"id": "b", "leaf": "yellow"},
        }
        icon = TreeDiagram(icon_spec, labels=False, h_spacing=0.35, level_gap=0.4, leaf_colors=BALL_COLOR)
        icon.next_to(formula, LEFT, buff=0.8)
        with self.voiceover(text="Everything else stays the same.") as tracker:
            self.play(FadeIn(icon, scale=0.6), run_time=tracker.duration * 0.35)
            self.play(Indicate(icon, color=HIGHLIGHT), run_time=tracker.duration * 0.4)
        self.play(FadeOut(icon), run_time=FAST)

        # 9.6: the mean line splits into the depth-1 step
        d1 = FITS[1]
        cut_x = d1["thresholds"][0]
        cut = DashedLine(axes.c2p(cut_x, Y_RANGE[0]), axes.c2p(cut_x, Y_RANGE[1]), color=HIGHLIGHT, stroke_width=2)
        counter = label(f"depth {d1['max_depth']}", BODY_SIZE).move_to(COUNTER_POS)
        new_fit = step_fn(d1)
        with self.voiceover(
            text="Find the cut that lowers variance the most, then repeat inside each piece."
        ) as tracker:
            self.play(FadeOut(formula, arrow, mean_label), run_time=FAST)
            self.play(Create(cut), FadeIn(counter), run_time=tracker.duration * 0.3)
            self.play(ReplacementTransform(fit, new_fit), run_time=tracker.duration * 0.3)
            self.play(
                Flash(axes.c2p(cut_x, np.mean(d1["values"])), color=HIGHLIGHT, flash_radius=0.4),
                run_time=min(1.0, tracker.duration * 0.2),
            )
        fit = new_fit

        # 9.7: depth 2 -> 3 -> 5, the steps slide onto the curve
        deeper = SHOWN_DEPTHS[1:]
        with self.voiceover(
            text="The result is a step function, and with more depth the steps follow the curve more closely."
        ) as tracker:
            step_t = tracker.duration * 0.9 / len(deeper)
            for i, d in enumerate(deeper):
                new_fit = step_fn(FITS[d])
                anims = [
                    ReplacementTransform(fit, new_fit),
                    Transform(counter, label(f"depth {FITS[d]['max_depth']}", BODY_SIZE).move_to(COUNTER_POS)),
                ]
                if i == 0:
                    anims.append(FadeOut(cut))
                self.play(*anims, run_time=step_t)
                fit = new_fit

        # 9.8: pan right past the data; the last leaf just carries on
        deepest = FITS[SHOWN_DEPTHS[-1]]
        last_value = step_value(deepest, X_HI, "left")
        extension = DashedLine(axes.c2p(X_HI, last_value), axes.c2p(X_MAX, last_value), color=HIGHLIGHT, stroke_width=4)
        pan = axes.c2p(X_MAX, 0)[0] + EDGE_BUFF - frame.width / 2
        with self.voiceover(text="But past the edge of the data, it just stays flat.") as tracker:
            self.play(frame.animate.shift(RIGHT * pan), counter.animate.shift(RIGHT * pan), run_time=tracker.duration * 0.5)
            self.play(Create(extension), run_time=tracker.duration * 0.4)

        # 9.9
        band = Rectangle(
            width=axes.c2p(X_HI, 0)[0] - axes.c2p(X_LO, 0)[0],
            height=axes.c2p(0, Y_RANGE[1])[1] - axes.c2p(0, Y_RANGE[0])[1],
        )
        band.set_fill(HIGHLIGHT, 0.08).set_stroke(width=0)
        band.move_to(axes.c2p(X_LO, Y_RANGE[0]), aligned_edge=DOWN + LEFT)
        seen = label("seen", BODY_SIZE, HIGHLIGHT).next_to(axes.c2p(X_HI / 2, Y_RANGE[1]), DOWN)
        flat = label("flat", BODY_SIZE, IMPURITY).next_to(axes.c2p((X_HI + X_MAX) / 2, last_value), UP, buff=0.6)
        with self.voiceover(
            text="A tree can fill in between points it has seen, but it can't predict beyond them."
        ) as tracker:
            self.bring_to_back(band)
            self.play(FadeIn(band), FadeIn(seen), run_time=tracker.duration * 0.4)
            self.play(FadeIn(flat, shift=DOWN * 0.1), Indicate(extension, color=IMPURITY), run_time=tracker.duration * 0.4)

        # 9.10: back to the balls, on a line stretched to 26
        plot = VGroup(axes, x_lab, y_lab, dots, curve, fit, extension, band, seen, flat, counter)
        line = NumberLine(
            x_range=[0, BALL_LINE_MAX, 1],
            length=12.5,
            color=GRID,
            include_numbers=True,
            numbers_to_include=list(range(0, BALL_LINE_MAX + 1, 5)),
            font_size=CAPTION_SIZE,
        )
        line.move_to(DOWN * 0.3)
        for num in line.numbers:
            num.set_color(TEXT_MUTED)
        balls = VGroup(
            *[
                Dot(line.n2p(i), radius=0.15, color=BALL_COLOR[c]).shift(UP * 0.3)
                for i, c in enumerate(BALLS["colors"])
            ]
        )
        ext = EXTRA["ball_extrapolation"]
        probe_19, probe_25 = ext["probes"]
        ghost_pos = line.n2p(probe_25["x"]) + UP * 0.3
        ghost = Circle(radius=0.15).set_stroke(TEXT_MUTED, 2).move_to(ghost_pos)
        ghost = DashedVMobject(ghost, num_dashes=10)
        ghost_fill = Dot(ghost_pos, radius=0.15, color=BALL_COLOR[probe_25["prediction"]])

        t = ext["leaf_threshold"] + 0.5  # the cut sits between ball t and ball t+1
        leaf_box = Rectangle(width=line.n2p(BALL_LINE_MAX)[0] - line.n2p(t)[0] + 0.2, height=1.1)
        leaf_box.set_fill(HIGHLIGHT, 0.1).set_stroke(HIGHLIGHT, 2)
        leaf_box.move_to(line.n2p(t) + UP * 0.3, aligned_edge=LEFT)
        leaf_label = label(f"one leaf: {ext['leaf_rule']}", CAPTION_SIZE, HIGHLIGHT).next_to(leaf_box, UP, buff=0.15)
        leaf_label.align_to(leaf_box, RIGHT)
        cut = DashedLine(line.n2p(t) + DOWN * 0.3, line.n2p(t) + UP * 0.9, color=HIGHLIGHT, stroke_width=2)

        with self.voiceover(
            text="Our balls work the same way: every ball past eighteen lands in the same leaf, "
            "so a ball at twenty-five gets exactly the same prediction as one at nineteen."
        ) as tracker:
            # A plain cross-fade: FadeTransform stretched the wide plot into ellipses.
            self.play(FadeOut(plot), run_time=tracker.duration * 0.12)
            frame.move_to(ORIGIN)
            self.play(FadeIn(line, balls), run_time=tracker.duration * 0.13)
            self.play(Create(cut), FadeIn(leaf_box, leaf_label), run_time=tracker.duration * 0.2)
            self.play(Create(ghost), run_time=tracker.duration * 0.1)
            self.play(Indicate(balls[probe_19["x"]], color=HIGHLIGHT), run_time=tracker.duration * 0.15)
            self.play(FadeIn(ghost_fill), run_time=tracker.duration * 0.1)
            self.play(
                Indicate(balls[probe_19["x"]], color=HIGHLIGHT),
                Indicate(ghost_fill, color=HIGHLIGHT),
                run_time=tracker.duration * 0.15,
            )
        self.wait(SLOW)
        self.play(FadeOut(line, balls, ghost, ghost_fill, leaf_box, leaf_label, cut), run_time=NORMAL)
