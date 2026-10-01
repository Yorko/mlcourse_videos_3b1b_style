"""Scene 3: Entropy (docs/STORYBOARD.md, rows 3.1-3.30).

BallRow, Jar and EntropyCurve live here (not in components/) while scenes 4
and 5 are written in parallel; they follow the storyboard's component specs.
"""

import json
from pathlib import Path

import numpy as np
from manim import (
    DL,
    PI,
    TAU,
    UL,
    ArcBetweenPoints,
    Arrow,
    Axes,
    Brace,
    Circle,
    Circumscribe,
    Create,
    CurvedArrow,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Flash,
    GrowArrow,
    GrowFromCenter,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    ORIGIN,
    Line,
    MathTex,
    NumberLine,
    Rectangle,
    ReplacementTransform,
    Rotate,
    Sector,
    Text,
    TransformFromCopy,
    TransformMatchingTex,
    ValueTracker,
    VGroup,
    VMobject,
    Write,
    always_redraw,
    linear,
)
from manim_voiceover import VoiceoverScene

from components.celebrity_grid import CelebrityGrid
from components.tree_diagram import TreeDiagram
from style import *
from voice import speech_service

DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "balls.json").read_text())
CLASS_COLOR = {"blue": CLASS_0, "yellow": CLASS_1}

BALLS_Y = 1.8
BALLS_WIDTH = 11
JAR_XS = (-4, 0, 4)
JAR_Y = -1.2
MATH_SIZE = 44
TAG_SIZE = 34


def label(text, size=BODY_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def binary_entropy(p):
    """The curve S(p) for a two-colour jar (only used to draw the arch)."""
    if p <= 0 or p >= 1:
        return 0.0
    return float(-p * np.log2(p) - (1 - p) * np.log2(1 - p))


# --- Components (storyboard section 0) ----------------------------------------


class BallRow(VGroup):
    """Dots (r = 0.15) on a NumberLine(0..n-1), coloured CLASS_0 / CLASS_1."""

    def __init__(self, colors, width=BALLS_WIDTH, radius=0.15, y=BALLS_Y, **kwargs):
        super().__init__(**kwargs)
        n = len(colors)
        self.colors = list(colors)
        self.line = NumberLine(
            x_range=[0, n - 1, 1],
            length=width,
            color=GRID,
            include_numbers=True,
            font_size=CAPTION_SIZE,
            decimal_number_config={"num_decimal_places": 0},
        )
        self.line.numbers.set_color(TEXT_MUTED)
        self.dots = VGroup(
            *[Dot(self.line.n2p(i), radius=radius, color=CLASS_COLOR[c]) for i, c in enumerate(colors)]
        )
        self.add(self.line, self.dots)
        self.shift(UP * y - self.line.n2p((n - 1) / 2))

    def indices(self, color):
        return [i for i, c in enumerate(self.colors) if c == color]


class Jar(VGroup):
    """A U-shaped jar with balls packed inside. ``set_p(p)`` recolours to a yellow fraction p."""

    def __init__(self, n_blue, n_yellow, radius=0.15, cols=5, seed=3, **kwargs):
        super().__init__(**kwargs)
        n = n_blue + n_yellow
        rows = int(np.ceil(n / cols))
        step = 2 * radius + 0.06
        inner_w, inner_h = cols * step, rows * step
        w, h = inner_w + 0.24, inner_h + 0.45
        rc = 0.2  # corner radius
        self.outline = VMobject(stroke_color=TEXT_MUTED, stroke_width=4)
        self.outline.set_points_as_corners([[-w / 2, h, 0], [-w / 2, rc, 0]])
        for piece in (
            ArcBetweenPoints([-w / 2, rc, 0], [-w / 2 + rc, 0, 0], angle=PI / 2),
            Line([-w / 2 + rc, 0, 0], [w / 2 - rc, 0, 0]),
            ArcBetweenPoints([w / 2 - rc, 0, 0], [w / 2, rc, 0], angle=PI / 2),
            Line([w / 2, rc, 0], [w / 2, h, 0]),
        ):
            self.outline.append_points(piece.points)
        self.balls = VGroup()
        for i in range(n):
            r, c = divmod(i, cols)
            x = -inner_w / 2 + step / 2 + c * step
            y = 0.12 + step / 2 + r * step
            self.balls.add(Dot([x, y, 0], radius=radius))
        # a fixed shuffle so the colours look mixed rather than layered
        self.order = np.random.default_rng(seed).permutation(n)
        self.add(self.outline, self.balls)
        self.center()
        self.set_counts(n_blue)

    def set_counts(self, n_blue):
        for rank, idx in enumerate(self.order):
            self.balls[idx].set_color(CLASS_0 if rank < n_blue else CLASS_1)
        return self

    def set_p(self, p_yellow):
        n = len(self.balls)
        return self.set_counts(n - int(round(p_yellow * n)))


class EntropyCurve(VGroup):
    """Axes(0..1, 0..1), the entropy arch, and a tracker-driven dot."""

    def __init__(self, width=6, height=3.5, **kwargs):
        super().__init__(**kwargs)
        self.axes = Axes(
            x_range=[0, 1, 0.5],
            y_range=[0, 1, 0.5],
            x_length=width,
            y_length=height,
            tips=False,
            axis_config={"color": GRID, "stroke_width": 3},
        )
        ticks = VGroup(
            *[
                label(f"{v:g}", CAPTION_SIZE, TEXT_MUTED).next_to(self.axes.c2p(v, 0), DOWN, buff=0.2)
                for v in (0, 0.5, 1)
            ]
        )
        y_tick = label("1", CAPTION_SIZE, TEXT_MUTED).next_to(self.axes.c2p(0, 1), LEFT, buff=0.2)
        x_label = label("fraction yellow", CAPTION_SIZE, TEXT_MUTED).next_to(ticks, DOWN, buff=0.15)
        y_label = label("entropy (bits)", CAPTION_SIZE, TEXT_MUTED).next_to(self.axes.c2p(0, 1), UP, buff=0.25)
        self.labels = VGroup(ticks, y_tick, x_label, y_label)
        self.curve = self.axes.plot(binary_entropy, x_range=[0, 1, 0.0025], color=IMPURITY, stroke_width=5)
        self.p = ValueTracker(0)
        self.dot = always_redraw(
            lambda: Dot(self.point(self.p.get_value()), radius=0.09, color=TEXT)
        )
        self.add(self.axes, self.labels, self.curve, self.dot)

    def point(self, p, value=None):
        return self.axes.c2p(p, binary_entropy(p) if value is None else value)


def ghost_tree():
    """A faint silhouette of the tree we'll eventually grow (data/balls.json)."""
    nodes = {n["id"]: n for n in DATA["tree"]["nodes"]}

    def spec(nid):
        n = nodes[nid]
        if n["leaf"]:
            return {"id": str(nid), "leaf": n["prediction"]}
        return {"id": str(nid), "q": n["question"], "no": spec(n["left"]), "yes": spec(n["right"])}

    tree = TreeDiagram(
        spec(0),
        labels=False,
        h_spacing=0.5,
        level_gap=0.5,
        leaf_colors=CLASS_COLOR,
        dot_radius=0.09,
    )
    for edge in tree.edges.values():
        edge.set_color(TEXT_MUTED)
    return tree


# --- Scene ----------------------------------------------------------------------


class Entropy(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())
        colors = DATA["colors"]
        n = len(colors)
        n_blue, n_yellow = DATA["counts"]["blue"], DATA["counts"]["yellow"]
        surprisal = DATA["surprisal"]
        s0 = DATA["entropy"]["S0"]

        # carried over from the end of scene 2
        grid_icon = CelebrityGrid(8, 8, icon_height=0.45, spacing=0.6).set_opacity(0.3)
        grid_icon.scale(0.25).to_corner(UL, buff=EDGE_BUFF)
        self.add(grid_icon)

        balls = BallRow(colors)

        # 3.1
        with self.voiceover(text="Let's switch to a simpler world.") as tracker:
            self.play(FadeOut(grid_icon), run_time=min(1.0, tracker.duration))

        # 3.2
        count_blue = label(f"{n_blue} blue", BODY_SIZE, CLASS_0).move_to([-2.5, 2.9, 0])
        count_yellow = label(f"{n_yellow} yellow", BODY_SIZE, CLASS_1).move_to([2.5, 2.9, 0])
        with self.voiceover(text="Here are twenty balls on a line, nine blue and eleven yellow.") as tracker:
            self.play(Create(balls.line), run_time=tracker.duration * 0.3)
            self.play(
                LaggedStart(*[GrowFromCenter(d) for d in balls.dots], lag_ratio=0.15),
                run_time=tracker.duration * 0.45,
            )
            self.play(FadeIn(count_blue, shift=DOWN * 0.2), FadeIn(count_yellow, shift=DOWN * 0.2), run_time=FAST)

        # 3.3
        half = n // 2
        nums = balls.line.numbers
        brace_l = Brace(VGroup(*balls.dots[:half], *nums[:half]), DOWN, color=TEXT_MUTED)
        brace_r = Brace(VGroup(*balls.dots[half:], *nums[half:]), DOWN, color=TEXT_MUTED)
        soft_l = label("mostly blue", CAPTION_SIZE, TEXT_MUTED).next_to(brace_l, DOWN, buff=0.15)
        soft_r = label("mostly yellow", CAPTION_SIZE, TEXT_MUTED).next_to(brace_r, DOWN, buff=0.15)
        with self.voiceover(
            text="Blues tend to sit on the left and yellows on the right, so a ball's position is a clue to its color."
        ) as tracker:
            self.play(GrowFromCenter(brace_l), FadeIn(soft_l), run_time=tracker.duration * 0.25)
            self.play(GrowFromCenter(brace_r), FadeIn(soft_r), run_time=tracker.duration * 0.25)
            self.wait(tracker.duration * 0.3)
            self.play(FadeOut(brace_l, brace_r, soft_l, soft_r), run_time=FAST)

        # 3.4: a faint "goal" icon, stays until scene 5
        goal = ghost_tree()
        goal.scale_to_fit_height(1.0).move_to([5.5, 3.0, 0]).set_opacity(0.3)
        with self.voiceover(text="Eventually we'll build a tree that predicts color from position.") as tracker:
            self.play(FadeOut(count_blue, count_yellow), run_time=FAST)
            self.play(FadeIn(goal), run_time=tracker.duration * 0.5)

        # 3.5
        uncertain = label("uncertainty?", BODY_SIZE, HIGHLIGHT).move_to(UP * 0.3)
        with self.voiceover(text="But first, before asking anything, how uncertain are we?") as tracker:
            self.play(Write(uncertain), run_time=tracker.duration * 0.5)

        # 3.6: one ball hops out and back, then the two probabilities
        p_blue = MathTex(r"p_{\text{blue}}", "=", rf"\frac{{{n_blue}}}{{{n}}}", font_size=MATH_SIZE, color=CLASS_0)
        p_yellow = MathTex(
            r"p_{\text{yellow}}", "=", rf"\frac{{{n_yellow}}}{{{n}}}", font_size=MATH_SIZE, color=CLASS_1
        )
        p_blue.move_to([-2.5, 0.3, 0])
        p_yellow.move_to([2.5, 0.3, 0])
        drawn = balls.dots[balls.indices("blue")[3]]
        with self.voiceover(
            text="If I pull out a ball at random, it's blue with probability 9 out of 20 "
            "and yellow with probability 11 out of 20."
        ) as tracker:
            self.play(FadeOut(uncertain), run_time=FAST)
            self.play(drawn.animate(path_arc=-PI / 2).shift(UP * 1.0), run_time=tracker.duration * 0.15)
            self.play(drawn.animate(path_arc=PI / 2).shift(DOWN * 1.0), run_time=tracker.duration * 0.15)
            self.play(Write(p_blue), run_time=tracker.duration * 0.25)
            self.play(Write(p_yellow), run_time=tracker.duration * 0.25)

        # 3.7
        coin = Circle(radius=0.35).set_fill(TEXT_MUTED, 1).set_stroke(TEXT, 2).move_to(UP * 0.3)
        with self.voiceover(text="That's close to a coin flip.") as tracker:
            self.play(FadeIn(coin), run_time=FAST)
            self.play(Rotate(coin, angle=2 * TAU, axis=UP), run_time=NORMAL)
            self.play(FadeOut(coin), run_time=FAST)

        # 3.8
        with self.voiceover(text="You'd have a hard time betting either way."):
            pass

        # 3.9: balls shrink to the top, three jars appear
        jar_specs = [DATA["jars"][0], DATA["jars"][1], DATA["jars"][n // 2]]
        jars = VGroup(*[Jar(j["blue"], j["yellow"]) for j in jar_specs])
        for jar, x in zip(jars, JAR_XS):
            jar.move_to([x, JAR_Y, 0])
        balls.save_state()
        with self.voiceover(text="Compare a few jars.") as tracker:
            self.play(
                balls.animate.scale(0.6).to_edge(UP, buff=EDGE_BUFF),
                p_blue.animate.move_to([-2.5, 1.6, 0]),
                p_yellow.animate.move_to([2.5, 1.6, 0]),
                run_time=tracker.duration * 0.4,
            )
            self.play(LaggedStart(*[FadeIn(j, shift=UP * 0.2) for j in jars], lag_ratio=0.3), run_time=tracker.duration * 0.5)

        def jar_label(text, i, color=TEXT_MUTED):
            word = label(text, BODY_SIZE, color).next_to(jars[i], DOWN, buff=0.3)
            return word.align_to(jars[i].get_bottom() + DOWN * 0.6, DOWN)

        labels = [jar_label("none", 0), jar_label("a little", 1), jar_label("max", 2, IMPURITY)]
        lines = [
            "If every ball is yellow, there's no uncertainty at all.",
            "One blue among nineteen yellow, still very little.",
            "Ten and ten, as uncertain as it gets.",
        ]
        # 3.10, 3.11, 3.12
        for i, line in enumerate(lines):
            with self.voiceover(text=line) as tracker:
                self.play(Indicate(jars[i], color=HIGHLIGHT, scale_factor=1.1), run_time=tracker.duration * 0.4)
                self.play(FadeIn(labels[i], shift=UP * 0.2), run_time=tracker.duration * 0.3)

        # 3.13
        targets = [jar_label("0", 0), jar_label("small", 1), jar_label("max", 2, IMPURITY)]
        with self.voiceover(
            text="So whatever our measure is, it should be zero for a pure jar and largest for an even mix."
        ) as tracker:
            self.play(
                *[ReplacementTransform(a, b) for a, b in zip(labels, targets)], run_time=tracker.duration * 0.3
            )
            self.wait(tracker.duration * 0.35)
            self.play(FadeOut(jars, *targets), run_time=tracker.duration * 0.15)
        # park the probabilities bottom-left; they come back in 3.27
        fractions = VGroup(p_blue, p_yellow)
        self.play(
            fractions.animate.scale(0.75).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_corner(DL, buff=EDGE_BUFF),
            run_time=NORMAL,
        )

        # 3.14
        grid_icon = CelebrityGrid(8, 8, icon_height=0.45, spacing=0.6).scale(0.25).to_corner(UL, buff=EDGE_BUFF)
        unit = label("1 halving question = 1 bit", CAPTION_SIZE)
        unit.next_to(grid_icon, DOWN, buff=0.25, aligned_edge=LEFT)
        with self.voiceover(text="Twenty Questions gives us a unit.") as tracker:
            self.play(FadeIn(grid_icon), Write(unit), run_time=tracker.duration * 0.8)

        # 3.15: one halving, as in 2.10
        rows = range(8)
        keep = grid_icon.cells(rows, range(4))
        drop = grid_icon.cells(rows, range(4, 8))
        with self.voiceover(text="Call one perfectly halving yes-or-no question one bit.") as tracker:
            self.play(keep.animate.shift(LEFT * 0.08), drop.animate.shift(RIGHT * 0.08), run_time=tracker.duration * 0.35)
            self.play(drop.animate.set_opacity(0.15), Indicate(unit, color=HIGHLIGHT), run_time=tracker.duration * 0.45)

        # 3.16
        prob_word = label("probability").move_to([-2.2, 0.6, 0])
        bits_word = label("bits", color=HIGHLIGHT).move_to([2.2, 0.6, 0]).align_to(prob_word[2], DOWN)
        flip = CurvedArrow(
            prob_word.get_top() + UP * 0.15, bits_word.get_top() + UP * 0.15, angle=-PI / 2.5, color=TEXT_MUTED
        )
        with self.voiceover(text="Now flip it around.") as tracker:
            self.play(FadeIn(prob_word), run_time=FAST)
            self.play(Create(flip), FadeIn(bits_word), run_time=max(tracker.duration - FAST, FAST))
        self.play(FadeOut(prob_word, bits_word, flip), run_time=FAST)

        # 3.17-3.19: pies 1/2, 1/4, 1/8
        pies = VGroup()
        for k, x in zip((1, 2, 3), (-3, 0, 3)):
            disk = Circle(radius=0.75).set_stroke(TEXT_MUTED, 3).set_fill(BACKGROUND, 1)
            wedge = Sector(radius=0.75, angle=TAU / 2**k, start_angle=PI / 2).set_fill(HIGHLIGHT, 0.85).set_stroke(width=0)
            prob = MathTex(rf"p = \frac{{1}}{{{2**k}}}", font_size=MATH_SIZE).next_to(disk, UP, buff=0.3)
            bits = label(f"{k} bit" + ("s" if k > 1 else ""), BODY_SIZE, HIGHLIGHT).next_to(disk, DOWN, buff=0.3)
            pies.add(VGroup(disk, wedge, prob, bits).move_to([x, 0, 0]))
        pie_lines = [
            "If something had a one-in-two chance and you learn that it happened, "
            "you've learned as much as one halving question: one bit.",
            "A one-in-four outcome is like two halvings, so two bits.",
            "One-in-eight, three bits.",
        ]
        for pie, line in zip(pies, pie_lines):
            disk, wedge, prob, bits = pie
            with self.voiceover(text=line) as tracker:
                self.play(FadeIn(disk), FadeIn(prob), run_time=min(0.6, tracker.duration * 0.25))
                self.play(GrowFromCenter(wedge), run_time=min(0.8, tracker.duration * 0.3))
                self.play(FadeIn(bits, shift=UP * 0.2), run_time=min(0.6, tracker.duration * 0.25))
        self.wait(NORMAL)
        self.play(FadeOut(pies, grid_icon, unit), run_time=NORMAL)

        # 3.20: (1/2)^bits = p  ->  2^bits = 1/p  ->  bits = log2 1/p
        f1 = MathTex(r"\left(\frac12\right)^{\text{bits}}", "=", "p", font_size=60)
        f2 = MathTex(r"2^{\text{bits}}", "=", r"\frac{1}{p}", font_size=60)
        f3 = MathTex(r"\text{bits}", "=", r"\log_2", r"\frac{1}{p}", font_size=60)
        f3[2].set_color(HIGHLIGHT)
        for f in (f1, f2, f3):
            f.move_to(UP * 1.0)
        with self.voiceover(text="So the number of bits is log base two of one over the probability.") as tracker:
            self.play(Write(f1), run_time=tracker.duration * 0.3)
            self.play(TransformMatchingTex(f1, f2), run_time=tracker.duration * 0.3)
            self.play(TransformMatchingTex(f2, f3), run_time=tracker.duration * 0.3)

        # 3.21
        halvings = VGroup()
        for _ in range(3):
            arrow = Arrow(LEFT * 0.4, RIGHT * 0.4, buff=0, color=HIGHLIGHT, stroke_width=4)
            div = MathTex(r"\div 2", font_size=BODY_SIZE, color=HIGHLIGHT).next_to(arrow, UP, buff=0.08)
            halvings.add(VGroup(arrow, div))
        halvings.arrange(RIGHT, buff=0.15).next_to(f3, DOWN, buff=0.35).set_x(f3[2].get_x())
        with self.voiceover(text="Log base two simply counts how many halvings it takes to get there.") as tracker:
            self.play(
                LaggedStart(
                    *[LaggedStart(GrowArrow(a), FadeIn(d), lag_ratio=0.3) for a, d in halvings], lag_ratio=0.5
                ),
                run_time=tracker.duration * 0.6,
            )
            self.wait(tracker.duration * 0.2)
            self.play(FadeOut(halvings), run_time=FAST)

        # 3.22: rare -> many bits, common -> few (the 1/8 and 1/2 pies)
        bar_unit = 0.9
        bar_rows = VGroup()
        for word, k, verdict in (("rare", 3, "many bits"), ("common", 1, "few bits")):
            name = label(word, CAPTION_SIZE, TEXT_MUTED)
            bar = Rectangle(width=bar_unit * k, height=0.3).set_fill(HIGHLIGHT, 0.85).set_stroke(width=0)
            tail = label(verdict, CAPTION_SIZE)
            bar_rows.add(VGroup(name, bar, tail))
        for name, bar, tail in bar_rows:
            name.move_to(LEFT * 1.6, aligned_edge=RIGHT)
            bar.next_to(LEFT * 1.4, RIGHT, buff=0)
            tail.next_to(bar, RIGHT, buff=0.25)
        bar_rows[1].shift(DOWN * 0.6)
        bar_rows.move_to(DOWN * 1.6)
        with self.voiceover(text="Rare outcomes carry lots of bits, and common ones carry very few.") as tracker:
            for name, bar, tail in bar_rows:
                self.play(
                    FadeIn(name), GrowFromEdge(bar, LEFT), FadeIn(tail, shift=LEFT * 0.2),
                    run_time=tracker.duration * 0.35,
                )
        self.play(FadeOut(bar_rows), run_time=FAST)

        # 3.23: tags above one blue and one yellow ball
        blue_i = balls.indices("blue")[0]
        yellow_i = min(balls.indices("yellow"), key=lambda i: abs(i - 0.7 * (n - 1)))
        tags, tag_lines = VGroup(), VGroup()
        for color, idx, count in (("blue", blue_i, n_blue), ("yellow", yellow_i, n_yellow)):
            tag = MathTex(
                rf"\log_2\frac{{{n}}}{{{count}}}", r"\approx", f"{surprisal[color]:.2f}",
                font_size=TAG_SIZE, color=CLASS_COLOR[color],
            )
            tags.add(tag)
        with self.voiceover(
            text="Blue is the rarer color here, so drawing a blue ball tells you a bit more: "
            "about 1.15 bits, versus 0.86 for yellow."
        ) as tracker:
            self.play(FadeOut(f3), balls.animate.restore(), run_time=tracker.duration * 0.25)
            for tag, idx, color in zip(tags, (blue_i, yellow_i), ("blue", "yellow")):
                dot = balls.dots[idx]
                tag.next_to(dot, UP, buff=0.75)
                link = Line(dot.get_top() + UP * 0.05, tag.get_bottom() + DOWN * 0.08, color=CLASS_COLOR[color], stroke_width=2)
                tag_lines.add(link)
                self.play(Create(link), Write(tag), run_time=tracker.duration * 0.3)

        # 3.24: the weighted average
        weighted = MathTex(
            rf"\frac{{{n_blue}}}{{{n}}}", r"\cdot", f"{surprisal['blue']:.2f}", "+",
            rf"\frac{{{n_yellow}}}{{{n}}}", r"\cdot", f"{surprisal['yellow']:.2f}",
            font_size=MATH_SIZE,
        )
        weighted[0].set_color(CLASS_0)
        weighted[4].set_color(CLASS_1)
        weighted.move_to(ORIGIN)
        with self.voiceover(
            text="Now average those over the outcomes, weighting each by how often it happens."
        ) as tracker:
            self.play(TransformFromCopy(tags[0][2], weighted[2]), TransformFromCopy(tags[1][2], weighted[6]),
                      run_time=tracker.duration * 0.4)
            self.play(FadeIn(weighted[0], weighted[1], weighted[3], weighted[4], weighted[5]),
                      run_time=tracker.duration * 0.4)

        # 3.25
        general = MathTex(r"\sum_i", "p_i", r"\log_2", r"\frac{1}{p_i}", font_size=MATH_SIZE).move_to(ORIGIN)
        name = label("entropy", BODY_SIZE, IMPURITY)
        name.next_to(general, RIGHT, buff=0.6)
        with self.voiceover(text="That average has a name: entropy.") as tracker:
            self.play(TransformMatchingTex(weighted, general), run_time=tracker.duration * 0.5)
            self.play(Write(name), run_time=tracker.duration * 0.4)

        # 3.26: the minus sign travels from inside the log to the front
        middle = MathTex(r"\sum_i", "p_i", "(", "-", r"\log_2", "p_i", ")", font_size=MATH_SIZE).move_to(ORIGIN)
        final = MathTex("S", "=", "-", r"\sum_i", "p_i", r"\log_2", "p_i", font_size=MATH_SIZE).move_to(ORIGIN)
        with self.voiceover(
            text="In textbooks you'll see it with a minus sign out front, "
            "because log of one over p is the same as minus log p."
        ) as tracker:
            self.play(FadeOut(tags, tag_lines), run_time=FAST)
            self.play(
                ReplacementTransform(general[0], middle[0]),
                ReplacementTransform(general[1], middle[1]),
                ReplacementTransform(general[2], middle[4]),
                ReplacementTransform(general[3], VGroup(middle[3], middle[5])),
                FadeIn(middle[2], middle[6]),
                name.animate.next_to(middle, RIGHT, buff=0.6),
                run_time=tracker.duration * 0.4,
            )
            self.play(
                *[ReplacementTransform(middle[a], final[b]) for a, b in ((0, 3), (1, 4), (3, 2), (4, 5), (5, 6))],
                FadeOut(middle[2], middle[6]),
                FadeIn(final[0], final[1]),
                name.animate.next_to(final, RIGHT, buff=0.6),
                run_time=tracker.duration * 0.4,
            )

        # 3.27: plug in our twenty balls
        fb = rf"\frac{{{n_blue}}}{{{n}}}"
        fy = rf"\frac{{{n_yellow}}}{{{n}}}"
        plugged = MathTex(
            "S_0", "=", "-", fb, r"\log_2", fb, "-", fy, r"\log_2", fy, r"\approx", f"{s0:.2f}",
            font_size=MATH_SIZE,
        )
        for i in (3, 5):
            plugged[i].set_color(CLASS_0)
        for i in (7, 9):
            plugged[i].set_color(CLASS_1)
        plugged.next_to(final, DOWN, buff=0.8)
        with self.voiceover(
            text="For our twenty balls, that comes out to about 0.99 bits, almost exactly one."
        ) as tracker:
            self.play(
                TransformFromCopy(p_blue[2], plugged[3]),
                TransformFromCopy(p_blue[2], plugged[5]),
                TransformFromCopy(p_yellow[2], plugged[7]),
                TransformFromCopy(p_yellow[2], plugged[9]),
                run_time=tracker.duration * 0.35,
            )
            self.play(Write(VGroup(*[plugged[i] for i in (0, 1, 2, 4, 6, 8)])), run_time=tracker.duration * 0.3)
            self.play(Write(plugged[10:]), run_time=tracker.duration * 0.25)

        # 3.28
        with self.voiceover(text="So it really is nearly a perfect coin flip.") as tracker:
            self.play(Circumscribe(plugged[10:], color=HIGHLIGHT), run_time=min(1.5, tracker.duration))
        self.wait(SLOW)

        # 3.29: keep S0 top-right, trace the arch while a jar refills
        s0_park = MathTex("S_0", r"\approx", f"{s0:.2f}", font_size=TAG_SIZE).move_to([3.4, 3.2, 0])
        curve = EntropyCurve().move_to(DOWN * 0.8)
        jar = Jar(n, 0).scale(0.8).move_to([5.3, 1.2, 0])
        jar.add_updater(lambda j: j.set_p(curve.p.get_value()))
        self.play(
            FadeOut(final, name, fractions, balls, *[plugged[i] for i in range(1, 10)]),
            ReplacementTransform(VGroup(plugged[0], plugged[10], plugged[11]), s0_park),
            run_time=NORMAL,
        )
        with self.voiceover(
            text="And if we slide that proportion from all blue to all yellow, entropy traces out this arch."
        ) as tracker:
            setup = min(1.5, tracker.duration * 0.3)
            self.play(Create(curve.axes), FadeIn(curve.labels), FadeIn(jar), run_time=setup)
            self.add(curve.dot)
            self.play(
                Create(curve.curve, rate_func=linear),
                curve.p.animate(rate_func=linear).set_value(1),
                run_time=max(tracker.duration - setup, 4),
            )

        # 3.30
        peak = DashedLine(curve.axes.c2p(0, 1), curve.axes.c2p(1, 1), color=TEXT_MUTED, dash_length=0.1)
        peak_label = label("1 bit", CAPTION_SIZE, TEXT_MUTED).next_to(peak, RIGHT, buff=0.15)
        with self.voiceover(
            text="It's zero at both ends, where the jar is pure, and peaks at exactly one bit at fifty-fifty."
        ) as tracker:
            leg = tracker.duration * 0.22
            self.play(curve.p.animate.set_value(0), run_time=leg)
            self.play(Flash(curve.point(0), color=HIGHLIGHT), run_time=FAST)
            self.play(curve.p.animate.set_value(1), run_time=leg)
            self.play(Flash(curve.point(1), color=HIGHLIGHT), run_time=FAST)
            self.play(curve.p.animate.set_value(0.5), run_time=leg * 0.6)
            self.play(Create(peak), FadeIn(peak_label), Flash(curve.point(0.5), color=HIGHLIGHT), run_time=NORMAL)

        # hold: mark our balls, then shrink the curve to the corner for scene 4
        p_ours = n_yellow / n
        self.play(curve.p.animate.set_value(p_ours), run_time=NORMAL)
        mark = VGroup(
            Dot(curve.point(p_ours, s0), radius=0.09, color=TEXT),
            label("our balls", CAPTION_SIZE).next_to(curve.point(p_ours, s0), UP + RIGHT, buff=0.2),
        )
        self.play(FadeIn(mark[1], shift=DOWN * 0.1), run_time=FAST)
        self.add(mark[0])
        self.wait(SLOW)
        curve.dot.clear_updaters()
        jar.clear_updaters()
        mini = VGroup(curve, peak, mark)
        self.play(FadeOut(jar, peak_label), run_time=FAST)
        self.play(mini.animate.scale(0.45).move_to([5, -2.4, 0]), run_time=SLOW)
        # end state for scene 4: balls at y = 1.8, mini curve bottom-right, S0 and goal tree top-right
        self.play(FadeIn(BallRow(colors)), run_time=NORMAL)
        self.wait(NORMAL)
