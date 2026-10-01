"""Scene 10: wrap-up (docs/STORYBOARD.md, rows 10.1-10.9).

The cold-open loan tree returns with its path lit, regrows into a different
tree after a few past applicants change, and then multiplies into a forest
that votes.
"""

import json
from pathlib import Path

import numpy as np
from manim import (
    BOLD,
    ORIGIN,
    AnimationGroup,
    Circumscribe,
    Dot,
    FadeIn,
    FadeOut,
    FadeTransform,
    Flash,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    MoveToTarget,
    Rectangle,
    ShowPassingFlash,
    Text,
    VGroup,
    Write,
    there_and_back,
)
from manim_voiceover import VoiceoverScene

from components.forest import Forest
from components.tree_diagram import TreeDiagram
from scenes.s01_cold_open import loan_card
from style import *
from voice import speech_service

DATA = Path(__file__).resolve().parents[1] / "data"
V1 = json.loads((DATA / "loan_tree.json").read_text())
D = json.loads((DATA / "loan_tree_v2.json").read_text())
V2 = D["v2"]
FOREST = D["forest"]

TREE_SCALE, TREE_POS = 0.88, np.array([2.3, 0.25, 0])  # scene 1's layout
CARD_POS = LEFT * 4.95


def label(text, size=CAPTION_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


def light_path_now(tree: TreeDiagram, path: list[str]) -> None:
    """Static version of scene 1's lighting: question outlines and edges in HIGHLIGHT."""
    for nid in path[:-1]:
        tree.node(nid)[0].set_stroke(HIGHLIGHT, width=3)
    for cid in path[1:]:
        tree.edges[cid].set_stroke(color=HIGHLIGHT, width=6)
        if cid in tree.edge_labels:
            tree.edge_labels[cid].set_color(HIGHLIGHT)


class WrapUp(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())

        # Scene-1 state at 1.5: card on the left, tree on the right, path lit, rest dimmed.
        card = loan_card().scale(0.9).move_to(CARD_POS)
        tree = TreeDiagram(V1).scale(TREE_SCALE).move_to(TREE_POS)
        path = D["v1_path"]
        light_path_now(tree, path)
        off_path = tree.off_path_mobjects(path[-1])
        off_path.set_opacity(DIM_OPACITY)

        # 10.1
        with self.voiceover(text="So which question comes first?") as tracker:
            self.play(FadeIn(card), FadeIn(tree), run_time=min(1.2, tracker.duration))

        # 10.2: root first, then the same rule level by level.
        depth = max(tree.node_depth.values())
        levels = [
            [tree.node(i) for i, d in tree.node_depth.items() if d == k and i not in tree.leaves]
            for k in range(depth)
        ]
        with self.voiceover(
            text="The one with the biggest information gain, then the same rule again, all the way down."
        ) as tracker:
            self.play(off_path.animate.set_opacity(1), run_time=0.6)
            self.play(Indicate(levels[0][0][1], color=GAIN, scale_factor=1.3), run_time=1.0)
            self.play(
                LaggedStart(
                    *[
                        AnimationGroup(*[Indicate(n[1], color=GAIN, scale_factor=1.2) for n in lvl])
                        for lvl in levels[1:]
                    ],
                    lag_ratio=0.6,
                ),
                run_time=max(tracker.duration - 1.6, 1.0),
            )

        # 10.3
        with self.voiceover(text="That gives you a model you can read like a flowchart.") as tracker:
            self.play(
                LaggedStart(
                    *[Circumscribe(tree.node(i), color=HIGHLIGHT, buff=0.08) for i in path],
                    lag_ratio=0.4,
                ),
                run_time=max(tracker.duration, 1.0),
            )

        # 10.4: six past applicants; three of them change their outcome.
        past = D["past_applicants"]
        cls = [CLASS_0, CLASS_1]
        dots = VGroup(*[Dot(radius=0.16, color=cls[c]) for c in past["before"]]).arrange(RIGHT, buff=0.45)
        past_label = label("past applicants", color=TEXT_MUTED)
        row = VGroup(past_label, dots).arrange(RIGHT, buff=0.5).move_to([TREE_POS[0], -3.0, 0])
        with self.voiceover(text="But here's the catch.") as tracker:
            self.play(FadeIn(past_label), LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.1),
                      run_time=0.8)
            self.play(
                LaggedStart(*[dots[i].animate.set_color(cls[past["after"][i]]) for i in past["flipped"]],
                            lag_ratio=0.3),
                run_time=max(tracker.duration - 0.8, 0.8),
            )

        # 10.5: the tree regrows; the card walks the new path, still to "Deny".
        old_path = tree.path_mobjects(path[-1]).copy()
        tree2 = TreeDiagram(V2).scale(TREE_SCALE).move_to(TREE_POS)
        path2 = D["v2_path"]
        token = card.copy().scale(0.22)

        def beside(nid: str):
            return tree2.node(nid).get_left() + LEFT * (token.width / 2 + 0.12)

        def ask(nid: str) -> list:
            box, text = tree2.node(nid)
            return [box.animate.set_stroke(HIGHLIGHT, width=3), Indicate(text, color=TEXT, scale_factor=1.12)]

        with self.voiceover(
            text="Change a handful of past applicants, and the tree can regrow completely: "
            "different questions, a different reason for the same denial."
        ) as tracker:
            regrow = 2.0
            self.play(FadeTransform(tree, tree2), FadeOut(row), run_time=regrow)
            step = max((tracker.duration - regrow - 0.8 - 0.8) / (len(path2) - 1), 0.9)
            self.play(token.animate.move_to(beside(path2[0])), run_time=0.8)
            for k in range(len(path2) - 1):
                here, nxt = path2[k], path2[k + 1]
                self.play(*ask(here), run_time=0.4 * step)
                target = tree2.node(nxt).get_center() if nxt == path2[-1] else beside(nxt)
                self.play(
                    ShowPassingFlash(tree2.edges[nxt].copy().set_stroke(HIGHLIGHT, 8), time_width=0.6),
                    *tree2.light_edge(nxt),
                    token.animate.move_to(target),
                    run_time=0.6 * step,
                )
            leaf = tree2.node(path2[-1])
            self.play(
                FadeOut(token, scale=0.4),
                Flash(leaf, color=IMPURITY, line_length=0.25, flash_radius=leaf.width / 2 + 0.15),
                leaf.animate(rate_func=there_and_back).scale(1.15),
                run_time=0.8,
            )

        # 10.6: the old path as a ghost, next to the new tree.
        ghost = old_path.set_opacity(DIM_OPACITY).scale(0.75).move_to(LEFT * 4.3 + UP * 0.4)
        with self.voiceover(text="The path is the explanation, but it isn't stable.") as tracker:
            self.play(
                FadeOut(card, shift=LEFT),
                tree2.animate.scale(0.75).move_to(RIGHT * 3.0 + UP * 0.25),
                run_time=1.0,
            )
            self.play(FadeIn(ghost), run_time=1.0)
            self.play(
                tree2.off_path_mobjects(path2[-1]).animate.set_opacity(DIM_OPACITY),
                run_time=max(min(tracker.duration - 2.0, 1.0), 0.5),
            )

        # 10.7
        with self.voiceover(text="The fix is wonderfully simple.") as tracker:
            tree2.generate_target()
            tree2.target.set_opacity(1).scale(0.3 / 0.75).move_to(ORIGIN)
            for e in tree2.target.edges.values():  # strokes don't scale with the tree
                e.set_stroke(width=e.get_stroke_width() * 0.4)
            for nd in tree2.target.nodes.values():
                nd[0].set_stroke(width=nd[0].get_stroke_width() * 0.5)
            self.play(FadeOut(ghost), MoveToTarget(tree2), run_time=min(1.5, tracker.duration))

        # 10.8: a forest of trees, each votes; 30 representative votes fly to a tally bar.
        forest = Forest(FOREST["trees"], cols=15, cell_w=0.8, cell_h=0.62, icon_width=0.62, seed=10).move_to(UP * 0.3)
        center = forest.icons[len(forest.icons) // 2 + 7]  # 8 rows x 15 cols: a middle-ish icon

        n, tally = FOREST["n_trees"], FOREST["tally"]
        bar_w, bar_h, bar_y = 7.0, 0.32, -2.75
        frame = Rectangle(width=bar_w, height=bar_h).set_stroke(GRID, 2).move_to([0, bar_y, 0])
        deny_w = bar_w * tally["Deny"] / n
        deny_bar = Rectangle(width=deny_w, height=bar_h).set_fill(IMPURITY, 1).set_stroke(width=0)
        deny_bar.align_to(frame, LEFT).set_y(bar_y)
        appr_bar = Rectangle(width=bar_w - deny_w, height=bar_h).set_fill(HIGHLIGHT, 1).set_stroke(width=0)
        appr_bar.align_to(frame, RIGHT).set_y(bar_y)
        deny_lab = label(f"Deny {tally['Deny']}", color=IMPURITY).next_to(frame, LEFT, buff=0.25)
        appr_lab = label(f"{tally['Approve']} Approve", color=HIGHLIGHT).next_to(frame, RIGHT, buff=0.25)

        reps = FOREST["representatives"]
        rng = np.random.default_rng(10)
        flyers, landings = [], []
        for i in reps:
            vote = FOREST["trees"][i]["vote"]
            d = Dot(forest.landing_point(i), radius=0.06, color=IMPURITY if vote == "Deny" else HIGHLIGHT)
            seg = deny_bar if vote == "Deny" else appr_bar
            x = rng.uniform(seg.get_left()[0] + 0.1, seg.get_right()[0] - 0.1)
            flyers.append(d)
            landings.append([x, bar_y, 0])

        with self.voiceover(
            text="Grow hundreds of trees, each on a random resample of the data, and let them vote."
        ) as tracker:
            grow = max(tracker.duration * 0.45, 2.0)
            others = [ic for ic in forest.icons if ic is not center]
            self.play(FadeTransform(tree2, center), run_time=0.8)
            self.play(LaggedStart(*[FadeIn(ic, scale=0.6) for ic in others], lag_ratio=0.01), run_time=grow)
            self.play(FadeIn(frame), *[FadeIn(d, scale=0.3) for d in flyers], run_time=0.5)
            fly = max(tracker.duration - grow - 0.8 - 0.5 - 1.0, 1.5)
            self.play(
                LaggedStart(*[d.animate.move_to(p) for d, p in zip(flyers, landings)], lag_ratio=0.05),
                run_time=fly,
            )
            self.play(
                FadeOut(VGroup(*flyers)),
                GrowFromEdge(deny_bar, LEFT),
                GrowFromEdge(appr_bar, RIGHT),
                FadeIn(deny_lab),
                FadeIn(appr_lab),
                run_time=1.0,
            )
        self.play(Indicate(deny_lab, color=IMPURITY, scale_factor=1.25), run_time=1.0)

        # 10.9: end card.
        title = label("Random forests: next", TITLE_SIZE, weight=BOLD).move_to(TITLE_POSITION)
        credit = label("mlcourse.ai · Topic 3", color=TEXT_MUTED).move_to(CAPTION_POSITION)
        tally_group = VGroup(frame, deny_bar, appr_bar, deny_lab, appr_lab)
        with self.voiceover(text="That's a random forest, and it's next.") as tracker:
            self.play(
                FadeOut(tally_group),
                forest.animate.set_opacity(DIM_OPACITY).shift(DOWN * 0.3),
                run_time=0.6,
            )
            self.play(Write(title), FadeIn(credit), run_time=max(min(tracker.duration - 0.6, 2.0), 1.0))
        self.wait(3)
        self.play(FadeOut(VGroup(forest, title, credit)), run_time=NORMAL)
