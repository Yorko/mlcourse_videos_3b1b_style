"""Scene 2: Twenty Questions (docs/STORYBOARD.md, rows 2.1-2.17)."""

import json
from pathlib import Path

from manim import (
    UL,
    Circle,
    FadeIn,
    FadeOut,
    FadeTransform,
    Flash,
    GrowFromEdge,
    Indicate,
    LaggedStart,
    MathTex,
    ORIGIN,
    Rectangle,
    ReplacementTransform,
    Text,
    ValueTracker,
    VGroup,
    Wiggle,
    Write,
    always_redraw,
)
from manim_voiceover import VoiceoverScene

from components.celebrity_grid import CelebrityGrid
from style import *
from voice import speech_service

DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "twenty_questions.json").read_text())

GRID_CENTER = LEFT * 2 + DOWN * 0.3
GRID_KW = dict(icon_height=0.45, spacing=0.6)
SECRET = (5, 1)  # the hidden pick: in the left half, so "a woman?" keeps it
JACKPOT = (2, 6)  # "Angelina Jolie": anyone but the secret
COUNTER_POS = RIGHT * 5 + UP * 3
BAR_X, BAR_BOTTOM, BAR_MAX_H, BAR_W = 4.5, -2.0, 4.0, 0.8  # centred on (4.5, 0) when full
QUESTION_Y = 3.0
FORMULA_POS = RIGHT * 4 + DOWN * 1.5
MINI_X, MINI_BOTTOM = (3.4, 5.4), -2.3
KEY_Y = -3.25  # storyboard says -3.0, which touches the grid


def label(text, size=BODY_SIZE, color=TEXT, **kwargs):
    return Text(text, font=FONT, font_size=size, color=color, **kwargs)


class TwentyQuestions(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())
        n = DATA["n_candidates"]

        grid = CelebrityGrid(8, 8, **GRID_KW).move_to(GRID_CENTER)
        secret, jackpot = grid.icon(*SECRET), grid.icon(*JACKPOT)

        # "questions: k", ticking through every value when animated
        asked = ValueTracker(0)
        counter_label = label("questions:", CAPTION_SIZE, TEXT_MUTED).move_to(COUNTER_POS)

        def counter_num():
            num = label(str(round(asked.get_value())), CAPTION_SIZE)
            # sit on the baseline of "u", not the bottom of the "q" descender
            return num.next_to(counter_label, RIGHT, buff=0.15).align_to(counter_label[1], DOWN)

        counter = VGroup(counter_label, always_redraw(counter_num))

        # the "k left" bar
        left = ValueTracker(n)

        def bar_rect():
            rect = Rectangle(width=BAR_W, height=max(BAR_MAX_H * left.get_value() / n, 0.03))
            rect.set_fill(TEXT_MUTED, 1).set_stroke(width=0)
            return rect.move_to([BAR_X, BAR_BOTTOM, 0], aligned_edge=DOWN)

        bar = always_redraw(bar_rect)
        bar_label = always_redraw(
            lambda: label(f"{round(left.get_value())} left", CAPTION_SIZE).next_to(bar, UP, buff=0.15)
        )

        # 2.1
        title = label("Twenty Questions", TITLE_SIZE).move_to(TITLE_POSITION)
        with self.voiceover(text="Start with a game you've probably played: Twenty Questions.") as tracker:
            self.play(
                LaggedStart(*[FadeIn(icon, scale=0.8) for icon in grid], lag_ratio=0.02),
                Write(title),
                run_time=tracker.duration,
            )

        # 2.2: the secret pick gets a faint glow that follows it around
        glow = Circle(radius=0.36).set_fill(HIGHLIGHT, 0.15).set_stroke(width=0).move_to(secret)
        glow.add_updater(lambda m: m.move_to(secret))
        with self.voiceover(
            text="I'm thinking of a celebrity, and you can only ask yes-or-no questions."
        ) as tracker:
            self.bring_to_back(glow)
            self.play(FadeIn(glow), run_time=min(1.5, tracker.duration))

        # 2.3
        qmark = label("?", 72, HIGHLIGHT).next_to(grid, UP, buff=0.25)
        with self.voiceover(text="What should you ask first?") as tracker:
            self.play(FadeOut(title), FadeIn(qmark, shift=DOWN * 0.2), run_time=min(1.0, tracker.duration))

        # 2.4
        question = label("Is it Angelina Jolie?").move_to([GRID_CENTER[0], QUESTION_Y, 0])
        with self.voiceover(text="You could go for the jackpot: \"Is it Angelina Jolie?\"") as tracker:
            self.play(FadeOut(qmark), run_time=FAST)
            self.play(Write(question), FadeIn(counter), run_time=tracker.duration * 0.6 - FAST)
            self.play(Indicate(jackpot, color=HIGHLIGHT), run_time=tracker.duration * 0.25)
            self.play(jackpot.animate.set_color(HIGHLIGHT), run_time=tracker.duration * 0.15)

        # 2.5
        with self.voiceover(text="If the answer is yes, wonderful.") as tracker:
            self.play(Flash(jackpot, color=HIGHLIGHT, flash_radius=0.4), run_time=min(1.0, tracker.duration))

        # 2.6
        answer = label("No", color=IMPURITY).next_to(question, RIGHT, buff=0.4)
        with self.voiceover(text="But almost always the answer is no.") as tracker:
            self.play(FadeIn(answer, shift=DOWN * 0.3), run_time=min(1.0, tracker.duration))

        # 2.7
        with self.voiceover(text="And when it's no, you've ruled out exactly one person.") as tracker:
            self.play(FadeIn(bar, bar_label), run_time=FAST)
            self.play(
                FadeOut(jackpot, scale=0.5),
                left.animate.set_value(DATA["jackpot_no_left"]),
                asked.animate.set_value(1),
                run_time=tracker.duration * 0.6,
            )

        # 2.8: freeze the bar so Wiggle isn't overwritten by its redraw
        with self.voiceover(text="You've learned almost nothing.") as tracker:
            bar.suspend_updating()
            self.play(Wiggle(bar, scale_value=1.05), run_time=min(1.2, tracker.duration))
            bar.resume_updating()
        self.play(FadeOut(question, answer), run_time=FAST)

        # 2.9: restore the jackpot icon, reset, ask the balanced question
        question = label("Is the celebrity a woman?").move_to(question)
        with self.voiceover(text="Now compare that with \"Is the celebrity a woman?\"") as tracker:
            jackpot.set_color(TEXT_MUTED)
            self.play(
                FadeIn(jackpot),
                left.animate.set_value(n),
                asked.animate.set_value(0),
                run_time=FAST,
            )
            self.play(Write(question), run_time=tracker.duration - FAST)

        # 2.10: the grid splits down the middle, one half ghosts out
        rows, cols = range(8), range(4)
        keep = grid.cells(rows, cols)
        drop = grid.cells(rows, range(4, 8))
        with self.voiceover(text="Whatever the answer, half the possibilities disappear.") as tracker:
            self.play(keep.animate.shift(LEFT * 0.3), drop.animate.shift(RIGHT * 0.3), run_time=tracker.duration * 0.4)
            self.play(
                drop.animate.set_opacity(0.15),
                left.animate.set_value(DATA["halvings"][1]),
                asked.animate.set_value(1),
                run_time=tracker.duration * 0.5,
            )

        # 2.11: keep halving, always along the longer side, keeping the secret's half
        icon = grid.icon(0, 0)
        gaps = (GRID_KW["spacing"] - icon.width, GRID_KW["spacing"] - icon.height)

        def regrid(group, n_rows, n_cols):
            return group.animate.arrange_in_grid(rows=n_rows, cols=n_cols, buff=gaps).move_to(GRID_CENTER)

        steps = DATA["halvings"][2:]
        with self.voiceover(
            text="Keep asking questions like that, and 64 candidates come down to one in just six questions."
        ) as tracker:
            step_time = tracker.duration / (len(steps) + 1)
            self.play(FadeOut(drop), regrid(keep, len(rows), len(cols)), run_time=step_time)
            for k, n_left in enumerate(steps, start=2):
                if len(rows) > len(cols):
                    mid = rows.start + len(rows) // 2
                    rows = next(h for h in (range(rows.start, mid), range(mid, rows.stop)) if SECRET[0] in h)
                else:
                    mid = cols.start + len(cols) // 2
                    cols = next(h for h in (range(cols.start, mid), range(mid, cols.stop)) if SECRET[1] in h)
                survivors = grid.cells(rows, cols)
                losers = VGroup(*[icon for icon in keep if icon not in survivors])
                keep = survivors
                assert len(keep) == n_left
                self.play(
                    FadeOut(losers, scale=0.6),
                    regrid(keep, len(rows), len(cols)),
                    left.animate.set_value(n_left),
                    asked.animate.set_value(k),
                    run_time=step_time,
                )
        self.play(secret.animate.set_color(HIGHLIGHT).scale(1.6), run_time=FAST)

        # 2.12: the formula takes over from the bar
        twenty = DATA["twenty"]
        formula = MathTex(
            rf"2^{{{twenty['questions']}}} \approx {twenty['candidates_approx']:,}".replace(",", "{,}"), color=TEXT
        ).move_to(FORMULA_POS)
        with self.voiceover(
            text="Twenty of them could pin down one person out of about a million, two to the twentieth."
        ) as tracker:
            self.play(FadeOut(bar, bar_label), run_time=FAST)
            self.play(
                Write(formula),
                asked.animate.set_value(twenty["questions"]),
                run_time=tracker.duration * 0.6,
            )

        # 2.13: back to the full grid
        full = CelebrityGrid(8, 8, **GRID_KW).move_to(GRID_CENTER)
        with self.voiceover(text="What made the second question good wasn't cleverness.") as tracker:
            glow.clear_updaters()
            self.play(
                FadeOut(glow, counter, question),
                FadeTransform(secret, full),
                run_time=min(1.5, tracker.duration),
            )
        grid = full

        # 2.14: how many candidates each question leaves after a "no"
        mini = VGroup()
        for x, (name, n_left, color) in zip(
            MINI_X,
            [("Jolie?", DATA["jackpot_no_left"], TEXT_MUTED), ("woman?", DATA["halvings"][1], GAIN)],
        ):
            rect = Rectangle(width=BAR_W, height=BAR_MAX_H * n_left / n).set_fill(color, 1).set_stroke(width=0)
            rect.move_to([x, MINI_BOTTOM, 0], aligned_edge=DOWN)
            name_text = label(name, CAPTION_SIZE, TEXT_MUTED).next_to(rect, DOWN, buff=0.2)
            value = label(f"{n_left} left", CAPTION_SIZE).next_to(rect, UP, buff=0.15)
            mini.add(VGroup(rect, name_text, value))
        with self.voiceover(text="You couldn't predict the answer, so either answer cut away a lot.") as tracker:
            self.play(FadeOut(formula), *[FadeIn(g[1]) for g in mini], run_time=FAST)
            self.play(
                LaggedStart(*[GrowFromEdge(g[0], DOWN) for g in mini], lag_ratio=0.4),
                LaggedStart(*[FadeIn(g[2]) for g in mini], lag_ratio=0.4),
                run_time=tracker.duration * 0.6,
            )

        # 2.15
        key = label("information = reduced uncertainty", t2c={"information": GAIN})
        key.move_to([GRID_CENTER[0], KEY_Y, 0])
        with self.voiceover(text="That's what information means here: reduced uncertainty.") as tracker:
            self.play(Write(key), run_time=tracker.duration * 0.8)
        self.wait(SLOW)

        # 2.16
        n_word = len("uncertainty")
        uncertainty = key[-n_word:]
        with self.voiceover(
            text="But for a computer to choose questions, \"uncertainty\" has to become a number."
        ) as tracker:
            self.play(FadeOut(mini), grid.animate.set_opacity(0.3), run_time=tracker.duration * 0.4)
            self.play(Indicate(uncertainty, color=HIGHLIGHT), run_time=tracker.duration * 0.4)

        # 2.17: the grid parks in the corner as the icon scene 3 picks up (3.10)
        measure = label("uncertainty = ?", t2c={"?": HIGHLIGHT}).move_to(ORIGIN)
        with self.voiceover(text="So how do you measure it?") as tracker:
            self.play(
                FadeOut(key[:-n_word]),
                ReplacementTransform(uncertainty, measure[:n_word]),
                FadeIn(measure[n_word:], shift=LEFT * 0.2),
                grid.animate.scale(0.25).to_corner(UL, buff=EDGE_BUFF),
                run_time=min(1.5, tracker.duration),
            )
        self.wait(NORMAL)
        self.play(FadeOut(measure), run_time=FAST)
