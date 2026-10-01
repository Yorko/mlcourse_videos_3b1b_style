"""Scene 6: Back to the bank, numeric features + Gini aside (docs/STORYBOARD.md, rows 6.1-6.16)."""

import json
from pathlib import Path

import numpy as np
from manim import (
    UL,
    Axes,
    Brace,
    Circumscribe,
    Create,
    DashedVMobject,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    NumberLine,
    Rectangle,
    ReplacementTransform,
    RoundedRectangle,
    Text,
    Transform,
    TransformFromCopy,
    ValueTracker,
    VGroup,
    VMobject,
    Write,
    always_redraw,
)
from manim_voiceover import VoiceoverScene

from components.tree_diagram import TreeDiagram
from style import *
from voice import speech_service

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AGE = json.loads((DATA_DIR / "age.json").read_text())
LOAN_TREE = json.loads((DATA_DIR / "loan_tree.json").read_text())

CLIENTS = AGE["clients"]
AGE_CUTS = {c["t"]: c for c in AGE["age_cuts"]}
SWITCH = AGE["age_switch_points"]
BEST = AGE["age_best"]
BAD = AGE["bad_cut"]
CURVES = AGE["impurity_curves"]

# Layout
TABLE_CENTER = np.array([-3.5, -0.55, 0])
ROW_H = 0.42
COL_W = 1.6
LINE_Y = 1.0
SALARY_Y = -1.0
LINE_X = (-4.6, 6.1)
TICK_H = 0.55
LABEL_Y = LINE_Y + 0.6
BAR_BASE_Y = -2.8
BAR_SCALE = 5.0  # screen units per bit of information gain
BAR_W = 0.3
DOT_R = 0.11


def label(text, size=CAPTION_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def class_color(defaulted):
    return CLASS_1 if defaulted else CLASS_0


def fmt(t):
    return f"{t:g}"


def number_line(lo, hi, step, y):
    line = NumberLine(
        x_range=[lo, hi, step],
        length=LINE_X[1] - LINE_X[0],
        color=GRID,
        include_numbers=True,
        font_size=CAPTION_SIZE,
        label_direction=DOWN,
    )
    line.numbers.set_color(TEXT_MUTED)
    line.shift(np.array([LINE_X[0], y, 0]) - line.n2p(lo))
    return line


def counts_label(counts):
    """'3 / 0' with the repaid count in blue and the defaulted count in yellow."""
    b = label(str(counts[0]), color=CLASS_0)
    s = label("/", color=TEXT_MUTED)
    y = label(str(counts[1]), color=CLASS_1)
    return VGroup(b, s, y).arrange(RIGHT, buff=0.08)


class NumericGini(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())

        # 6.1: the loan tree parks in the corner as an icon
        icon = TreeDiagram(LOAN_TREE).scale(0.3).to_corner(UL, buff=EDGE_BUFF * 0.6)
        with self.voiceover(text="Back to the bank.") as tracker:
            self.play(FadeIn(icon, scale=0.8), run_time=min(1.0, tracker.duration))

        # 6.2: the 11-client table (article order)
        header = VGroup(label("Age"), label("Defaulted"))
        rows = VGroup(
            *[
                VGroup(
                    label(str(c["age"])),
                    label("yes" if c["defaulted"] else "no", color=class_color(c["defaulted"])),
                )
                for c in CLIENTS
            ]
        )
        for i, g in enumerate([header, *rows]):
            for j, cell in enumerate(g):
                cell.move_to(TABLE_CENTER + np.array([(j - 0.5) * COL_W, (len(rows) / 2 - i) * ROW_H, 0]))
        top = TABLE_CENTER[1] + (len(rows) / 2 + 0.5) * ROW_H
        bottom = TABLE_CENTER[1] - (len(rows) / 2 + 0.5) * ROW_H
        x0, x1 = TABLE_CENTER[0] - COL_W, TABLE_CENTER[0] + COL_W
        rules = VGroup(
            Line([x0, top - ROW_H, 0], [x1, top - ROW_H, 0], color=GRID, stroke_width=2),
            Line([TABLE_CENTER[0], top, 0], [TABLE_CENTER[0], bottom, 0], color=GRID, stroke_width=2),
        )
        with self.voiceover(text="A real feature, a measurement like age, can take dozens of values.") as tracker:
            self.play(FadeIn(header), Create(rules), run_time=FAST)
            self.play(
                LaggedStart(*[FadeIn(r, shift=DOWN * 0.15) for r in rows], lag_ratio=0.15),
                run_time=tracker.duration * 0.6,
            )
            self.play(Indicate(header[0], color=HIGHLIGHT), run_time=min(1.0, tracker.duration * 0.3))

        # 6.3: each row flies onto the age line as a dot
        age_line = number_line(15, 66, 5, LINE_Y)
        dots = VGroup(
            *[
                Dot(age_line.n2p(c["age"]), radius=DOT_R, color=class_color(c["defaulted"]))
                for c in CLIENTS
            ]
        )
        age_name = label("age", color=TEXT_MUTED).next_to(age_line, LEFT, buff=0.3)
        with self.voiceover(text="Do we really have to try every possible cut?") as tracker:
            self.play(Create(age_line), FadeIn(age_name), run_time=FAST)
            self.play(
                LaggedStart(*[ReplacementTransform(r, d) for r, d in zip(rows, dots)], lag_ratio=0.12),
                FadeOut(header, rules),
                run_time=tracker.duration - FAST,
            )

        # 6.4: a faint tick at every midpoint between neighboring distinct ages
        def tick(t, color=TEXT_MUTED, opacity=0.3):
            p = age_line.n2p(t)
            return Line(p + DOWN * TICK_H / 2, p + UP * TICK_H / 2, color=color, stroke_width=3).set_opacity(opacity)

        ticks = {t: tick(t) for t in AGE_CUTS}
        with self.voiceover(text="Sort the clients by age and look at where the color switches.") as tracker:
            self.play(
                LaggedStart(*[Create(m) for m in ticks.values()], lag_ratio=0.2),
                run_time=tracker.duration * 0.7,
            )

        # 6.5: only the switch points survive
        switch_labels = VGroup(
            *[label(fmt(t), color=HIGHLIGHT).move_to([age_line.n2p(t)[0], LABEL_Y, 0]) for t in SWITCH]
        )
        for left, right in zip(switch_labels[:-1], switch_labels[1:]):  # keep "30" and "32" apart
            overlap = left.get_right()[0] + 0.2 - right.get_left()[0]
            if overlap > 0:
                left.shift(LEFT * overlap / 2)
                right.shift(RIGHT * overlap / 2)
        with self.voiceover(
            text="Here it switches only five times, and those five midpoints are exactly the cuts the tree ends up using."
        ) as tracker:
            self.play(
                *[FadeOut(m) for t, m in ticks.items() if t not in SWITCH],
                run_time=tracker.duration * 0.3,
            )
            self.play(
                *[ticks[t].animate.set_stroke(HIGHLIGHT, opacity=1) for t in SWITCH],
                LaggedStart(*[FadeIn(lab, shift=DOWN * 0.1) for lab in switch_labels], lag_ratio=0.2),
                run_time=tracker.duration * 0.5,
            )

        # 6.6: a bad cut at 17.5
        cut_x = ValueTracker(BAD["t"])

        def cut_line(color):
            p = age_line.n2p(cut_x.get_value())
            return DashedLine(p + DOWN * 0.45, p + UP * 0.45, color=color, stroke_width=4, dash_length=0.08)

        cut = cut_line(IMPURITY)
        with self.voiceover(text="So why would you never pick, say, 17.5?") as tracker:
            self.play(Create(cut), run_time=min(1.0, tracker.duration))

        # 6.7
        ages = [c["age"] for c in CLIENTS]
        pair = VGroup(*[dots[i] for i in sorted(range(len(ages)), key=lambda i: ages[i])[:2]])
        with self.voiceover(text="Both seventeen and eighteen defaulted.") as tracker:
            self.play(Indicate(pair, color=HIGHLIGHT, scale_factor=1.6), run_time=min(1.2, tracker.duration))

        # 6.8: slide to 19; braces track the cut, the gain bar roughly doubles
        brace_y = LINE_Y - 0.75

        def side_braces():
            c = age_line.n2p(cut_x.get_value())[0]
            left = Line([LINE_X[0], brace_y, 0], [c - 0.05, brace_y, 0])
            right = Line([c + 0.05, brace_y, 0], [LINE_X[1], brace_y, 0])
            return VGroup(
                Brace(left, DOWN, buff=0, color=TEXT_MUTED),
                Brace(right, DOWN, buff=0, color=TEXT_MUTED),
            )

        braces = always_redraw(side_braces)
        before, after = AGE_CUTS[BAD["t"]], AGE_CUTS[BAD["slide_to"]]

        def brace_labels(entry):
            g = VGroup(counts_label(entry["left"]), counts_label(entry["right"]))
            b = side_braces()
            for lab, br in zip(g, b):
                lab.next_to(br, DOWN, buff=0.1)
            return g

        side_counts = brace_labels(before)

        bar_x = 3.6

        def gain_bar(ig, color):
            rect = Rectangle(width=0.6, height=max(ig * BAR_SCALE, 0.02)).set_fill(color, 1).set_stroke(width=0)
            return rect.move_to([bar_x, BAR_BASE_Y, 0], aligned_edge=DOWN)

        def gain_text(ig):
            return label(f"IG = {ig:.3f}", color=TEXT_MUTED).next_to(gain_bar(ig, GAIN), RIGHT, buff=0.25)

        mini_bar, mini_text = gain_bar(BAD["ig"], GAIN), gain_text(BAD["ig"])
        mini_base = Line([bar_x - 0.6, BAR_BASE_Y, 0], [bar_x + 0.6, BAR_BASE_Y, 0], color=GRID, stroke_width=2)
        with self.voiceover(
            text="Slide the cut up to 19 and the left side stays pure, but the right side loses a defaulter "
            "and gets cleaner, so the gain roughly doubles."
        ) as tracker:
            self.play(
                FadeIn(braces, side_counts),
                Create(mini_base),
                GrowFromEdge(mini_bar, DOWN),
                FadeIn(mini_text),
                run_time=tracker.duration * 0.3,
            )
            cut.add_updater(lambda m: m.become(cut_line(HIGHLIGHT)))
            self.play(
                cut_x.animate.set_value(BAD["slide_to"]),
                Transform(side_counts, brace_labels(after)),
                Transform(mini_bar, gain_bar(BAD["ig_after"], GAIN)),
                Transform(mini_text, gain_text(BAD["ig_after"])),
                run_time=tracker.duration * 0.5,
            )
            cut.clear_updaters()
        self.play(FadeOut(braces, side_counts, mini_bar, mini_text, mini_base, cut), run_time=FAST)

        # 6.9: gain bars at the five switch points
        bar_base = Line([LINE_X[0], BAR_BASE_Y, 0], [LINE_X[1], BAR_BASE_Y, 0], color=GRID, stroke_width=2)
        bars = VGroup()
        for t in SWITCH:
            rect = Rectangle(width=BAR_W, height=AGE_CUTS[t]["ig"] * BAR_SCALE).set_fill(TEXT_MUTED, 1)
            rect.set_stroke(width=0).move_to([age_line.n2p(t)[0], BAR_BASE_Y, 0], aligned_edge=DOWN)
            bars.add(rect)
        bars_title = label("information gain", color=TEXT_MUTED).next_to(bar_base, UP, buff=0.15).align_to(bar_base, RIGHT)
        with self.voiceover(
            text="That's a general fact: the best cut always sits at one of these switch points."
        ) as tracker:
            self.play(Create(bar_base), FadeIn(bars_title), run_time=FAST)
            self.play(
                LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.2),
                run_time=tracker.duration * 0.7 - FAST,
            )

        # 6.10: the winner
        win = bars[SWITCH.index(BEST["t"])]
        win_label = label(f"entropy IG ≈ {BEST['ig']:.2f}", color=GAIN)
        win_label.next_to(win, RIGHT, buff=0.2).align_to(win, UP)
        with self.voiceover(text="Here the winner is 43.5, which becomes the root of the tree.") as tracker:
            self.play(
                win.animate.set_fill(GAIN),
                ticks[BEST["t"]].animate.set_stroke(GAIN),
                switch_labels[SWITCH.index(BEST["t"])].animate.set_color(GAIN),
                FadeIn(win_label),
                run_time=tracker.duration * 0.35,
            )
            self.play(
                Circumscribe(win, color=HIGHLIGHT),
                Flash(icon.node(icon.root_id), color=HIGHLIGHT, flash_radius=0.3),
                Indicate(icon.node(icon.root_id), color=HIGHLIGHT),
                run_time=tracker.duration * 0.45,
            )

        # 6.11: the same trick on salary
        sal = AGE["salary_switch_points"]
        sal_line = number_line(20, 105, 10, SALARY_Y)
        sal_dots = VGroup(
            *[
                Dot(sal_line.n2p(c["salary"]), radius=DOT_R, color=class_color(c["defaulted"]))
                for c in CLIENTS
            ]
        )
        sal_name = label("salary, $k", color=TEXT_MUTED).next_to(sal_line, LEFT, buff=0.3)
        sal_ticks = VGroup(
            *[
                Line(sal_line.n2p(t) + DOWN * TICK_H / 2, sal_line.n2p(t) + UP * TICK_H / 2, color=HIGHLIGHT, stroke_width=3)
                for t in sal
            ]
        )
        with self.voiceover(text="With more features, you do the same trick for each one.") as tracker:
            self.play(FadeOut(bars, bar_base, bars_title, win_label), run_time=FAST)
            self.play(FadeIn(sal_line, sal_dots, sal_name), run_time=tracker.duration * 0.3)
            self.play(
                LaggedStart(*[Create(t) for t in sal_ticks], lag_ratio=0.15),
                LaggedStart(*[Flash(t.get_center(), color=HIGHLIGHT, flash_radius=0.25) for t in sal_ticks], lag_ratio=0.15),
                run_time=tracker.duration * 0.5,
            )

        # 6.12: the aside panel with the entropy arch
        lines_group = VGroup(age_line, age_name, dots, *[ticks[t] for t in SWITCH], switch_labels,
                             sal_line, sal_name, sal_dots, sal_ticks)
        panel = RoundedRectangle(width=8, height=5.5, corner_radius=0.25).move_to(DOWN * 0.3)
        panel.set_stroke(GRID, 2).set_fill(BACKGROUND, 1)
        panel_title = label("Aside: Gini impurity", BODY_SIZE).next_to(panel.get_top(), DOWN, buff=0.3)
        axes = Axes(
            x_range=[0, 1, 0.5],
            y_range=[0, 1, 0.5],
            x_length=3.8,
            y_length=2.9,
            axis_config={"color": GRID, "include_tip": False, "font_size": CAPTION_SIZE},
        ).move_to(panel.get_center() + LEFT * 1.6 + DOWN * 0.2)
        for ax in (axes.x_axis, axes.y_axis):
            ax.add_numbers([0.5, 1], num_decimal_places=1, font_size=CAPTION_SIZE - 4, color=TEXT_MUTED)
        p_label = MathTex("p", color=TEXT_MUTED, font_size=CAPTION_SIZE + 4).next_to(axes.x_axis, RIGHT, buff=0.15)

        def curve(ys, color, scale=1.0):
            pts = [axes.c2p(p, y * scale) for p, y in zip(CURVES["p"], ys)]
            return VMobject(color=color, stroke_width=4).set_points_smoothly(pts)

        entropy_curve = curve(CURVES["entropy"], IMPURITY)
        with self.voiceover(
            text="One small confession: this particular tree was actually built with a cousin of entropy called Gini impurity."
        ) as tracker:
            self.play(FadeOut(lines_group), run_time=FAST)
            self.play(FadeIn(panel), FadeIn(panel_title), Create(axes), FadeIn(p_label), run_time=tracker.duration * 0.35)
            self.play(Create(entropy_curve), run_time=tracker.duration * 0.4)

        # 6.13: draw two clients from a small cluster (the 11 clients' colors)
        right_x = panel.get_center()[0] + 2.2
        cluster = VGroup(
            *[Dot(radius=0.09, color=class_color(c["defaulted"])) for c in CLIENTS]
        ).arrange_in_grid(rows=2, buff=0.12)
        cluster.move_to([right_x, panel.get_center()[1] + 1.4, 0])
        blue_i = next(i for i, c in enumerate(CLIENTS) if not c["defaulted"])
        yellow_i = next(i for i, c in enumerate(CLIENTS) if c["defaulted"])
        drawn = VGroup(
            Dot(radius=0.14, color=CLASS_0), Dot(radius=0.14, color=CLASS_1)
        ).arrange(RIGHT, buff=0.35).move_to([right_x, panel.get_center()[1] + 0.55, 0])
        with self.voiceover(text="Draw two clients at random.") as tracker:
            self.play(FadeIn(cluster, lag_ratio=0.1), run_time=tracker.duration * 0.4)
            self.play(
                TransformFromCopy(cluster[blue_i], drawn[0]),
                TransformFromCopy(cluster[yellow_i], drawn[1]),
                run_time=tracker.duration * 0.5,
            )

        # 6.14: the Gini formula
        formula = MathTex("G = 2p(1-p)", color=TEXT, font_size=BODY_SIZE).move_to([right_x, panel.get_center()[1] - 0.2, 0])
        with self.voiceover(text="How likely is it that one repaid and one defaulted?") as tracker:
            self.play(Indicate(drawn, color=HIGHLIGHT, scale_factor=1.3), run_time=tracker.duration * 0.35)
            self.play(Write(formula), run_time=tracker.duration * 0.55)

        # 6.15: Gini, then doubled to compare with entropy
        gini_curve = curve(CURVES["gini"], TEXT)
        doubled = curve(CURVES["gini"], TEXT, scale=2)
        dashed = DashedVMobject(doubled.copy(), num_dashes=40)
        misclass = curve(CURVES["misclassification"], TEXT_MUTED, scale=2).set_stroke(width=2, opacity=0.6)
        legend = VGroup(
            label("entropy", color=IMPURITY),
            label("2 × Gini", color=TEXT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([right_x, panel.get_center()[1] - 1.15, 0])
        foot_text = label("misclassification error, rarely used", CAPTION_SIZE - 4, TEXT_MUTED)
        foot_key = Line(LEFT * 0.25, RIGHT * 0.25, color=TEXT_MUTED, stroke_width=2).set_opacity(0.6)
        footnote = VGroup(foot_key, foot_text).arrange(RIGHT, buff=0.15)
        footnote.next_to(panel.get_bottom(), UP, buff=0.25)
        with self.voiceover(
            text="Gini tops out at one half and entropy at one, so double it to compare, "
            "and the two curves closely track each other."
        ) as tracker:
            self.play(Create(gini_curve), run_time=tracker.duration * 0.3)
            self.play(Transform(gini_curve, doubled), FadeIn(legend), run_time=tracker.duration * 0.3)
            self.play(FadeOut(gini_curve), FadeIn(dashed), run_time=tracker.duration * 0.05)
            gini_curve = dashed
            self.play(Create(misclass), FadeIn(footnote), run_time=tracker.duration * 0.25)

        # 6.16
        with self.voiceover(text="That's why they usually pick the same splits.") as tracker:
            self.play(
                Indicate(VGroup(entropy_curve, gini_curve), color=HIGHLIGHT, scale_factor=1.05),
                run_time=min(1.5, tracker.duration),
            )
        self.wait(NORMAL)
        self.play(
            FadeOut(VGroup(panel, panel_title, axes, p_label, entropy_curve, gini_curve, misclass, cluster,
                           drawn, formula, legend, footnote, icon)),
            run_time=NORMAL,
        )
