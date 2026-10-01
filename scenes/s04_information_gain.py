"""Scene 4: Information gain (docs/STORYBOARD.md, rows 4.1-4.24).

Starts from the state scene 3 ends in: the balls at y = 1.8, the entropy arch
parked bottom-right, S0 parked top-right. Every number comes from
data/balls.json, including which threshold wins.
"""

import json
from math import floor
from pathlib import Path

import numpy as np
from manim import (
    Axes,
    Brace,
    Circle,
    Circumscribe,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Rectangle,
    ReplacementTransform,
    ScaleInPlace,
    Text,
    TransformFromCopy,
    TransformMatchingTex,
    Transform,
    UL,
    UR,
    ValueTracker,
    VGroup,
    Write,
    always_redraw,
    config,
    there_and_back,
    linear,
)
from manim_voiceover import VoiceoverScene

from components.celebrity_grid import CelebrityGrid
from style import *
from voice import speech_service

DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "balls.json").read_text())
CUTS = {d["t"]: d for d in DATA["thresholds"]}
BALL_COLOR = {"blue": CLASS_0, "yellow": CLASS_1}

BALL_Y = 1.8
ROW_WIDTH = 11
BALL_R = 0.15
GAP = 0.6  # each side of a split moves this far away from the cut
CUT_HALF = 0.75  # half-height of the dashed cut line
VALUE_Y = 0.25  # S1 / S2 values under the braces
FORMULA_Y = -0.9
BARS_BASE_Y = -3.0
BARS_MAX_H = 2.6
BAR_W = 0.36
SAFE_X = config.frame_width / 2 - EDGE_BUFF
CURVE_CENTER = RIGHT * 5 + DOWN * 2.4
CURVE_SCALE = 0.45


def label(text, size=CAPTION_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def fmt(v):
    return f"{v:.2f}"


def clamp_x(mob):
    """Shift a mobject horizontally so it stays inside the safe area."""
    if mob.get_left()[0] < -SAFE_X:
        mob.shift(RIGHT * (-SAFE_X - mob.get_left()[0]))
    if mob.get_right()[0] > SAFE_X:
        mob.shift(LEFT * (mob.get_right()[0] - SAFE_X))
    return mob


def entropy_fn(p):
    """Binary entropy, only used to draw the shape of the arch."""
    if p <= 0 or p >= 1:
        return 0.0
    return float(-(p * np.log2(p) + (1 - p) * np.log2(1 - p)))


class BallRow(VGroup):
    """20 balls r = 0.15 on a number line 0..19, centered at y = 1.8, width 11.

    Each ball is a cell (line segment + tick + dot + position label) so the line
    opens up with the balls. ``split_at(t)`` returns animations that open a gap
    between ball t and t+1 (the question "x <= t"); ``merge()`` closes it.
    """

    def __init__(self, colors, width=ROW_WIDTH, y=BALL_Y, **kwargs):
        super().__init__(**kwargs)
        self.n = len(colors)
        self.unit = width / (self.n - 1)
        self.x0 = -width / 2
        self.y = y
        self.offsets = [0.0] * self.n
        self.cells = VGroup()
        self.dots = VGroup()
        for i, c in enumerate(colors):
            x = self.rest_x(i)
            seg = Line([x - self.unit / 2, y, 0], [x + self.unit / 2, y, 0], color=GRID, stroke_width=2)
            tick = Line([x, y - 0.08, 0], [x, y + 0.08, 0], color=GRID, stroke_width=2)
            dot = Dot([x, y, 0], radius=BALL_R, color=BALL_COLOR[c])
            num = label(str(i), CAPTION_SIZE * 0.7, TEXT_MUTED).move_to([x, y - 0.38, 0])
            self.cells.add(VGroup(seg, tick, dot, num))
            self.dots.add(dot)
        self.add(self.cells)

    def rest_x(self, pos):
        """Screen x of a (possibly fractional) position when the row is closed."""
        return self.x0 + pos * self.unit

    def side(self, t, which):
        idx = [i for i in range(self.n) if (i <= t) == (which == "left")]
        return VGroup(*[self.cells[i] for i in idx])

    def _move_to(self, offsets):
        anims = []
        for cell, old, new in zip(self.cells, self.offsets, offsets):
            if abs(new - old) > 1e-6:
                anims.append(cell.animate.shift(RIGHT * (new - old)))
        self.offsets = list(offsets)
        return anims

    def split_at(self, t, sides=("left", "right"), gap=GAP):
        offsets = []
        for i in range(self.n):
            if i <= t:
                offsets.append(-gap if "left" in sides else 0.0)
            else:
                offsets.append(gap if "right" in sides else 0.0)
        return self._move_to(offsets)

    def merge(self):
        return self._move_to([0.0] * self.n)


class EntropyCurve(VGroup):
    """The entropy arch: Axes(0..1, 0..1), the curve, and ``mark(p, s, text)``."""

    def __init__(self, x_length=6, y_length=3.5, **kwargs):
        super().__init__(**kwargs)
        self.axes = Axes(
            x_range=[0, 1, 0.5],
            y_range=[0, 1, 0.5],
            x_length=x_length,
            y_length=y_length,
            tips=False,
            axis_config={"color": GRID, "stroke_width": 2},
        )
        self.graph = self.axes.plot(entropy_fn, x_range=[0, 1, 0.005], color=IMPURITY)
        top = self.axes.c2p(1, 1)
        self.one_line = DashedLine(self.axes.c2p(0, 1), top, color=GRID, stroke_width=1.5, dash_length=0.05)
        self.add(self.axes, self.one_line, self.graph)

    def mark(self, p, s, text, color=TEXT, direction=UP, size=CAPTION_SIZE * 0.8):
        dot = Dot(self.axes.c2p(p, s), radius=0.05, color=color)
        tag = text if not isinstance(text, str) else label(text, size, color)
        tag.next_to(dot, direction, buff=0.08)
        return VGroup(dot, tag)


class InformationGain(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())
        ent = DATA["entropy"]
        n_total = DATA["counts"]["blue"] + DATA["counts"]["yellow"]
        q = DATA["split_12"]  # the question "x <= 12" from the narration
        q_t = next(t for t, d in CUTS.items() if d["left"] == q["left"] and d["right"] == q["right"])
        best_t = DATA["best_threshold"]

        # --- state carried over from scene 3 ---------------------------------
        balls = BallRow(DATA["colors"])
        curve = EntropyCurve(x_length=6 * CURVE_SCALE, y_length=3.5 * CURVE_SCALE).move_to(CURVE_CENTER)
        p_all = DATA["counts"]["yellow"] / n_total
        ours = curve.mark(p_all, ent["S0"], "our balls", direction=UP)
        s0_park = MathTex("S_0", r"\approx", fmt(ent["S0"]), font_size=BODY_SIZE, color=TEXT)
        s0_park.to_corner(UR, buff=EDGE_BUFF)
        self.add(balls, curve, ours, s0_park)

        # the cut: a dashed line driven by a threshold tracker (in ball units)
        t_val = ValueTracker(0.5)

        def cut_x():
            return balls.rest_x(t_val.get_value())

        cut = always_redraw(
            lambda: DashedLine(
                [cut_x(), BALL_Y - CUT_HALF, 0],
                [cut_x(), BALL_Y + CUT_HALF, 0],
                color=HIGHLIGHT,
                stroke_width=4,
                dash_length=0.1,
            )
        )
        cut_label = always_redraw(
            lambda: MathTex(
                rf"x \le {int(floor(t_val.get_value()))}\,?", font_size=BODY_SIZE, color=HIGHLIGHT
            ).next_to(cut.get_top(), UP, buff=0.12)
        )

        # 4.1
        with self.voiceover(text="Now we can score a question.") as tracker:
            self.play(FadeIn(cut), run_time=min(NORMAL, tracker.duration))

        # 4.2
        threshold_word = label("threshold", CAPTION_SIZE, TEXT_MUTED)
        with self.voiceover(
            text='On this line, a question is a cut point, a threshold: "Is the position at most twelve?"'
        ) as tracker:
            self.add(cut_label)
            self.play(FadeIn(cut_label), run_time=FAST)
            self.play(t_val.animate.set_value(q_t + 0.5), run_time=tracker.duration * 0.6)
            threshold_word.next_to(cut_label, RIGHT, buff=0.25)
            self.play(FadeIn(threshold_word, shift=LEFT * 0.2), run_time=FAST)

        # 4.3
        with self.voiceover(text="Does asking it lower our uncertainty?") as tracker:
            self.play(Indicate(cut_label, color=HIGHLIGHT), run_time=min(1.2, tracker.duration))

        # 4.4 / 4.5: the two groups, with braces and counts
        def group_info(t, which):
            counts = CUTS[t][which]
            grp = balls.side(t, which)
            brace = Brace(grp, DOWN, buff=0.08, color=TEXT_MUTED)
            count = label(str(sum(counts)), CAPTION_SIZE)
            rest = label(
                f": {counts[0]} blue, {counts[1]} yellow",
                CAPTION_SIZE,
                t2c={f"{counts[0]} blue": CLASS_0, f"{counts[1]} yellow": CLASS_1},
            )
            rest.next_to(count, RIGHT, buff=0.05).align_to(count, DOWN)
            text = VGroup(count, rest).next_to(brace, DOWN, buff=0.12)
            clamp_x(text)
            return brace, count, VGroup(brace, text)

        with self.voiceover(text="On the left we get thirteen balls, eight blue and five yellow.") as tracker:
            self.play(FadeOut(threshold_word), *balls.split_at(q_t, ("left",)), run_time=tracker.duration * 0.35)
            brace_l, count_l, info_l = group_info(q_t, "left")
            self.play(FadeIn(info_l, shift=DOWN * 0.1), run_time=tracker.duration * 0.35)

        with self.voiceover(text="On the right, seven balls: one blue and six yellow.") as tracker:
            self.play(*balls.split_at(q_t), run_time=tracker.duration * 0.35)
            brace_r, count_r, info_r = group_info(q_t, "right")
            self.play(FadeIn(info_r, shift=DOWN * 0.1), run_time=tracker.duration * 0.35)

        # 4.6 / 4.7: child entropies, also marked on the arch
        def s_value(name, value, info):
            tex = MathTex(name, r"\approx", fmt(value), font_size=BODY_SIZE, color=IMPURITY)
            tex.next_to(info, DOWN, buff=0.2)
            return clamp_x(tex)

        s1 = s_value("S_1", CUTS[q_t]["S_left"], info_l)
        s2 = s_value("S_2", CUTS[q_t]["S_right"], info_r)
        p1 = q["left"][1] / sum(q["left"])
        p2 = q["right"][1] / sum(q["right"])
        mark1 = curve.mark(p1, CUTS[q_t]["S_left"], MathTex("S_1", font_size=28, color=IMPURITY), direction=DOWN)
        mark2 = curve.mark(p2, CUTS[q_t]["S_right"], MathTex("S_2", font_size=28, color=IMPURITY), direction=RIGHT)

        with self.voiceover(text="The left group is still pretty mixed, at about 0.96 bits.") as tracker:
            self.play(Write(s1), run_time=tracker.duration * 0.4)
            self.play(TransformFromCopy(s1[0], mark1), run_time=tracker.duration * 0.4)

        with self.voiceover(text="The right group is much more predictable, at about 0.59.") as tracker:
            self.play(Write(s2), run_time=tracker.duration * 0.4)
            self.play(TransformFromCopy(s2[0], mark2), run_time=tracker.duration * 0.4)

        # 4.8
        arrows = VGroup(
            *[
                MathTex(r"\downarrow", font_size=BODY_SIZE, color=GAIN).next_to(s, RIGHT, buff=0.15)
                for s in (s1, s2)
            ]
        )
        with self.voiceover(text="Both are lower than the 0.99 we started with.") as tracker:
            self.play(Indicate(s0_park, color=HIGHLIGHT), run_time=tracker.duration * 0.4)
            self.play(LaggedStart(*[FadeIn(a, shift=DOWN * 0.2) for a in arrows], lag_ratio=0.3),
                      run_time=tracker.duration * 0.4)
        self.play(FadeOut(arrows), run_time=FAST)

        # 4.9
        qmark = MathTex("?", font_size=BODY_SIZE + 12, color=HIGHLIGHT).move_to([cut_x(), VALUE_Y, 0])
        qmark.match_y(s1)
        with self.voiceover(text="So how do we combine them into one score?") as tracker:
            self.play(FadeIn(qmark, scale=0.6), run_time=min(NORMAL, tracker.duration))

        # 4.10: the naive average
        naive = MathTex(
            r"\frac{" + fmt(CUTS[q_t]["S_left"]) + "+" + fmt(CUTS[q_t]["S_right"]) + "}{2}",
            r"\;?",
            font_size=BODY_SIZE,
            color=TEXT_MUTED,
        ).move_to([0, FORMULA_Y, 0])
        naive[1].set_color(HIGHLIGHT)
        with self.voiceover(text="You might just average them.") as tracker:
            self.play(Write(naive[0]), ReplacementTransform(qmark, naive[1]), run_time=min(1.5, tracker.duration))

        # 4.11
        with self.voiceover(text="But should a group of seven count as much as a group of thirteen?") as tracker:
            self.play(
                Indicate(brace_l, color=HIGHLIGHT),
                Indicate(brace_r, color=HIGHLIGHT),
                ScaleInPlace(count_l, 1.3, rate_func=there_and_back),
                ScaleInPlace(count_r, 1.3, rate_func=there_and_back),
                run_time=tracker.duration * 0.6,
            )

        # 4.12: a cut that peels off one ball
        peel_t = min(CUTS, key=lambda t: min(sum(CUTS[t]["left"]), sum(CUTS[t]["right"])))
        peel = CUTS[peel_t]
        with self.voiceover(text="Imagine a cut that peels off one single ball.") as tracker:
            self.play(
                FadeOut(info_l, info_r, s1, s2),
                *balls.merge(),
                run_time=tracker.duration * 0.3,
            )
            self.play(t_val.animate.set_value(peel_t + 0.5), run_time=tracker.duration * 0.3)
            self.play(*balls.split_at(peel_t), run_time=tracker.duration * 0.2)
            lone = balls.side(peel_t, "left" if sum(peel["left"]) == 1 else "right")
            self.play(Circumscribe(lone[0][2], color=HIGHLIGHT, shape=Circle), run_time=tracker.duration * 0.2)

        # 4.13: the pure lone group fools a plain average
        def peel_value(which, value):
            grp = balls.side(peel_t, which)
            rel = r"=" if value == 0 else r"\approx"
            tex = MathTex("S", rel, fmt(value) if value else "0", font_size=BODY_SIZE, color=IMPURITY)
            tex.move_to([grp.get_center()[0], VALUE_Y, 0])
            return clamp_x(tex)

        pv_l = peel_value("left", peel["S_left"])
        pv_r = peel_value("right", peel["S_right"])
        plain = MathTex(
            r"\frac{" + (fmt(peel["S_left"]) if peel["S_left"] else "0") + "+" + fmt(peel["S_right"]) + "}{2}",
            r"\approx",
            fmt(peel["plain_avg"]),
            font_size=BODY_SIZE,
            color=TEXT_MUTED,
        ).move_to([0, FORMULA_Y, 0])
        check = MathTex(r"\checkmark", font_size=BODY_SIZE + 8, color=GAIN).next_to(plain, RIGHT, buff=0.3)
        xmark = VGroup(
            Line(UL * 0.18, -UL * 0.18), Line(UR * 0.18, -UR * 0.18)
        ).set_stroke(IMPURITY, 6).move_to(check)
        with self.voiceover(
            text="That tiny group is perfectly pure, so a plain average would call it a great question,"
        ) as tracker:
            self.play(Write(pv_l), Write(pv_r), run_time=tracker.duration * 0.35)
            self.play(ReplacementTransform(naive, plain), run_time=tracker.duration * 0.35)
            self.play(FadeIn(check, scale=1.4), run_time=tracker.duration * 0.2)

        with self.voiceover(
            text="even though the other nineteen balls are almost exactly as mixed as before."
        ) as tracker:
            self.play(Indicate(pv_r, color=IMPURITY), run_time=tracker.duration * 0.5)
            self.play(ReplacementTransform(check, xmark), run_time=tracker.duration * 0.3)

        # 4.14: weight by share
        def weight(which, ref):
            n = sum(peel[which])
            tex = MathTex(rf"\tfrac{{{n}}}{{{n_total}}}", font_size=BODY_SIZE + 4, color=TEXT)
            return clamp_x(tex.next_to(ref, DOWN, buff=0.2))

        w_l, w_r = weight("left", pv_l), weight("right", pv_r)
        with self.voiceover(text="So we weight each group by its share of the balls.") as tracker:
            self.play(FadeIn(w_l, shift=DOWN * 0.1), FadeIn(w_r, shift=DOWN * 0.1), run_time=tracker.duration * 0.35)
            self.play(
                Indicate(balls.side(peel_t, "left"), color=HIGHLIGHT, scale_factor=1.05),
                Indicate(balls.side(peel_t, "right"), color=HIGHLIGHT, scale_factor=1.05),
                run_time=tracker.duration * 0.45,
            )
        # back to x <= 12, with its braces and entropies
        self.play(FadeOut(pv_l, pv_r, w_l, w_r, plain, xmark), run_time=FAST)
        self.play(*balls.split_at(q_t), t_val.animate.set_value(q_t + 0.5), run_time=NORMAL)
        self.play(FadeIn(info_l, info_r, s1, s2), run_time=FAST)

        # 4.15: the information gain formula
        w1 = rf"\tfrac{{{sum(q['left'])}}}{{{n_total}}}"
        w2 = rf"\tfrac{{{sum(q['right'])}}}{{{n_total}}}"
        formula = MathTex("S_0", "-", w1, "S_1", "-", w2, "S_2", font_size=BODY_SIZE + 8, color=TEXT)
        formula.move_to([0, FORMULA_Y, 0])
        formula[3].set_color(IMPURITY)
        formula[6].set_color(IMPURITY)
        ig_word = label("information gain", BODY_SIZE, GAIN).next_to(formula, DOWN, buff=0.35)
        with self.voiceover(
            text="Entropy before, minus each group's entropy weighted by its share: that's the information gain."
        ) as tracker:
            self.play(
                TransformFromCopy(s0_park[0], formula[0]),
                TransformFromCopy(s1[0], formula[3]),
                TransformFromCopy(s2[0], formula[6]),
                TransformFromCopy(count_l, formula[2]),
                TransformFromCopy(count_r, formula[5]),
                FadeIn(formula[1], formula[4]),
                run_time=tracker.duration * 0.55,
            )
            self.play(Write(ig_word), run_time=tracker.duration * 0.35)

        # 4.16
        ig_val = MathTex(r"\approx", fmt(q["ig"]), font_size=BODY_SIZE + 8, color=GAIN)
        ig_val.next_to(formula, RIGHT, buff=0.2)
        VGroup(formula, ig_val).move_to([0, FORMULA_Y, 0])
        track_w = 4.0
        track = Rectangle(width=track_w, height=0.22).set_stroke(GRID, 2).set_fill(opacity=0)
        track.next_to(ig_word, DOWN, buff=0.35)
        fill = Rectangle(width=track_w * q["ig"] / ent["S0"], height=0.22).set_stroke(width=0).set_fill(GAIN, 1)
        fill.align_to(track, LEFT).match_y(track)
        bar_lo = label(fmt(q["ig"]), CAPTION_SIZE, GAIN).next_to(fill, DOWN, buff=0.1).align_to(fill, LEFT)
        bar_hi = label(fmt(ent["S0"]), CAPTION_SIZE, TEXT_MUTED).next_to(track, DOWN, buff=0.1).align_to(track, RIGHT)
        gain_bar = VGroup(track, fill, bar_lo, bar_hi)
        with self.voiceover(text="Here it's about 0.16 bits, out of the 0.99 we started with.") as tracker:
            self.play(Write(ig_val), ig_word.animate.match_x(VGroup(formula, ig_val)), run_time=tracker.duration * 0.35)
            self.play(FadeIn(track, bar_hi), GrowFromEdge(fill, LEFT), FadeIn(bar_lo), run_time=tracker.duration * 0.45)

        # 4.17: the general recipe, then park it top-left
        general = MathTex(
            "IG(Q)", "=", "S_0", "-", r"\sum_i", r"\frac{N_i}{N}", "S_i", font_size=BODY_SIZE + 8, color=TEXT
        ).move_to([0, FORMULA_Y, 0])
        general[6].set_color(IMPURITY)
        with self.voiceover(
            text="That's a modest step, and it's the same recipe for any number of groups."
        ) as tracker:
            self.play(FadeOut(gain_bar), run_time=FAST)
            self.play(
                TransformMatchingTex(formula, general),
                FadeOut(ig_val),
                run_time=tracker.duration * 0.45,
            )
            self.play(
                general.animate.scale(0.6).to_corner(UL, buff=EDGE_BUFF),
                FadeOut(ig_word),
                run_time=tracker.duration * 0.3,
            )

        # 4.18: every gap is a candidate
        gap_ticks = VGroup(
            *[
                Line([balls.rest_x(t + 0.5), BALL_Y - 0.25, 0], [balls.rest_x(t + 0.5), BALL_Y + 0.45, 0])
                .set_stroke(HIGHLIGHT, 3, opacity=0.4)
                for t in sorted(CUTS)
            ]
        )
        with self.voiceover(text="Of course, twelve was just one candidate.") as tracker:
            self.play(
                FadeOut(info_l, info_r, s1, s2, cut, cut_label, curve, ours, mark1, mark2, s0_park),
                *balls.merge(),
                run_time=tracker.duration * 0.45,
            )
            self.play(LaggedStart(*[Create(tk) for tk in gap_ticks], lag_ratio=0.08), run_time=tracker.duration * 0.45)

        # 4.19: pause and guess
        with self.voiceover(
            text="Before I show you, pause and guess: which cut on this line do you think lowers the uncertainty the most?"
        ) as tracker:
            self.play(
                LaggedStart(*[Indicate(tk, color=HIGHLIGHT, scale_factor=1.3) for tk in gap_ticks], lag_ratio=0.1),
                run_time=tracker.duration * 0.6,
            )
        self.wait(3)

        # 4.20: gain bars, x-aligned with the gaps
        max_ig = max(d["ig"] for d in CUTS.values())
        baseline = Line([-SAFE_X + 0.3, BARS_BASE_Y, 0], [SAFE_X - 0.3, BARS_BASE_Y, 0], color=GRID, stroke_width=2)
        axis_name = label("information gain", CAPTION_SIZE, GAIN)
        axis_name.move_to([-SAFE_X, BARS_BASE_Y + BARS_MAX_H + 0.2, 0], aligned_edge=LEFT)
        bars = {}
        for t, d in sorted(CUTS.items()):
            h = max(BARS_MAX_H * d["ig"] / max_ig, 0.02)
            bar = Rectangle(width=BAR_W, height=h).set_stroke(width=0).set_fill(TEXT_MUTED, 1)
            bar.move_to([balls.rest_x(t + 0.5), BARS_BASE_Y, 0], aligned_edge=DOWN)
            bars[t] = bar
        with self.voiceover(text='Now "which question should come first" has a mechanical answer.') as tracker:
            self.play(Create(baseline), FadeIn(axis_name), run_time=min(1.5, tracker.duration))

        # 4.21: sweep every threshold, then pick the tallest bar
        t_val.set_value(0.5)
        with self.voiceover(text="Try every threshold, compute the gain of each,") as tracker:
            self.play(FadeIn(cut), FadeIn(cut_label), run_time=FAST)
            step = max(tracker.duration - FAST, 4.0) / len(bars)
            for t in sorted(bars):
                self.play(t_val.animate.set_value(t + 0.5), GrowFromEdge(bars[t], DOWN), run_time=step, rate_func=linear)

        winner = bars[best_t]
        win_label = VGroup(
            MathTex(rf"x \le {best_t}", font_size=CAPTION_SIZE + 6, color=GAIN),
            MathTex(fmt(CUTS[best_t]["ig"]), font_size=CAPTION_SIZE + 6, color=GAIN),
        ).arrange(DOWN, buff=0.08)
        win_label.next_to(winner, UP, buff=0.22)
        with self.voiceover(text="and pick the tallest bar.") as tracker:
            self.play(
                winner.animate.set_fill(GAIN),
                t_val.animate.set_value(best_t + 0.5),
                run_time=tracker.duration * 0.4,
            )
            self.play(Circumscribe(winner, color=HIGHLIGHT), FadeIn(win_label, shift=UP * 0.1),
                      run_time=tracker.duration * 0.5)

        # 4.22: ghost of the celebrity grid
        grid_icon = CelebrityGrid(8, 8, icon_height=0.45, spacing=0.6).scale(0.25).to_corner(UR, buff=EDGE_BUFF)
        grid_icon.set_opacity(0.4)
        with self.voiceover(
            text="It's Twenty Questions again, only now the computer keeps the books."
        ) as tracker:
            self.play(FadeIn(grid_icon), run_time=min(1.5, tracker.duration))

        # 4.23: clipping off one ball = "Is it Angelina Jolie?"
        edge_ts = [t for t, d in CUTS.items() if min(sum(d["left"]), sum(d["right"])) == 1]
        jolie = grid_icon.icon(2, 6)
        with self.voiceover(
            text='A cut that clips off one ball is the "Angelina Jolie" question, with a tiny bar.'
        ) as tracker:
            self.play(
                *[Indicate(bars[t], color=IMPURITY, scale_factor=1.6) for t in edge_ts],
                *[Indicate(gap_ticks[t], color=IMPURITY, scale_factor=1.3) for t in edge_ts],
                jolie.animate.set_opacity(1).set_color(HIGHLIGHT).scale(1.8),
                run_time=tracker.duration * 0.6,
            )

        # 4.24: the winner
        with self.voiceover(text="The winner leaves both sides more predictable.") as tracker:
            self.play(Indicate(winner, color=GAIN, scale_factor=1.15), run_time=tracker.duration * 0.4)
            self.play(*balls.split_at(best_t), run_time=tracker.duration * 0.4)
        self.wait(NORMAL)
        # Indicate on balls.side(...) leaves those temporary groups in the scene: keep anything holding a ball
        ball_family = set(balls.get_family())
        everything_else = [m for m in self.mobjects if not set(m.get_family()) & ball_family]
        self.play(*[FadeOut(m) for m in everything_else], run_time=NORMAL)

        self.wait(FAST)
