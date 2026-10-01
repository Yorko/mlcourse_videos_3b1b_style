"""Scene 8: overfitting (docs/STORYBOARD.md, rows 8.1-8.17).

Every partition, sliver, accuracy and tree comes from ``data/toy2d.json``,
``data/depth_cv.json``, ``data/balls.json`` and ``data/overfitting.json``.
The ball row and ball tree reuse scene 5's ``BallRow`` / ``BallTree`` so 8.5
looks like 5.14.
"""

import json
from pathlib import Path

import numpy as np
from manim import (
    DEGREES,
    ITALIC,
    ORIGIN,
    UL,
    UR,
    AnimationGroup,
    Axes,
    Circle,
    Circumscribe,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    FadeTransform,
    Flash,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MovingCameraScene,
    NumberLine,
    Polygon,
    Rectangle,
    Restore,
    RoundedRectangle,
    Succession,
    Text,
    Triangle,
    VGroup,
    VMobject,
    Write,
)
from manim_voiceover import VoiceoverScene

from components.tree_diagram import TreeDiagram
from scenes.s05_growing_tree import ROW_PANEL, TREE_LEVEL_GAP, TREE_ROOT, BallRow, BallTree
from style import *
from voice import speech_service

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TOY = json.loads((DATA_DIR / "toy2d.json").read_text())
CV = json.loads((DATA_DIR / "depth_cv.json").read_text())
BALLS = json.loads((DATA_DIR / "balls.json").read_text())
OVER = json.loads((DATA_DIR / "overfitting.json").read_text())

TREES = {t["max_depth"]: t for t in TOY["trees"]}  # None = unlimited
MIN_LEAF = {t["min_samples_leaf"]: t for t in OVER["min_leaf"]}
BALL_COLOR = {"blue": CLASS_0, "yellow": CLASS_1}
POINT_COLOR = {0: CLASS_0, 1: CLASS_1}

PLANE_CENTER = np.array([-3.45, -0.1, 0.0])
PLANE_HEIGHT = 6.4
PLANE_THUMB_HEIGHT = 2.0
INF = 11  # the "∞" stop sits one tick past 10 on the depth slider


def label(text, size=CAPTION_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def pct(x: float) -> str:
    return f"{x * 100:g}%"


# --- 2D plane --------------------------------------------------------------------


class Plane(VGroup):
    """The 200 toy points over a box of leaf rectangles. Data coords -> scene via ``c2p``."""

    def __init__(self, height=PLANE_HEIGHT, center=PLANE_CENTER, **kwargs):
        super().__init__(**kwargs)
        (self.x0, self.x1), (self.y0, self.y1) = TOY["bounds"]
        self.k = height / (self.y1 - self.y0)
        self.origin = np.array(center)
        self.frame = Rectangle(width=(self.x1 - self.x0) * self.k, height=height)
        self.frame.set_stroke(GRID, 2).move_to(center)
        self.points_group = VGroup(
            *[
                Dot(self.c2p(*p["x"]), radius=0.05, color=POINT_COLOR[p["label"]]).set_stroke(BACKGROUND, 0.8)
                for p in TOY["points"]
            ]
        )
        self.points_group.set_z_index(3)
        self.frame.set_z_index(2)
        self.regions = self.make_regions(TREES[3]["leaves"])
        self.add(self.regions, self.frame, self.points_group)

    def c2p(self, x, y):
        cx, cy = (self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2
        return self.origin + np.array([(x - cx) * self.k, (y - cy) * self.k, 0.0])

    def box(self, box, **style):
        (x0, x1), (y0, y1) = box
        r = Rectangle(width=max((x1 - x0) * self.k, 1e-3), height=max((y1 - y0) * self.k, 1e-3))
        return r.move_to(self.c2p((x0 + x1) / 2, (y0 + y1) / 2)).set_style(**style)

    def make_regions(self, leaves) -> VGroup:
        rects = VGroup()
        for lf in leaves:
            c = POINT_COLOR[lf["prediction"]]
            rects.add(self.box(lf["box"], fill_color=c, fill_opacity=0.28, stroke_color=c, stroke_width=1, stroke_opacity=0.7))
        return rects

    def fitted_regions(self, leaves) -> VGroup:
        """Leaf rectangles for ``leaves``, following the plane if it has been moved or scaled."""
        new = self.make_regions(leaves)
        new.scale(self.frame.height / PLANE_HEIGHT, about_point=self.origin)
        return new.shift(self.frame.get_center() - self.origin)

    def set_regions(self, new):
        self.remove(self.regions)
        self.regions = new
        self.submobjects.insert(0, new)

    def readout(self, text):
        """A caption centred above the plane (leaf count, train accuracy)."""
        return label(text, CAPTION_SIZE * 0.85, TEXT_MUTED).next_to(self.frame, UP, buff=0.1)

    def point(self, i):
        return self.points_group[i]


# --- Slider ----------------------------------------------------------------------


class Slider(VGroup):
    """A NumberLine with a downward Triangle knob and a name."""

    def __init__(self, name, x_min, x_max, ticks: dict, value, length=4.6, **kwargs):
        super().__init__(**kwargs)
        self.line = NumberLine(
            x_range=[x_min, x_max, 1], length=length, include_tip=False, include_numbers=False,
            tick_size=0.06, stroke_width=3, color=HIGHLIGHT,
        )
        self.tick_labels = VGroup(
            *[label(t, CAPTION_SIZE * 0.75, TEXT_MUTED).next_to(self.line.n2p(v), DOWN, buff=0.15) for v, t in ticks.items()]
        )
        self.knob = Triangle(color=HIGHLIGHT, fill_color=HIGHLIGHT, fill_opacity=1).rotate(np.pi)
        self.knob.scale_to_fit_width(0.24)
        self.knob.next_to(self.line.n2p(value), UP, buff=0.04)
        self.name = label(name, CAPTION_SIZE, TEXT).next_to(self.line, UP, buff=0.35).align_to(self.line, LEFT)
        self.add(self.line, self.tick_labels, self.knob, self.name)

    def knob_to(self, value):
        target = self.knob.copy().next_to(self.line.n2p(value), UP, buff=0.04)
        return self.knob.animate.move_to(target)



# --- Icons -----------------------------------------------------------------------


def trousers(height=0.8, color=GAIN):
    w, h = 0.6, 1.0
    pts = [(-w / 2, h / 2), (w / 2, h / 2), (w / 2 + 0.03, -h / 2), (0.06, -h / 2), (0, h / 6),
           (-0.06, -h / 2), (-w / 2 - 0.03, -h / 2)]
    p = Polygon(*[np.array([x, y, 0]) for x, y in pts], color=color, fill_color=color, fill_opacity=0.9, stroke_width=2)
    belt = Line([-w / 2, h / 2 - 0.12, 0], [w / 2, h / 2 - 0.12, 0], color=BACKGROUND, stroke_width=3)
    return VGroup(p, belt).scale_to_fit_height(height)


def cross(size=0.35):
    return MathTex(r"\times", color=IMPURITY).scale_to_fit_height(size)


def check(size=0.35):
    return MathTex(r"\checkmark", color=GAIN).scale_to_fit_height(size)


# --- Ball trees ------------------------------------------------------------------


def ball_spec(nodes) -> dict:
    by_id = {n["id"]: n for n in nodes}

    def walk(i):
        n = by_id[i]
        if n["leaf"]:
            return {"id": f"n{i}", "leaf": n["prediction"]}
        return {"id": f"n{i}", "q": n["question"].replace("<=", "≤"), "no": walk(n["left"]), "yes": walk(n["right"])}

    return walk(0)


def ball_path(nodes, x) -> list[str]:
    by_id = {n["id"]: n for n in nodes}
    n, path = by_id[0], ["n0"]
    while not n["leaf"]:
        n = by_id[n["left"] if x <= n["threshold"] else n["right"]]
        path.append(f"n{n['id']}")
    return path


def place_tree(tree):
    right_edge = config_right()
    tree.move_root_to(TREE_ROOT)
    if tree.get_right()[0] > right_edge or tree.get_left()[0] < 0.3:
        tree.scale_to_fit_width(min(tree.width, right_edge - 0.3))
        tree.move_root_to(TREE_ROOT)
    tree.shift(RIGHT * max(0.0, 0.3 - tree.get_left()[0]))
    tree.shift(LEFT * max(0.0, tree.get_right()[0] - right_edge))
    return tree


def config_right() -> float:
    from manim import config

    return config.frame_width / 2 - EDGE_BUFF


def toy_spec(nodes) -> dict:
    by_id = {n["id"]: n for n in nodes}

    def walk(i):
        n = by_id[i]
        if n["leaf"]:
            return {"id": str(i), "leaf": str(n["prediction"])}
        return {"id": str(i), "q": "", "no": walk(n["left"]), "yes": walk(n["right"])}

    return walk(0)


# --- Scene -----------------------------------------------------------------------


class Overfitting(VoiceoverScene, MovingCameraScene):
    def swap_regions(self, plane, leaves, *anims, run_time=0.6):
        """Cross-fade the plane's leaf rectangles (leaf counts differ, so no Transform)."""
        old, new = plane.regions, plane.fitted_regions(leaves)
        plane.remove(old)
        self.add(old)
        self.play(FadeOut(old), FadeIn(new), *anims, run_time=run_time)
        self.remove(new)
        plane.set_regions(new)

    def construct(self):
        self.set_speech_service(speech_service())
        frame = self.camera.frame

        plane = Plane()
        depth_ticks = {1: "1", 3: "3", 6: "6", 10: "10", INF: "∞"}
        slider = Slider("max depth", 1, INF, depth_ticks, 3).move_to([3.5, 2.5, 0])
        def readout_for(tree):
            return plane.readout(f"{tree['n_leaves']} leaves · train accuracy {pct(tree['train_accuracy'])}")

        readout = readout_for(TREES[3])

        # 8.1
        with self.voiceover(
            text="If deeper trees fit the data better, why not keep splitting until every leaf is pure?"
        ) as tracker:
            self.play(FadeIn(plane), run_time=NORMAL)
            self.play(Create(slider.line), FadeIn(slider.tick_labels), Write(slider.name), run_time=NORMAL)
            self.play(FadeIn(slider.knob, shift=DOWN * 0.2), FadeIn(readout), run_time=FAST)

        # 8.2: 3 -> 6 -> 10 -> unlimited
        stops = OVER["depth_stops"][1:]
        with self.voiceover(text="Watch what happens.") as tracker:
            step = max(0.6, (tracker.duration + 1.0) / len(stops))
            for d in stops:
                new_readout = readout_for(TREES[d])
                self.swap_regions(
                    plane, TREES[d]["leaves"],
                    slider.knob_to(INF if d is None else d), FadeTransform(readout, new_readout),
                    run_time=step,
                )
                readout = new_readout

        # 8.3: the slivers around stray points, then zoom in on the smallest one
        slivers = OVER["slivers"][:3]
        outlines = VGroup(*[plane.box(s["box"], stroke_color=IMPURITY, stroke_width=3, fill_opacity=0) for s in slivers])
        outlines.set_z_index(4)
        rings = [Circle(radius=0.14).move_to(plane.point(s["points"][0])) for s in slivers]
        target = plane.point(slivers[0]["points"][0]).get_center()
        frame.save_state()
        with self.voiceover(
            text="The boundary turns jagged, carving out tiny boxes around single points "
            "that are almost certainly just noise."
        ) as tracker:
            self.play(Create(outlines), run_time=NORMAL)
            self.play(
                LaggedStart(
                    *[Circumscribe(r, shape=Circle, color=IMPURITY, fade_out=True, stroke_width=3) for r in rings],
                    lag_ratio=0.5,
                ),
                run_time=SLOW,
            )
            self.play(frame.animate.scale(0.25).move_to(target), run_time=max(1.0, tracker.duration - 3.2))
        self.wait(NORMAL)  # hold on the zoomed sliver

        # 8.4: zoom back out; the green-trousers rule
        icons = VGroup(*[trousers() for _ in range(4)]).arrange(RIGHT, buff=0.5).move_to([3.5, -0.8, 0])
        defaulted = VGroup(*[Dot(radius=0.09, color=CLASS_1).next_to(t, UP, buff=0.15) for t in icons])
        card_text = label("green trousers  →  default", CAPTION_SIZE, TEXT)
        card = VGroup(
            RoundedRectangle(width=card_text.width + 0.5, height=card_text.height + 0.4, corner_radius=0.12)
            .set_stroke(IMPURITY, 3)
            .set_fill(BACKGROUND, 1),
            card_text,
        ).move_to([3.5, -2.4, 0])
        vignette = VGroup(icons, defaulted, card)
        with self.voiceover(
            text="It's like a bank noticing that the four clients who came in wearing green trousers all defaulted, "
            "and making that a rule."
        ) as tracker:
            self.play(Restore(frame), run_time=NORMAL)
            self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in icons], lag_ratio=0.25), run_time=NORMAL)
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in defaulted], lag_ratio=0.2), run_time=FAST)
            self.play(FadeIn(card, shift=UP * 0.2), run_time=NORMAL)
        self.wait(FAST)
        self.play(FadeOut(vignette, outlines), run_time=FAST)

        # 8.5: scene 5's perfect tree comes back; the plane shrinks into the corner
        balls = BallRow(BALLS["colors"])
        full_nodes = BALLS["tree"]["nodes"]
        cuts = [n["t"] for n in full_nodes if not n["leaf"]]
        row = dict(ROW_PANEL, center=np.array([-3.25, 0.2, 0.0]))
        balls.place(cuts, **row)
        cut_lines = VGroup(*balls.cut_lines.values())
        tree = place_tree(BallTree(ball_spec(full_nodes), level_gap=TREE_LEVEL_GAP, font_size=CAPTION_SIZE - 2, h_gap=0.25))
        perfect = label("perfect", BODY_SIZE, GAIN, slant=ITALIC).next_to(tree.node("n0"), RIGHT, buff=0.6)
        with self.voiceover(text="Remember our perfect tree?") as tracker:
            self.play(
                plane.animate.scale(PLANE_THUMB_HEIGHT / PLANE_HEIGHT).to_corner(UL, buff=EDGE_BUFF),
                FadeOut(slider, readout),
                run_time=NORMAL,
            )
            self.play(FadeIn(balls, cut_lines, tree, perfect), run_time=NORMAL)

        # 8.6
        with self.voiceover(text="That's exactly the problem.") as tracker:
            self.play(Indicate(perfect, color=GAIN, scale_factor=1.3), run_time=min(1.2, tracker.duration))

        # 8.7: the 21st ball lands in the one-ball leaf "x > 18" and gets the wrong color
        nb = OVER["new_ball"]
        xs, _ = balls.positions(cuts, **row)
        k = int(np.floor(nb["x"]))
        new_x = xs[k] + (nb["x"] - k) * (xs[k + 1] - xs[k])
        r = row["radius"]
        new_ball = Dot(radius=r, color=BALL_COLOR[nb["true_color"]]).set_stroke(TEXT, 2)
        new_ball.move_to([new_x, row["center"][1] + 0.55, 0]).set_z_index(5)
        drop = DashedLine(new_ball.get_bottom(), [new_x, row["center"][1] - 0.05, 0], color=TEXT_MUTED,
                          stroke_width=2, dash_length=0.04)
        new_label = label(f"{nb['x']:g}", CAPTION_SIZE * 0.6, TEXT).next_to(new_ball, UP, buff=0.1)
        path = ball_path(full_nodes, nb["x"])
        assert path[-1] == f"n{nb['full_leaf']}"
        traveller = new_ball.copy()

        def walk(t, tr, path_ids, time):
            anims = []
            for prev, cur in zip(path_ids, path_ids[1:]):
                anims.append(AnimationGroup(*tr.light_edge(cur), t.animate.next_to(tr.node(cur), RIGHT, buff=0.08)))
            return Succession(t.animate.next_to(tr.node(path_ids[0]), RIGHT, buff=0.12), *anims, run_time=time)

        leaf = tree.node(path[-1])
        miss = cross().next_to(leaf, DOWN, buff=0.12)
        # "perfect" cracks: a zig-zag between "per" and "fect", then the halves tilt apart
        left_half, right_half = perfect[:3], perfect[3:]
        seam = (left_half.get_right()[0] + right_half.get_left()[0]) / 2
        top, bottom = perfect.get_top()[1] + 0.12, perfect.get_bottom()[1] - 0.12
        zig = VMobject(color=IMPURITY, stroke_width=3).set_points_as_corners(
            [[seam + (0.06 if i % 2 else -0.06), top + (bottom - top) * i / 6, 0] for i in range(7)]
        )
        with self.voiceover(
            text="It fits every training ball, and that's precisely why it can stumble on the twenty-first."
        ) as tracker:
            self.play(FadeIn(new_ball, shift=DOWN * 0.4), FadeIn(new_label), Create(drop), run_time=NORMAL)
            self.add(traveller)
            self.play(walk(traveller, tree, path, 2.2))
            self.play(FadeIn(miss, scale=1.5), Indicate(leaf, color=IMPURITY), run_time=FAST)
            self.play(Create(zig), run_time=0.4)
            self.play(
                left_half.animate.rotate(8 * DEGREES).shift(LEFT * 0.08).set_color(IMPURITY),
                right_half.animate.rotate(-8 * DEGREES).shift(RIGHT * 0.08).set_color(IMPURITY),
                FadeOut(zig),
                run_time=0.6,
            )

        # 8.8: prune the single-ball leaves; two training balls are now wrong, the new one right
        pruned = OVER["pruned_ball_tree"]
        pruned_tree = BallTree(ball_spec(pruned["nodes"]), level_gap=TREE_LEVEL_GAP, font_size=CAPTION_SIZE - 2, h_gap=0.25)
        pruned_tree.move_root_to(tree.node("n0").get_center())
        pruned_cuts = [n["t"] for n in pruned["nodes"] if not n["leaf"]]
        gone_cuts = VGroup(*[balls.cut_lines[t] for t in cuts if t not in pruned_cuts])
        pruned_path = ball_path(pruned["nodes"], nb["x"])
        assert pruned_path[-1] == f"n{nb['pruned_leaf']}"
        with self.voiceover(
            text="A simpler tree that gets a couple of training balls wrong could easily do better on new ones."
        ) as tracker:
            self.play(FadeOut(traveller, miss), FadeTransform(tree, pruned_tree), FadeOut(gone_cuts),
                      *balls.layout_anims(pruned_cuts, **row), run_time=NORMAL)
            xs2, _ = balls.positions(pruned_cuts, **row)
            new_x2 = xs2[k] + (nb["x"] - k) * (xs2[k + 1] - xs2[k])
            self.play(VGroup(new_ball, drop, new_label).animate.shift(RIGHT * (new_x2 - new_x)), run_time=FAST)
            wrong_marks = VGroup(*[cross(0.22).next_to(balls.labels[i], DOWN, buff=0.1) for i in pruned["wrong"]])
            self.play(LaggedStart(*[FadeIn(m, scale=1.5) for m in wrong_marks], lag_ratio=0.3), run_time=FAST * 2)
            traveller = new_ball.copy()
            self.add(traveller)
            self.play(walk(traveller, pruned_tree, pruned_path, 1.5))
            hit = check().next_to(pruned_tree.node(pruned_path[-1]), DOWN, buff=0.12)
            self.play(FadeIn(hit, scale=1.5), run_time=FAST)
        self.wait(NORMAL)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=NORMAL)

        # 8.9: accuracy vs depth
        rows = CV["rows"]
        depths = [row_["max_depth"] for row_ in rows]
        axes = Axes(
            x_range=[1, depths[-1], 1], y_range=[0.75, 1.0, 0.05], x_length=9, y_length=4.5,
            axis_config={"color": GRID, "include_tip": False, "stroke_width": 2},
        ).move_to(ORIGIN + UP * 0.2)
        x_nums = VGroup(*[label(str(d), CAPTION_SIZE * 0.7, TEXT_MUTED).next_to(axes.c2p(d, 0.75), DOWN, buff=0.15)
                          for d in depths])
        y_nums = VGroup(*[label(pct(v), CAPTION_SIZE * 0.7, TEXT_MUTED).next_to(axes.c2p(1, v), LEFT, buff=0.15)
                          for v in np.round(np.arange(0.75, 1.0001, 0.05), 2)])
        x_title = label("max depth", CAPTION_SIZE, TEXT_MUTED).next_to(x_nums, DOWN, buff=0.15)
        y_title = label("accuracy", CAPTION_SIZE, TEXT_MUTED).next_to(axes.y_axis, UP, buff=0.2)
        train_pts = [axes.c2p(row_["max_depth"], row_["train_mean"]) for row_ in rows]
        cv_pts = [axes.c2p(row_["max_depth"], row_["test_mean"]) for row_ in rows]
        train_line = VMobject(color=CLASS_0, stroke_width=4).set_points_as_corners(train_pts)
        cv_line = VMobject(color=TEXT, stroke_width=4).set_points_as_corners(cv_pts)
        train_lab = label("train", CAPTION_SIZE, CLASS_0).next_to(train_pts[-1], UP, buff=0.15)
        cv_lab = label("unseen data", CAPTION_SIZE, TEXT).next_to(cv_pts[-1], DOWN, buff=0.15).align_to(train_lab, RIGHT)
        chart = VGroup(axes, x_nums, y_nums, x_title, y_title)
        with self.voiceover(text="On the training data, accuracy marches up to a hundred percent.") as tracker:
            self.play(Create(axes), FadeIn(x_nums, y_nums, x_title, y_title), run_time=NORMAL)
            self.play(Create(train_line), run_time=max(1.0, tracker.duration - 1.6))
            self.play(FadeIn(train_lab), run_time=FAST)

        # 8.10: held-out accuracy peaks at the real best depth (depth_cv.json), not at 2
        best = next(row_ for row_ in rows if row_["max_depth"] == CV["best_depth"])
        peak = Dot(axes.c2p(best["max_depth"], best["test_mean"]), radius=0.08, color=HIGHLIGHT).set_z_index(4)
        peak_lab = label(f"peak: depth {best['max_depth']}, {pct(best['test_mean'])}", CAPTION_SIZE * 0.85, HIGHLIGHT)
        peak_lab.move_to(axes.c2p(best["max_depth"], 0.82))
        peak_tick = DashedLine(peak.get_bottom(), peak_lab.get_top() + UP * 0.05, color=HIGHLIGHT, stroke_width=2,
                               dash_length=0.05)
        gap = Polygon(*train_pts, *cv_pts[::-1], stroke_width=0, fill_color=IMPURITY, fill_opacity=0.25)
        gap_lab = label("gap", CAPTION_SIZE, IMPURITY).move_to(
            (axes.c2p(depths[-3], rows[-3]["train_mean"]) + axes.c2p(depths[-3], rows[-3]["test_mean"])) / 2
        )
        # The spoken depth comes from the same data as the peak dot, so they can't
        # disagree. "about": the neighbors are within a fraction of a percent.
        best_word = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"][
            best["max_depth"]
        ]
        with self.voiceover(
            text=f"On data the tree has never seen, it peaks at about {best_word} questions deep, "
            "then slowly gets worse."
        ) as tracker:
            self.play(Create(cv_line), run_time=max(1.0, tracker.duration * 0.5))
            self.play(FadeIn(cv_lab), FadeIn(peak, scale=0.5), Flash(peak, color=HIGHLIGHT), FadeIn(peak_lab), Create(peak_tick), run_time=NORMAL)
            self.bring_to_back(gap)
            self.play(FadeIn(gap), FadeIn(gap_lab), run_time=NORMAL)
        chart.add(train_line, cv_line, train_lab, cv_lab, peak, peak_lab, peak_tick, gap, gap_lab)

        # 8.11
        motto = label("memorized ≠ learned", BODY_SIZE, TEXT).move_to(CAPTION_POSITION)
        with self.voiceover(text="The tree has memorized instead of learned.") as tracker:
            self.play(Write(motto), run_time=min(1.5, tracker.duration))
        self.wait(NORMAL)

        # 8.12: the chart parks top-right, the max-depth plane comes back on the left
        plane = Plane()
        plane.set_regions(plane.fitted_regions(TREES[None]["leaves"]))
        with self.voiceover(text="So how do you stop it?") as tracker:
            self.play(
                FadeOut(motto),
                chart.animate.scale(0.35).to_corner(UR, buff=EDGE_BUFF),
                FadeIn(plane, shift=RIGHT * 0.5),
                run_time=min(1.5, tracker.duration),
            )

        # 8.13: two sliders; each knob swaps in the precomputed partition
        depth_slider = Slider("max depth", 1, INF, depth_ticks, INF).move_to([3.5, 0.75, 0])
        leaf_ticks = {t["min_samples_leaf"]: str(t["min_samples_leaf"]) for t in OVER["min_leaf"]}
        stops_ml = sorted(leaf_ticks)
        leaf_slider = Slider("min points per leaf", stops_ml[0], stops_ml[-1], leaf_ticks, stops_ml[0]).move_to([3.5, -0.85, 0])
        n_leaves = TREES[None]["n_leaves"]
        readout = plane.readout(f"{n_leaves} leaves")

        def leaves_to(tree, *anims, run_time):
            nonlocal readout
            new = plane.readout(f"{tree['n_leaves']} leaves")
            self.swap_regions(plane, tree["leaves"], FadeTransform(readout, new), *anims, run_time=run_time)
            readout = new

        best_d = CV["best_depth"]
        with self.voiceover(
            text="The simplest way is to stop growing early: cap the depth, or demand a minimum number of points "
            "in every leaf."
        ) as tracker:
            self.play(FadeIn(depth_slider, leaf_slider, readout), run_time=NORMAL)
            n_steps = 2 + len(stops_ml) - 1
            step = max(0.6, (tracker.duration - NORMAL) / n_steps)
            leaves_to(TREES[best_d], depth_slider.knob_to(best_d), run_time=step)
            leaves_to(TREES[None], depth_slider.knob_to(INF), run_time=step)
            for k_ in stops_ml[1:]:
                leaves_to(MIN_LEAF[k_], leaf_slider.knob_to(k_), run_time=step)

        # 8.14: grow the full tree, then snip the subtrees cost-complexity pruning removes
        ccp = OVER["ccp"]
        icon = TreeDiagram(
            toy_spec(ccp["full_nodes"]), labels=False, h_spacing=0.19, level_gap=0.15, dot_radius=0.04,
            edge_width=1.5, leaf_colors={"0": CLASS_0, "1": CLASS_1},
        )
        icon.move_to([3.5, -2.3, 0])
        kept = set(map(str, ccp["kept"]))
        cut_roots = [str(i) for i in ccp["removed"]]
        snips = []
        for root_id in cut_roots:
            below = [i for i in icon.nodes if i != root_id and root_id in icon.path_ids(i)]
            snips.append(VGroup(*[icon.nodes[i] for i in below], *[icon.edges[i] for i in below]))
        assert all(i in kept for i in cut_roots)
        with self.voiceover(
            text="Or grow the full tree and then prune back the branches that don't earn their keep."
        ) as tracker:
            self.play(icon.create_animation(lag_ratio=0.2), run_time=max(1.0, tracker.duration * 0.4))
            per = max(0.4, tracker.duration * 0.5 / len(snips))
            for root_id, s in zip(cut_roots, snips):
                self.play(
                    Flash(icon.nodes[root_id], color=IMPURITY, flash_radius=0.15, line_length=0.1),
                    FadeOut(s, shift=DOWN * 0.2),
                    icon.nodes[root_id].animate.set_color(
                        {0: CLASS_0, 1: CLASS_1}[ccp["full_nodes"][int(root_id)]["prediction"]]),
                    run_time=per,
                )
        self.play(FadeOut(icon), run_time=FAST)

        # 8.15
        with self.voiceover(text="And how do you pick the right depth?") as tracker:
            self.play(Indicate(depth_slider, color=HIGHLIGHT, scale_factor=1.08), run_time=min(1.5, tracker.duration))

        # 8.16: 5-fold cross-validation bar; the parked chart's peak gets circled
        n_folds = CV["cv"]["n_splits"]
        slices = VGroup(*[Rectangle(width=0.9, height=0.45) for _ in range(n_folds)]).arrange(RIGHT, buff=0)
        slices.set_stroke(GRID, 2).set_fill(CLASS_0, 0.25).move_to([3.5, -2.25, 0])
        hidden_lab = label("hidden", CAPTION_SIZE * 0.8, TEXT_MUTED)
        train_txt = label("the rest: train", CAPTION_SIZE * 0.8, TEXT_MUTED).next_to(slices, DOWN, buff=0.2)

        def hide(i):
            return [
                *[s.animate.set_fill(HIGHLIGHT if j == i else CLASS_0, 0.8 if j == i else 0.25) for j, s in enumerate(slices)],
                hidden_lab.animate.next_to(slices[i], UP, buff=0.12),
            ]

        hidden_lab.next_to(slices[0], UP, buff=0.12)
        slices[0].set_fill(HIGHLIGHT, 0.8)
        peak_ring = Circle(radius=0.12, color=HIGHLIGHT, stroke_width=3).move_to(peak)
        with self.voiceover(
            text="Hide part of the data from the tree, test on that hidden part, repeat with different slices hidden, "
            "and keep the depth that does best."
        ) as tracker:
            self.play(FadeIn(slices, hidden_lab, train_txt), run_time=FAST)
            step = max(0.6, (tracker.duration - 2.5) / n_folds)
            for i in list(range(1, n_folds)) + [0]:
                self.play(*hide(i), run_time=step)
            self.play(Create(peak_ring), Indicate(peak, color=HIGHLIGHT), run_time=NORMAL)
            leaves_to(TREES[best_d], depth_slider.knob_to(best_d), leaf_slider.knob_to(stops_ml[0]), run_time=NORMAL)

        # 8.17
        cv_title = label("cross-validation", BODY_SIZE, TEXT).move_to([3.5, CAPTION_POSITION[1], 0])
        with self.voiceover(text="That's cross-validation.") as tracker:
            self.play(Write(cv_title), run_time=min(1.2, tracker.duration))
        self.wait(SLOW)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=NORMAL)
