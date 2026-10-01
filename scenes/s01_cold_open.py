"""Scene 1: cold open (docs/STORYBOARD.md, rows 1.1-1.11).

A loan application falls down a decision tree to a "Deny" leaf, then we ask
which question should come first.
"""

import json
import random
from pathlib import Path

import numpy as np
from manim import (
    BOLD,
    ORIGIN,
    Dot,
    Circumscribe,
    FadeIn,
    FadeOut,
    Flash,
    Indicate,
    LaggedStart,
    Line,
    RoundedRectangle,
    ShowPassingFlash,
    Succession,
    Text,
    VGroup,
    Write,
    there_and_back,
)
from manim_voiceover import VoiceoverScene

from components.tree_diagram import TreeDiagram
from style import *
from voice import speech_service

DATA = Path(__file__).resolve().parents[1] / "data"
DENY_LEAF = "deny_income"  # the leaf the applicant lands on


def loan_card() -> VGroup:
    """The application: four features, values consistent with the deny path."""
    title = Text("Loan application", font=FONT, font_size=CAPTION_SIZE, color=TEXT, weight=BOLD)
    rows = VGroup(
        *[
            Text(f"{k}: {v}", font=FONT, font_size=CAPTION_SIZE - 2, color=TEXT_MUTED)
            for k, v in [
                ("Age", "23"),
                ("Home-owner", "no"),
                ("Income", "3,800"),
                ("Education", "secondary"),
            ]
        ]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    body = VGroup(title, Line(LEFT, RIGHT, color=GRID).set_width(title.width + 0.4), rows).arrange(
        DOWN, buff=0.25
    )
    rows.align_to(body, LEFT)
    box = RoundedRectangle(
        width=body.width + 0.6,
        height=body.height + 0.6,
        corner_radius=0.15,
        stroke_color=TEXT_MUTED,
        stroke_width=2,
        fill_color=BACKGROUND,
        fill_opacity=1,
    )
    body.move_to(box)
    return VGroup(box, body)


def overgrown_spec(seed: int = 3, max_depth: int = 6) -> dict:
    """A deep, bushy tree for the 1.11 teaser (structure only, no labels)."""
    rng = random.Random(seed)
    counter = iter(range(10_000))

    def grow(d: int) -> dict:
        nid = f"n{next(counter)}"
        if d == max_depth or (d >= 3 and rng.random() < 0.3):
            return {"id": nid, "leaf": rng.choice(["Deny", "Approve"])}
        return {"id": nid, "q": "", "no": grow(d + 1), "yes": grow(d + 1)}

    return grow(0)


class ColdOpen(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())

        spec = json.loads((DATA / "loan_tree.json").read_text())
        card = loan_card().scale(0.9).move_to(LEFT * 4.95)
        tree = TreeDiagram(spec).scale(0.88).move_to(np.array([2.3, 0.25, 0]))
        path = tree.path_ids(DENY_LEAF)  # root -> income5k -> deny_income

        # 1.1
        with self.voiceover(text="This is a loan application, and this little flowchart just denied it.") as tracker:
            self.play(FadeIn(card, shift=UP * 0.3), run_time=1.0)
            self.play(tree.create_animation(), run_time=max(tracker.duration - 1.2, 1.5))

        # 1.2-1.4: a small copy of the card walks the path, sitting left of each node.
        token = card.copy().scale(0.22)

        def beside(nid: str):
            return tree.node(nid).get_left() + LEFT * (token.width / 2 + 0.12)

        def ask(nid: str) -> list:
            """Light a question node: outline turns HIGHLIGHT, text pulses.

            Indicate(color=...) on the whole node would recolor the box fill too
            and hide the text, so only the text is indicated.
            """
            box, text = tree.node(nid)
            return [box.animate.set_stroke(HIGHLIGHT, width=3), Indicate(text, color=TEXT, scale_factor=1.12)]

        with self.voiceover(text="Own a home? No.") as tracker:
            self.play(token.animate.move_to(beside(path[0])), run_time=0.8)
            self.play(*ask(path[0]), run_time=0.6)
            self.play(
                ShowPassingFlash(tree.edges[path[1]].copy().set_stroke(HIGHLIGHT, 8), time_width=0.6),
                *tree.light_edge(path[1]),
                token.animate.move_to(beside(path[1])),
                run_time=0.9,
            )

        with self.voiceover(text="Income above 5,000? No.") as tracker:
            self.play(*ask(path[1]), run_time=0.6)
            self.play(
                ShowPassingFlash(tree.edges[path[2]].copy().set_stroke(HIGHLIGHT, 8), time_width=0.6),
                *tree.light_edge(path[2]),
                token.animate.move_to(tree.node(DENY_LEAF).get_center()),
                run_time=0.9,
            )

        with self.voiceover(text="Denied.") as tracker:
            leaf = tree.node(DENY_LEAF)
            self.play(
                FadeOut(token, scale=0.4),
                Flash(leaf, color=IMPURITY, line_length=0.25, flash_radius=leaf.width / 2 + 0.15),
                leaf.animate(rate_func=there_and_back).scale(1.15),
                run_time=0.8,
            )

        # 1.5
        with self.voiceover(text="And the path itself is the explanation.") as tracker:
            self.play(tree.off_path_mobjects(DENY_LEAF).animate.set_opacity(DIM_OPACITY), run_time=0.8)
            self.play(
                LaggedStart(
                    *[Circumscribe(tree.node(i), color=HIGHLIGHT, buff=0.08) for i in path],
                    lag_ratio=0.4,
                ),
                run_time=max(tracker.duration - 0.8, 1.0),
            )

        # 1.6
        with self.voiceover(text="What's remarkable is that nobody wrote these questions by hand.") as tracker:
            self.play(FadeOut(card, shift=LEFT), tree.animate.move_to(ORIGIN + UP * 0.35), run_time=1.2)

        # 1.7: past applicants flow up into the tree.
        rng = np.random.default_rng(17)
        crowd = VGroup(
            *[
                Dot(
                    [rng.uniform(-6.2, 6.2), rng.uniform(-3.65, -2.95), 0],
                    radius=0.04,
                    color=CLASS_0 if rng.random() < 0.5 else CLASS_1,
                )
                for _ in range(150)
            ]
        )
        flyers = VGroup(*crowd[::12])
        with self.voiceover(
            text="An algorithm studied thousands of past applicants and worked out for itself "
            "which questions to ask, in what order, and where to set each cutoff."
        ) as tracker:
            self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in crowd], lag_ratio=0.01), run_time=1.5)
            root = tree.node(tree.root_id)
            self.play(
                LaggedStart(
                    *[d.animate.move_to(root.get_center()).scale(0.4).set_opacity(0) for d in flyers],
                    lag_ratio=0.15,
                ),
                run_time=max(tracker.duration - 2.3, 1.5),
            )
            self.play(FadeOut(crowd), run_time=0.6)

        # 1.8
        label = Text("decision tree", font=FONT, font_size=BODY_SIZE, color=TEXT).move_to(DOWN * 3.1)
        with self.voiceover(text="That's a decision tree.") as tracker:
            self.play(tree.animate.set_opacity(1), Write(label), run_time=min(1.2, tracker.duration))

        # 1.9: the root question becomes "?"
        root = tree.node(tree.root_id)
        qmark = Text("?", font=FONT, font_size=40, color=HIGHLIGHT, weight=BOLD).move_to(root[1])
        with self.voiceover(
            text="So out of all the questions it could ask, how does it decide which one comes first?"
        ) as tracker:
            self.play(FadeOut(label), root[1].animate.become(qmark), run_time=1.0)
            self.play(
                Succession(*[Indicate(root[1], color=HIGHLIGHT, scale_factor=1.3) for _ in range(2)]),
                run_time=max(tracker.duration - 1.0, 1.0),
            )

        # 1.10: let it breathe, with a slow pulse.
        with self.voiceover(text="The answer is a beautiful idea from information theory.") as tracker:
            self.play(root.animate(rate_func=there_and_back).scale(1.06), run_time=tracker.duration)

        # 1.11: teaser, the tree overgrows into a bushy mess, then snaps back.
        ghost = TreeDiagram(overgrown_spec(), labels=False, h_spacing=0.2, level_gap=0.75, edge_width=2)
        ghost.move_to(tree)
        restored = tree.copy()
        with self.voiceover(
            text="And by the end you'll also see why a tree that's perfect on the data it learned from "
            "can be confidently wrong about the very next person who walks in."
        ) as tracker:
            grow_time = 2.0
            self.play(FadeOut(tree), ghost.create_animation(lag_ratio=0.5), run_time=grow_time)
            self.wait(max(tracker.duration - grow_time - 1.0, 0.5))
            self.play(FadeOut(ghost), FadeIn(restored), run_time=1.0)
        tree = restored

        # Title card, hold 2 s.
        title = Text("Decision trees", font=FONT, font_size=TITLE_SIZE, color=TEXT, weight=BOLD)
        subtitle = Text("what should you ask first?", font=FONT, font_size=BODY_SIZE, color=TEXT_MUTED)
        card_title = VGroup(title, subtitle).arrange(DOWN, buff=0.35)
        self.play(FadeOut(tree), run_time=FAST)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2), run_time=1.5)
        self.wait(SLOW)
        self.play(FadeOut(card_title), run_time=FAST)
