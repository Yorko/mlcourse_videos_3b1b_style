"""Scene 5: growing the tree (docs/STORYBOARD.md, rows 5.1-5.16).

The 20 balls on the left get split recursively; every cut appears as a node
of the tree on the right at the same moment. The tree structure, thresholds
and leaf classes all come from ``data/balls.json["tree"]``.
"""

import json
import random
from pathlib import Path

import numpy as np
from manim import (
    ITALIC,
    AnimationGroup,
    Circle,
    Circumscribe,
    Create,
    CurvedArrow,
    DashedLine,
    FadeIn,
    FadeOut,
    Flash,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    SurroundingRectangle,
    Text,
    TransformFromCopy,
    VGroup,
    Write,
    Dot,
)
from manim_voiceover import VoiceoverScene

from components.tree_diagram import TreeDiagram
from style import *
from voice import speech_service

BALLS = json.loads((Path(__file__).resolve().parents[1] / "data" / "balls.json").read_text())
NODES = {n["id"]: n for n in BALLS["tree"]["nodes"]}
BALL_COLOR = {"blue": CLASS_0, "yellow": CLASS_1}

# Ball-row layouts: scene 4's end state (centred, wide) and scene 5's left panel.
ROW_WIDE = dict(center=np.array([0.0, 1.8, 0.0]), width=11.0, gap=1.2, radius=0.15)
ROW_PANEL = dict(center=np.array([-3.25, 1.5, 0.0]), width=6.2, gap=0.32, radius=0.11)
TREE_ROOT = np.array([3.5, 2.6, 0.0])
TREE_LEVEL_GAP = 1.1
DEMO_BALL = 15  # the ball that walks down the tree in 5.8


def label(text, size=CAPTION_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def nid(i: int) -> str:
    return f"n{i}"


# --- Ball row ------------------------------------------------------------------


class BallRow(VGroup):
    """20 balls at positions 0..19, with a small position label under each.

    Cuts are threshold values t (cut between ball t and t+1). ``layout`` puts
    every active cut's gap into the row while keeping its total width fixed.
    """

    def __init__(self, colors, **kwargs):
        super().__init__(**kwargs)
        self.n = len(colors)
        self.dots = VGroup(*[Dot(radius=0.15, color=BALL_COLOR[c]) for c in colors])
        self.labels = VGroup(*[label(str(i), CAPTION_SIZE * 0.55, TEXT_MUTED) for i in range(self.n)])
        self.cut_lines: dict[int, DashedLine] = {}
        self.cuts: list[int] = []
        self.add(self.dots, self.labels)

    def positions(self, cuts, center, width, gap, **_):
        cuts = sorted(cuts)
        unit = (width - gap * len(cuts)) / (self.n - 1)
        xs = np.array([i * unit + gap * sum(1 for t in cuts if t < i) for i in range(self.n)])
        xs += center[0] - (xs[0] + xs[-1]) / 2
        cut_xs = {t: (xs[t] + xs[t + 1]) / 2 for t in cuts}
        return xs, cut_xs

    def _cut_line(self, x, y, radius):
        h = radius * 5
        return DashedLine([x, y - h, 0], [x, y + h, 0], color=HIGHLIGHT, stroke_width=3, dash_length=0.06)

    def place(self, cuts, center, width, gap, radius):
        """Set the layout instantly (no animation), creating cut lines."""
        self.cuts = list(cuts)
        xs, cut_xs = self.positions(cuts, center, width, gap)
        for i, (d, lab) in enumerate(zip(self.dots, self.labels)):
            d.scale_to_fit_width(2 * radius).move_to([xs[i], center[1], 0])
            lab.next_to(d, DOWN, buff=radius * 0.8)
        for t in cuts:
            line = self._cut_line(cut_xs[t], center[1], radius)
            self.cut_lines[t] = line
        return self

    def layout_anims(self, cuts, center, width, gap, radius):
        """Animations moving balls, labels and existing cut lines to a new layout."""
        self.cuts = list(cuts)
        xs, cut_xs = self.positions(cuts, center, width, gap)
        anims = []
        for i, (d, lab) in enumerate(zip(self.dots, self.labels)):
            target = d.copy().scale_to_fit_width(2 * radius).move_to([xs[i], center[1], 0])
            lab_target = lab.copy().next_to(target, DOWN, buff=radius * 0.8)
            anims += [d.animate.become(target), lab.animate.move_to(lab_target)]
        for t, line in self.cut_lines.items():
            if t in cut_xs:
                anims.append(line.animate.become(self._cut_line(cut_xs[t], center[1], radius).match_style(line)))
        return anims

    def new_cut_line(self, t, center, width, gap, radius):
        """A cut line at threshold t in the *current* (unsplit) layout, ready to Create."""
        xs, _ = self.positions(self.cuts, center, width, gap)
        line = self._cut_line((xs[t] + xs[t + 1]) / 2, center[1], radius)
        self.cut_lines[t] = line
        return line

    def group(self, idx) -> VGroup:
        return VGroup(*[self.dots[i] for i in idx], *[self.labels[i] for i in idx])


# --- Tree ----------------------------------------------------------------------


def tree_spec(i: int = 0) -> dict:
    """balls.json tree -> TreeDiagram spec. The "x <= t" (true) child goes left."""
    n = NODES[i]
    if n["leaf"]:
        return {"id": nid(i), "leaf": n["prediction"]}
    return {
        "id": nid(i),
        "q": n["question"].replace("<=", "≤"),
        "no": tree_spec(n["left"]),  # TreeDiagram puts "no" on the left...
        "yes": tree_spec(n["right"]),
    }


class BallTree(TreeDiagram):
    """TreeDiagram with ball-colored circle leaves and yes/no labels for "x ≤ t"."""

    LEAF_RADIUS = 0.17

    def _make_node(self, node, labels, font_size, dot_radius):
        if "leaf" in node:
            color = BALL_COLOR[node["leaf"]]
            return VGroup(Circle(radius=self.LEAF_RADIUS, color=color, fill_color=color, fill_opacity=1))
        return super()._make_node(node, labels, font_size, dot_radius)

    def __init__(self, spec, **kwargs):
        super().__init__(spec, **kwargs)
        # ...so the left edge answers "yes" to "x ≤ t": swap the edge labels.
        for cid, lab in list(self.edge_labels.items()):
            word = "Yes" if lab.text == "No" else "No"
            new = Text(word, font=FONT, font_size=lab.font_size, color=TEXT_MUTED).move_to(lab)
            self.submobjects[self.submobjects.index(lab)] = new
            self.edge_labels[cid] = new

    def piece(self, cid: str) -> VGroup:
        """Edge + edge label + node for a non-root node."""
        return VGroup(self.edges[cid], self.edge_labels[cid], self.nodes[cid])


def random_tree_spec(rng: random.Random, max_depth: int) -> dict:
    counter = iter(range(10_000))

    def grow(d):
        i = f"r{next(counter)}"
        if d == max_depth or (d >= 1 and rng.random() < 0.35):
            return {"id": i, "leaf": "x"}
        return {"id": i, "q": "", "no": grow(d + 1), "yes": grow(d + 1)}

    return grow(0)


# --- Scene ---------------------------------------------------------------------


class GrowingTree(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())

        root_t = NODES[0]["t"]
        right_id, left_id = NODES[0]["right"], NODES[0]["left"]

        balls = BallRow(BALLS["colors"]).place([root_t], **ROW_WIDE)
        tree = BallTree(tree_spec(), level_gap=TREE_LEVEL_GAP, font_size=CAPTION_SIZE - 2, h_gap=0.25)
        tree.move_root_to(TREE_ROOT)
        # Keep the tree inside the right panel.
        if tree.get_right()[0] > config_right() or tree.get_left()[0] < 0.3:
            tree.scale_to_fit_width(min(tree.width, config_right() - 0.3))
            tree.move_root_to(TREE_ROOT)
        tree.shift(RIGHT * max(0.0, 0.3 - tree.get_left()[0]))
        tree.shift(LEFT * max(0.0, tree.get_right()[0] - config_right()))

        # Start where scene 4 ends: balls split at the winning cut.
        self.add(balls, balls.cut_lines[root_t])

        # 5.1
        root = tree.node(nid(0))
        root[0].set_stroke(HIGHLIGHT, width=3)
        with self.voiceover(text="One question doesn't make a tree, though.") as tracker:
            self.play(*balls.layout_anims([root_t], **ROW_PANEL), run_time=1.2)
            self.play(GrowFromCenter(root), run_time=min(0.8, max(tracker.duration - 1.2, 0.4)))

        # 5.2: two "?" stubs
        def qmark(i):
            return label("?", BODY_SIZE, TEXT_MUTED).move_to(tree.node(nid(i)))

        stubs = {i: qmark(i) for i in (left_id, right_id)}
        with self.voiceover(text="What do we do with the two groups we just made?") as tracker:
            self.play(
                LaggedStart(
                    *[
                        AnimationGroup(Create(tree.edges[nid(i)]), FadeIn(tree.edge_labels[nid(i)]), FadeIn(stubs[i]))
                        for i in (left_id, right_id)
                    ],
                    lag_ratio=0.4,
                ),
                run_time=min(1.5, tracker.duration),
            )

        # 5.3
        right_box = SurroundingRectangle(balls.group(NODES[right_id]["balls"]), color=HIGHLIGHT, buff=0.1)
        with self.voiceover(text="We do exactly the same thing again, inside each group.") as tracker:
            self.play(Create(right_box), run_time=0.8)
            self.play(Indicate(stubs[right_id], color=HIGHLIGHT, scale_factor=1.5), run_time=1.0)

        # One split step: cut line + node on the tree (synced), then the gap opens
        # and any pure children grow as leaves.
        def cut_and_node(i, extra=()):
            n = NODES[i]
            line = balls.new_cut_line(n["t"], **ROW_PANEL)
            node = tree.node(nid(i))
            if i in stubs:
                grow = ReplacementTransform(stubs.pop(i), node)
            else:
                grow = AnimationGroup(
                    Create(tree.edges[nid(i)]), FadeIn(tree.edge_labels[nid(i)]), GrowFromCenter(node)
                )
            return AnimationGroup(Create(line), grow, *extra)

        def split_and_leaves(i):
            n = NODES[i]
            cuts = balls.cuts + [n["t"]]
            leaves = [c for c in (n["left"], n["right"]) if NODES[c]["leaf"]]
            return AnimationGroup(
                *balls.layout_anims(cuts, **ROW_PANEL),
                *[Create(tree.edges[nid(c)]) for c in leaves],
                *[FadeIn(tree.edge_labels[nid(c)]) for c in leaves],
                *[GrowFromCenter(tree.node(nid(c))) for c in leaves],
            )

        # 5.4
        with self.voiceover(
            text="The right group needs just one more question, \"is the position at most eighteen?\", "
            "and both pieces come out a single color."
        ) as tracker:
            step = max(tracker.duration - 0.5, 2.4) / 3
            self.play(cut_and_node(right_id, extra=[FadeOut(right_box)]), run_time=step * 1.2)
            self.play(split_and_leaves(right_id), run_time=step * 1.8)

        # 5.5: the remaining internal nodes on the left, top-down.
        left_chain = []
        frontier = [left_id]
        while frontier:
            i = frontier.pop(0)
            if not NODES[i]["leaf"]:
                left_chain.append(i)
                frontier += [NODES[i]["left"], NODES[i]["right"]]
        with self.voiceover(text="The left group is messier and takes three more cuts.") as tracker:
            per = max(tracker.duration, 3.0) / len(left_chain)
            for i in left_chain:
                self.play(cut_and_node(i), run_time=per * 0.45)
                self.play(split_and_leaves(i), run_time=per * 0.55)

        # The cut lines fade to GRID now that every split is done.
        leaf_ids = [i for i, n in NODES.items() if n["leaf"]]

        # 5.6: S = 0 under every pure group
        tags = VGroup()
        for i in leaf_ids:
            grp = balls.group(NODES[i]["balls"])
            tags.add(MathTex("S=0", font_size=CAPTION_SIZE * 0.85, color=GAIN).next_to(grp, DOWN, buff=0.15))
        with self.voiceover(
            text="A group where every ball is the same color has entropy zero, "
            "so there's nothing left to ask, and we stop."
        ) as tracker:
            self.play(
                *[line.animate.set_color(GRID) for line in balls.cut_lines.values()],
                root[0].animate.set_stroke(TEXT_MUTED, width=2),
                run_time=0.6,
            )
            self.play(
                LaggedStart(*[FadeIn(t, shift=UP * 0.15) for t in tags], lag_ratio=0.3),
                run_time=min(2.5, max(tracker.duration - 0.6, 1.0)),
            )

        # 5.7: leaves are at different depths, so ring each one instead of a brace.
        leaf_nodes = [tree.node(nid(i)) for i in leaf_ids]
        rings = VGroup(
            *[Circle(radius=BallTree.LEAF_RADIUS + 0.1, color=HIGHLIGHT, stroke_width=3).move_to(m) for m in leaf_nodes]
        )
        leaves_label = label("leaves", BODY_SIZE * 0.8, TEXT).next_to(tree, DOWN, buff=0.35)
        with self.voiceover(text="Those end points are called leaves.") as tracker:
            self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.15), Write(leaves_label), run_time=1.5)

        # 5.8: one ball walks down its path to its leaf.
        demo_leaf = next(i for i in leaf_ids if DEMO_BALL in NODES[i]["balls"])
        path = tree.path_ids(nid(demo_leaf))
        token = balls.dots[DEMO_BALL].copy()
        with self.voiceover(text="Each one predicts the color of the balls that land in it.") as tracker:
            self.play(FadeOut(tags), FadeOut(rings), run_time=0.5)
            moving = token.copy().move_to(tree.node(path[0]).get_left() + LEFT * 0.25)
            self.play(TransformFromCopy(balls.dots[DEMO_BALL], moving), run_time=0.8)
            for cid in path[1:]:
                target = tree.node(cid).get_center() if cid == path[-1] else tree.node(cid).get_left() + LEFT * 0.25
                self.play(*tree.light_edge(cid), moving.animate.move_to(target), run_time=0.7)
            leaf = tree.node(path[-1])
            self.play(
                FadeOut(moving),
                Flash(leaf, color=leaf[0].get_fill_color(), flash_radius=BallTree.LEAF_RADIUS + 0.15, line_length=0.2),
                run_time=0.6,
            )

        # 5.9
        counter = label(f"{BALLS['tree']['n_questions']} questions", BODY_SIZE * 0.8, TEXT).move_to(leaves_label)
        algos = label("ID3 · C4.5 · CART", CAPTION_SIZE, TEXT_MUTED)
        algos.to_corner(DOWN + RIGHT, buff=EDGE_BUFF)
        with self.voiceover(text="That's the core idea behind the classic tree algorithms.") as tracker:
            self.play(
                *[tree.edges[c].animate.set_stroke(GRID, width=3) for c in path[1:]],
                *[tree.edge_labels[c].animate.set_color(TEXT_MUTED) for c in path[1:]],
                ReplacementTransform(leaves_label, counter),
                run_time=0.8,
            )
            self.play(FadeIn(algos, shift=UP * 0.2), run_time=0.8)

        # 5.10: the greedy loop
        steps = VGroup(
            *[
                label(s, CAPTION_SIZE, TEXT)
                for s in ("1. pick the split with the biggest gain", "2. split", "3. repeat inside each part")
            ]
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        steps.move_to(np.array([-3.2, -1.2, 0]))
        loop = CurvedArrow(
            steps[2].get_left() + LEFT * 0.15, steps[0].get_left() + LEFT * 0.15, angle=-np.pi * 0.9, color=HIGHLIGHT
        )
        with self.voiceover(
            text="At every node, grab the question with the biggest gain right now, split, "
            "and then repeat the whole process inside each piece."
        ) as tracker:
            t = max(tracker.duration - 1.0, 3.0)
            self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.2) for s in steps], lag_ratio=0.6), run_time=t * 0.6)
            self.play(Create(loop), run_time=t * 0.25)
            self.play(Indicate(steps[0], color=HIGHLIGHT, scale_factor=1.05), run_time=t * 0.15)

        # 5.11
        question = label("best now = best overall?", BODY_SIZE, TEXT).move_to(DOWN * 3.1)
        with self.voiceover(
            text="Is grabbing the best question right now guaranteed to give the best tree overall?"
        ) as tracker:
            self.play(FadeOut(algos), Write(question), run_time=min(1.5, tracker.duration))

        # 5.12: "No." then the swarm of possible trees
        cross = MathTex(r"\times", font_size=TITLE_SIZE, color=IMPURITY).next_to(question, RIGHT, buff=0.25)
        with self.voiceover(text="No.") as tracker:
            self.play(FadeIn(cross, scale=1.6), question.animate.set_color(TEXT_MUTED), run_time=0.6)

        rng = random.Random(5)
        swarm = VGroup()
        for _ in range(40):
            s = TreeDiagram(random_tree_spec(rng, 4), labels=False, h_spacing=0.2, level_gap=0.5, edge_width=2)
            s.scale(rng.uniform(0.25, 0.45)).move_to([rng.uniform(-6.2, 6.2), rng.uniform(-3.3, 3.3), 0])
            swarm.add(s)
        swarm.set_opacity(0.15)
        with self.voiceover(
            text="Finding the truly best tree would mean searching through an astronomical number of possible trees, "
            "so in practice everyone settles for this greedy shortcut."
        ) as tracker:
            self.play(FadeOut(steps), FadeOut(loop), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(s, scale=0.6) for s in swarm], lag_ratio=0.08), run_time=max(tracker.duration - 2.2, 2.0))
            self.play(FadeOut(swarm), FadeOut(question), FadeOut(cross), run_time=1.0)

        # 5.13
        with self.voiceover(text="It works remarkably well.") as tracker:
            self.play(Indicate(tree, color=HIGHLIGHT, scale_factor=1.04), run_time=min(1.2, tracker.duration))

        # 5.14: glow + "perfect"
        glow = VGroup(*tree.edges.values(), *[tree.node(k)[0] for k in tree.nodes]).copy()
        glow.set_fill(opacity=0).set_stroke(GAIN, width=9, opacity=0)
        perfect = label("perfect", BODY_SIZE, GAIN, slant=ITALIC)
        perfect.next_to(root, RIGHT, buff=0.6)
        with self.voiceover(
            text="So now our tree is perfect: every training ball lands in a leaf of its own color."
        ) as tracker:
            self.bring_to_back(glow)
            self.play(glow.animate.set_stroke(opacity=0.3), run_time=1.0)
            self.play(Write(perfect), run_time=1.0)

        # 5.15
        with self.voiceover(text="Hold on to that word, perfect.") as tracker:
            self.play(Circumscribe(perfect, color=HIGHLIGHT, buff=0.12), run_time=min(1.5, tracker.duration))

        # 5.16: foreshadow. (Scene 8 rebuilds the same tree from balls.json, so no extra state is saved.)
        with self.voiceover(text="It's going to come back to bite us.") as tracker:
            self.play(perfect.animate.set_color(IMPURITY), run_time=0.3)
            self.wait(0.3)
            self.play(perfect.animate.set_color(GAIN), run_time=0.3)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=NORMAL)


def config_right() -> float:
    from manim import config

    return config.frame_width / 2 - EDGE_BUFF
