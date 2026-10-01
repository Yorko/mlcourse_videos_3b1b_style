"""Scene 1a: course intro (docs/STORYBOARD.md, rows 1a.1-1a.2).

Plays right after the cold open's title card. The images are prepared by
scripts/prep_s01a_assets.py (circular portrait, banner cut into three pieces
with the outer white keyed out) and scripts/key_s01a_mascot.py (keys a
replacement ods_mascot.png into ods_mascot_keyed.png).
"""

from pathlib import Path

import numpy as np
from manim import (
    BOLD,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Indicate,
    Text,
    VGroup,
    Write,
)
from manim_voiceover import VoiceoverScene

from components.tree_diagram import TreeDiagram
from style import *
from voice import speech_service

IMAGES = Path(__file__).resolve().parents[1] / "media" / "images" / "s01a_intro"
BANNER_WIDTH = 12.5  # frame units, all three pieces together


def banner() -> Group:
    """Left stickers, mascot, right stickers, side by side at a common height.

    Pieces are matched by height rather than pixel scale, so a higher-resolution
    replacement for one piece (like the redrawn mascot) still lines up. The
    mascot is the keyed copy made by scripts/key_s01a_mascot.py.
    """
    files = ("ods_left.png", "ods_mascot_keyed.png", "ods_right.png")
    pieces = [ImageMobject(IMAGES / f) for f in files]
    aspects = [p.pixel_array.shape[1] / p.pixel_array.shape[0] for p in pieces]
    height = BANNER_WIDTH / sum(aspects)
    x = -BANNER_WIDTH / 2
    for piece, aspect in zip(pieces, aspects):
        piece.set_height(height)
        piece.move_to([x + height * aspect / 2, 0, 0])
        x += height * aspect
    return Group(*pieces)


def tree_icon_spec() -> dict:
    """A full depth-3 tree with class-colored leaves, for the small icon."""
    leaves = iter(["0", "0", "1", "0", "1", "1", "0", "1"])
    counter = iter(range(100))

    def grow(d: int) -> dict:
        nid = f"t{next(counter)}"
        if d == 3:
            return {"id": nid, "leaf": next(leaves)}
        return {"id": nid, "q": "", "no": grow(d + 1), "yes": grow(d + 1)}

    return grow(0)


class CourseIntro(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())

        stickers = banner().move_to(UP * 1.0)
        left, mascot, right = stickers
        title = Text("mlcourse.ai", font=FONT, font_size=TITLE_SIZE, color=TEXT, weight=BOLD)
        title.move_to(DOWN * 1.3)
        lecture = VGroup(
            Text("Lecture", font=FONT, font_size=BODY_SIZE, color=TEXT_MUTED),
            Text("3", font=FONT, font_size=BODY_SIZE, color=HIGHLIGHT, weight=BOLD),
            Text("·", font=FONT, font_size=BODY_SIZE, color=TEXT_MUTED),
            Text("Decision trees", font=FONT, font_size=BODY_SIZE, color=TEXT_MUTED),
        ).arrange(RIGHT, buff=0.18)
        lecture.move_to(DOWN * 2.1)
        topic = lecture[3]

        # 1a.1: mascot first, then the stickers fan out from it.
        with self.voiceover(text="This is lecture 3 of the machine learning course mlcourse.ai.") as tracker:
            beat = max(tracker.duration / 4, 0.5)
            self.play(FadeIn(mascot, scale=0.8), run_time=beat)
            self.play(
                FadeIn(left, shift=RIGHT * 0.6),
                FadeIn(right, shift=LEFT * 0.6),
                run_time=beat,
            )
            self.play(Write(title), run_time=beat)
            self.play(FadeIn(lecture, shift=UP * 0.2), run_time=beat * 0.8)

        # 1a.2: one voiceover block (better prosody than splitting the sentence);
        # "I'm Yury," is roughly the first third of the audio.
        portrait = ImageMobject(IMAGES / "yury_circle.png").set_height(2.6)
        portrait.move_to(np.array([-3.4, -0.9, 0]))
        ring = Circle(radius=1.3 + 0.03, color=HIGHLIGHT, stroke_width=4).move_to(portrait)
        name = Text("Yury Kashnitsky", font=FONT, font_size=BODY_SIZE, color=TEXT)
        name.next_to(portrait, RIGHT, buff=0.5).shift(UP * 0.35)

        icon = TreeDiagram(
            tree_icon_spec(),
            labels=False,
            h_spacing=0.3,
            level_gap=0.6,
            leaf_colors={"0": CLASS_0, "1": CLASS_1},
            dot_radius=0.08,
        )
        icon.set_height(2.2).move_to(np.array([4.6, -0.9, 0]))

        with self.voiceover(text="I'm Yury, and let's dive into decision trees.") as tracker:
            first = max(tracker.duration * 0.35, 0.8)
            self.play(
                stickers.animate.scale(0.45).move_to(UP * 2.75),
                title.animate.scale(0.6).move_to(UP * 1.6),
                lecture.animate.scale(0.75).next_to(name, DOWN, buff=0.3, aligned_edge=LEFT),
                FadeIn(portrait, scale=0.9),
                Create(ring),
                Write(name),
                run_time=first,
            )
            rest = max(tracker.duration - first, 1.0)
            self.play(Indicate(topic, color=HIGHLIGHT, scale_factor=1.15), run_time=min(0.8, rest / 2))
            self.play(icon.create_animation(lag_ratio=0.4), run_time=max(rest - 0.8, 0.8))

        self.wait(FAST)
        self.play(
            FadeOut(Group(stickers, title, lecture, portrait, ring, name, icon)),
            run_time=FAST,
        )
